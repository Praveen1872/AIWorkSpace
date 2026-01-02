import streamlit as st
from pptx import Presentation
import io, json, re, time
from google import genai

st.set_page_config(page_title="Slide Architect Pro", layout="wide")

# --- 1. CLEANED CSS (Widescreen 16:9 Architecture) ---
st.markdown("""
<style>
    .stApp { 
        background-color: #FAF8F7; 
        color: #1A1A1A; 
        font-family: 'Inter', sans-serif;
    }

    .slide-stage {
        width: 960px;  /* 10 inches @ 96 DPI */
        height: 720px; /* 7.5 inches @ 96 DPI */
        background-color: #FFFFFF;
        margin: 20px auto;
        padding: 60px;
        border-radius: 8px;
        border: 1px solid #E0DEDD;
        box-shadow: 0px 10px 30px rgba(0, 0, 0, 0.08);
        display: flex;
        flex-direction: column;
        overflow: hidden;
        position: relative;
    }

    .slide-title {
        font-size: 42px;
        font-weight: 800;
        color: #FF4520;
        margin-bottom: 30px;
        line-height: 1.2;
        border-bottom: 2px solid #F3F4F6;
        padding-bottom: 15px;
    }

    .content-single {
        font-size: 26px;
        line-height: 1.6;
        color: #2D2D2D;
        flex-grow: 1;
    }

    .slide-point {
        margin-bottom: 20px;
        padding-left: 10px;
        list-style-type: none;
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

    .mentor-box { 
        background-color: #f0fdf4; 
        border-left: 5px solid #22c55e; 
        padding: 15px; 
        border-radius: 5px; 
        margin-top: 10px; 
        font-size: 14px;
    }
</style>
""", unsafe_allow_html=True)

# --- 2. AUTHENTICATION CHECK ---
is_logged_in = st.session_state.get('logged_in', False)
if not is_logged_in:
    st.switch_page("pages/login.py")

# --- 3. TOP NAVIGATION BAR ---
h_cols = st.columns([2, 0.9, 0.9, 0.9, 1.5, 0.8, 1], vertical_alignment="center")
with h_cols[0]: 
    st.markdown("<h3 style='margin:0;'>🚀 AI Mentor</h3>", unsafe_allow_html=True)
with h_cols[1]: 
    if st.button("PPT 🖼️", use_container_width=True, type="primary"): st.switch_page("pages/ppt_editor.py")
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

# --- 4. UTILITIES & API ---
def clean_text(text):
    return re.sub(r'\*\*|#+', '', str(text)).strip()

API_KEY = st.secrets["GEMINI_API_KEY"]
client = genai.Client(api_key=API_KEY)

def call_ai_architect(prompt, current_data=None, active_idx=None):
    system_instr = (
        "Create academic slides. IMPORTANT: Return ONLY a valid JSON object. "
        "Do NOT use markdown bolding (**). Structure content for a professional single-column view. "
        "Format: {'slides': [{'title': '...', 'left_col': ['point 1'], 'right_col': ['point 2']}], 'mentor_advice': '...'}"
    )
    if current_data:
        focus = f"Slide {active_idx+1}" if active_idx is not None else "the whole deck"
        system_instr = f"Context: {json.dumps(current_data)}. Update {focus} based on: {prompt}. " + system_instr

    model_list = ["gemini-2.0-flash-lite", "gemini-2.0-flash"]
    
    for model_name in model_list:
        try:
            response = client.models.generate_content(model=model_name, contents=prompt, config={"system_instruction": system_instr})
            match = re.search(r'\{.*\}', response.text, re.DOTALL)
            if match:
                res_json = json.loads(match.group(0))
                return res_json.get('slides'), res_json.get('mentor_advice'), model_name
        except: continue
    return None, None, None

# --- 5. MAIN INTERFACE ---
col_stage, col_chat = st.columns([1.8, 1], gap="large")

with col_stage:
    st.title("🖼️ Slides Editor")
    
    if "ppt_data" in st.session_state and st.session_state.ppt_data:
        data = st.session_state.ppt_data
        if "current_slide_idx" not in st.session_state or st.session_state.current_slide_idx >= len(data):
            st.session_state.current_slide_idx = 0
            
        active_slide = data[st.session_state.current_slide_idx]
        title_display = clean_text(active_slide.get('title', 'Untitled Slide'))
       
        # MERGE COLUMNS FOR SINGLE DISPLAY
        all_points = active_slide.get("left_col", []) + active_slide.get("right_col", [])
        points_html = "".join([f'<div class="slide-point">• {clean_text(p)}</div>' for p in all_points])

        # RENDER 10x7.5 STAGE
        st.markdown(f"""
             <div class="slide-stage">
                <div class="slide-title">{title_display}</div>
                <div class="content-single">
                    {points_html if points_html else '<i>Add content to this slide...</i>'}
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
            # EXPORT LOGIC
            prs = Presentation()
            # Set 16:9 Aspect Ratio in PPTX
            prs.slide_width = 9144000  # 10 inches
            prs.slide_height = 6858000 # 7.5 inches
            
            for s in st.session_state.ppt_data:
                slide = prs.slides.add_slide(prs.slide_layouts[1]) # Bullet layout
                slide.shapes.title.text = clean_text(s.get('title', ''))
                
                # Combine points for the single text frame in PPTX
                full_content = "\n".join([clean_text(p) for p in (s.get('left_col', []) + s.get('right_col', []))])
                slide.placeholders[1].text = full_content
            
            buf = io.BytesIO()
            prs.save(buf)
            st.download_button("📥 Download PPTX", buf.getvalue(), "presentation.pptx", use_container_width=True)
    else:
        st.info("👋 Ask the Assistant to generate your slide deck!")

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

    if user_in := st.chat_input("Ex: 'Create 3 slides on Quantum Computing'"):
        st.session_state.chat_history.append({"role": "user", "content": user_in})
        with st.spinner("Designing your slides..."):
            idx = st.session_state.current_slide_idx if (edit_mode and "ppt_data" in st.session_state) else None
            new_slides, advice, model_name = call_ai_architect(user_in, st.session_state.get("ppt_data"), idx)
            if new_slides:
                if edit_mode and idx is not None:
                    st.session_state.ppt_data[idx] = new_slides[0]
                else:
                    st.session_state.ppt_data = new_slides
                
                st.session_state.chat_history.append({
                    "role": "assistant", 
                    "content": f"Slides updated successfully.", 
                    "advice": advice
                })
                st.rerun()