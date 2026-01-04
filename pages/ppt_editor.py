import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
from pptx import Presentation
import io, json, re
from google import genai
st.set_page_config(page_title="Slide Architect Pro", layout="wide")
st.markdown("""
<style>
    .stApp { 
        background-color: #FAF8F7; 
        color: #1A1A1A; 
        font-family: 'Inter', sans-serif;
    }

    .slide-stage {
        width: 700px;
        height: 500px;
        background-color: #FFFFFF;
        margin: 20px auto;
        padding: 50px;
        border-radius: 8px;
        border: 1px solid #E0DEDD;
        box-shadow: 0px 10px 30px rgba(0, 0, 0, 0.08);
        display: flex;
        flex-direction: column;
        overflow: hidden;
        position: relative;
    }
.slide-stage {
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 40px;
       
        box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1);
        margin-bottom: 20px;
    }
    .slide-title {
        font-size: 42px;
        font-weight: 800;
        color: #FF4520;
        margin-bottom: 25px;
        line-height: 1.2;
    }

    .slide-content {
        font-size: 26px;
        line-height: 1.6;
        color: #2D2D2D;
        flex-grow: 1;
    }

    .slide-point {
        margin-bottom: 20px;
        padding-left: 10px;
    }

    div.stButton > button { 
        border-radius: 12px; 
        background-color: white; 
        color: black;
        border: 1px solid #E0DEDD;
        height: 3.2em;
        width: 100%;
        font-weight: 600;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }

    div.stButton > button:hover {
        background-color: #FF4520;
        color: white !important;
        transform: translateY(-2px);
        box-shadow: 0px 6px 15px rgba(255, 69, 32, 0.3);
        border-color: #FF4520;
    }

    [data-testid="column"] {
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 0px 5px !important;
    }
</style>
""", unsafe_allow_html=True)
is_logged_in = st.session_state.get("logged_in", False)
if not is_logged_in:
    st.switch_page("pages/login.py")

user_uid = st.session_state.get("user_uid")

def initialize_firebase():
    if not firebase_admin._apps:
        creds = dict(st.secrets["firebase_credentials"])
        creds["private_key"] = creds["private_key"].replace("\\n", "\n")
        cred = credentials.Certificate(creds)
        firebase_admin.initialize_app(cred)

initialize_firebase()
firestore_db = firestore.client()
ppt_col = (
    firestore_db
    .collection("users")
    .document(user_uid)
    .collection("documents")
    .document("ppt")
    .collection("items")
)

h_cols = st.columns([2, 0.9, 0.9, 0.9, 1.5, 0.8, 1], vertical_alignment="center")
with h_cols[0]: 
    st.markdown("<h3 style='margin:0;'>🚀 AI Mentor</h3>", unsafe_allow_html=True)

with h_cols[1]: 
    if st.button("PPT 🖼️", use_container_width=True,type="primary"): st.switch_page("pages/ppt_editor.py")
with h_cols[2]: 
    if st.button("Word 📝", use_container_width=True): st.switch_page("pages/word_editor.py")
with h_cols[3]:
    
    if st.button("Notes 📓", use_container_width=True): st.switch_page("pages/note.py")
with h_cols[4]: 
    
    if st.button("Summarizer 📝", use_container_width=True): st.switch_page("pages/Summarizer.py")

with h_cols[6]:
    if st.button("Logout 🚪", use_container_width=True):
        st.session_state.logged_in = False
        st.switch_page("AIMentor.py")


st.markdown("<hr style='margin:0 0 20px 0; border-top: 1px solid #E0DEDD;'>", unsafe_allow_html=True)

st.markdown("""
    <style>
    
    .slide-title { color: #1e293b; font-size: 32px; font-weight: 800; margin-bottom: 25px; border-bottom: 3px solid #3b82f6; width: 100%; padding-bottom: 10px; }
    .col-container { display: flex; gap: 30px; }
    .content-col { flex: 1; }
    .slide-point { font-size: 18px; margin-bottom: 12px; color: #475569; line-height: 1.6; }
    .mentor-box { background-color: #f0fdf4; border-left: 5px solid #22c55e; padding: 15px; border-radius: 5px; margin-top: 10px; }
    </style>
""", unsafe_allow_html=True)

def clean_text(text):
    return re.sub(r'\*\*|#+', '', str(text)).strip()


API_KEY = st.secrets["GEMINI_API_KEY"]
client = genai.Client(api_key=API_KEY)


def call_ai_architect(prompt, current_data=None, active_idx=None):
    
    system_instr = (
    "You are an Academic Slide Architect. Create as many slides as necessary to cover the topic "
    "comprehensively. IMPORTANT: Each slide MUST have a MAXIMUM of 4 bullet points. "
    "If the content requires more than 7 points, increment to a new slide with a specific sub-title. "
    "Return ONLY a valid JSON object. Do NOT use markdown bolding (**). "
    "Format: {'slides': [{'title': '...', 'points': ['point 1', 'point 2']}], 'mentor_advice': '...'}"
)
    if current_data:
        focus = f"Slide {active_idx+1}" if active_idx is not None else "the whole deck"
        system_instr = f"Context: {json.dumps(current_data)}. Update {focus} based on: {prompt}. " + system_instr

    model_list = ["gemini-2.5-flash-lite"]
    
    for model_name in model_list:
        try:
            response = client.models.generate_content(model=model_name, contents=prompt, config={"system_instruction": system_instr})
            match = re.search(r'\{.*\}', response.text, re.DOTALL)
            if match:
                res_json = json.loads(match.group(0))
                return res_json.get('slides'), res_json.get('mentor_advice'), model_name
        except: continue
    return None, None, None

def store_ppt_chunks(ppt_doc_ref, slides):
    chunks_col = ppt_doc_ref.collection("chunks")
    for s in slides:
        text = s.get("title", "") + " " + " ".join(s.get("points", []))
        chunks_col.add({
            "text": text.strip(),
            "embedding": []   # placeholder only
        })
def load_user_ppts():
    docs = ppt_col.order_by("created_at", direction=firestore.Query.DESCENDING).stream()
    return [{"id": d.id, **d.to_dict()} for d in docs]
col_stage, col_chat = st.columns([1.8, 1], gap="large")

with st.sidebar:
    st.subheader("📂 PPT History")

    ppt_docs = load_user_ppts()
    if ppt_docs:
        title_map = {p["title"]: p["id"] for p in ppt_docs}
        selected = st.selectbox("Past PPTs", title_map.keys())

        if st.button("📂 Load PPT"):
            st.session_state.active_ppt_id = title_map[selected]
            st.rerun()

    if st.button("🗑️ Clear All PPTs"):
        for doc in ppt_col.stream():
            for c in doc.reference.collection("chunks").stream():
                c.reference.delete()
            doc.reference.delete()
        st.session_state.pop("ppt_data", None)
        st.rerun()
if "active_ppt_id" in st.session_state:
    ppt_doc = ppt_col.document(st.session_state.active_ppt_id)
    chunks = ppt_doc.collection("chunks").stream()
    slides = []
    for c in chunks:
        slides.append({"title": "", "points": [c.to_dict()["text"]]})
    st.session_state.ppt_data = slides
with col_stage:
    st.title("🖼️ Slides Editor")
    
    if "ppt_data" in st.session_state and st.session_state.ppt_data:
        data = st.session_state.ppt_data
        if "current_slide_idx" not in st.session_state or st.session_state.current_slide_idx >= len(data):
            st.session_state.current_slide_idx = 0
            
        active_slide = data[st.session_state.current_slide_idx]
        title_display = clean_text(active_slide.get('title', 'Untitled Slide'))
        active_points = active_slide.get("points", [])[:7] # Strict 7-point limit
        points_html = "".join([f'<div class="slide-point">• {clean_text(p)}</div>' for p in active_points])

        st.markdown(f"""
     <div class="slide-stage">
        <div class="slide-title">{title_display}</div>
        <div class="content-single">
            {points_html if points_html else '<i>No content for this slide.</i>'}
        </div>
    </div>
""", unsafe_allow_html=True)

        
        st.write("### 🎞️ Slide Navigator")
        nav_cols = st.columns(min(len(data), 10))
        for i in range(len(data)):
            with nav_cols[i % 10]:
                is_active = (i == st.session_state.current_slide_idx)
                if st.button(f"{i+1}", key=f"nav_{i}", type="primary" if is_active else "secondary"):
                    st.session_state.current_slide_idx = i
                    st.rerun()

        st.divider()
        c1, c2 = st.columns(2)
        with c1:
            if st.button("🗑️ Delete Slide", use_container_width=True):
                st.session_state.ppt_data.pop(st.session_state.current_slide_idx)
                st.rerun()
        with c2:
           prs = Presentation()
           prs.slide_width = 9144000 
           prs.slide_height = 6858000
           for s in st.session_state.ppt_data:
                slide = prs.slides.add_slide(prs.slide_layouts[1]) 
                slide.shapes.title.text = clean_text(s.get('title', ''))
    
                 # Export the single points list (limited to 7)
                slide_points = s.get('points', [])[:7]
                combined_text = "\n".join([clean_text(p) for p in slide_points])
    
                if len(slide.placeholders) > 1:
                    slide.placeholders[1].text = combined_text
                   
           buf = io.BytesIO()
           prs.save(buf)
           st.download_button(
                label="📥 Download PPTX",
                data=buf.getvalue(),
                file_name="presentation.pptx",
                mime="application/vnd.openxmlformats-officedocument.presentationml.presentation",
                use_container_width=True
)
          
    else:
        st.info("👋 Ask the Assistant to generate !")

with col_chat:
    st.title("AI Assistant")
    edit_mode = st.toggle("🎯 Edit ONLY Active Slide", value=False)
    
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    chat_box = st.container(height=450)
    for m in st.session_state.chat_history:
        with chat_box.chat_message(m["role"]):
            st.write(m["content"])
            if "advice" in m:
                st.markdown(f'<div class="mentor-box">💡 {m["advice"]}</div>', unsafe_allow_html=True)
    ppt_prompt = st.chat_input("Enter PPT topic")


    if user_in := ppt_prompt:
        st.session_state.chat_history.append({"role": "user", "content": user_in})
        with st.spinner("Architecting ..."):
            idx = st.session_state.current_slide_idx if (edit_mode and "ppt_data" in st.session_state) else None
            new_slides, advice, model_name = call_ai_architect(user_in, st.session_state.get("ppt_data"), idx)
            if new_slides:
                st.session_state.ppt_data = new_slides
                st.session_state.chat_history.append({
                    "role": "assistant", 
                    "content": f"Done", 
                    "advice": advice
                })
                st.rerun()
