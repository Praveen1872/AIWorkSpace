import streamlit as st
from pptx import Presentation
import io, json, re, time
from google import genai

st.set_page_config(page_title="Slide Architect Pro", layout="wide")

st.markdown("""
<style>
    /* 1. Global App & Font Polish */
    .stApp { 
        background-color: #FAF8F7; 
        color: #1A1A1A; 
        font-family: 'Inter', sans-serif;
    }

    /* 2. Column Alignment Logic */
    [data-testid="column"] {
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 0px 5px !important; /* Tightens the gap between buttons */
    }

    /* 3. Button Design (Orange Professional Theme) */
    div.stButton > button { 
        border-radius: 12px; 
        background-color: white; 
        color: black;
        border: none;
        height: 3.2em; /* Slightly taller for better touch/click experience */
        width: 100%;
        font-weight: 600;
        letter-spacing: 0.3px;
        box-shadow: 0px 2px 4px rgba(0, 0, 0, 0.05); /* Subtle depth */
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }

    /* 4. Interactive Hover & Active States */
    div.stButton > button:hover {
        background-color: #FF4520;
        color: white !important;
        transform: translateY(-2px); /* Lift effect */
        box-shadow: 0px 6px 15px rgba(255, 96, 66, 0.3); /* Glowing shadow */
    }

    div.stButton > button:active {
        transform: translateY(0px); /* Pressed effect */
        box-shadow: 0px 2px 4px rgba(255, 96, 66, 0.2);
    }

    /* 5. Custom Horizontal Rule */
    hr {
        margin-top: 1rem;
        margin-bottom: 2rem;
        border: 0;
        border-top: 1px solid #E0DEDD;
    }
</style>
""", unsafe_allow_html=True)
is_logged_in = st.session_state.get('logged_in', False)
if not is_logged_in:
    st.switch_page("pages/login.py")


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
    .slide-stage {
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 40px;
        min-height: 450px;
        box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1);
        margin-bottom: 20px;
    }
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
        "Create academic slides. IMPORTANT: Every slide MUST have two columns of content. "
        "Return ONLY a valid JSON object. Do NOT use markdown bolding (**). "
        "Format: {'slides': [{'title': '...', 'left_col': ['point 1'], 'right_col': ['point 1']}], 'mentor_advice': '...'}"
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


col_stage, col_chat = st.columns([1.8, 1], gap="large")

with col_stage:
    st.title("🖼️ Slides Editor")
    
    if "ppt_data" in st.session_state and st.session_state.ppt_data:
        data = st.session_state.ppt_data
        if "current_slide_idx" not in st.session_state or st.session_state.current_slide_idx >= len(data):
            st.session_state.current_slide_idx = 0
            
        active_slide = data[st.session_state.current_slide_idx]
        title_display = clean_text(active_slide.get('title', 'Untitled Slide'))
        """
        # Column Logic
        l_pts = "".join([f'<div class="slide-point">• {clean_text(p)}</div>' for p in active_slide.get("left_col", [])])
        r_pts = "".join([f'<div class="slide-point">• {clean_text(p)}</div>' for p in active_slide.get("right_col", [])])

        st.markdown(f"""
            
        """, unsafe_allow_html=True)"""
        # 1. Combine all points into one list
        all_points = active_slide.get("left_col", []) + active_slide.get("right_col", [])

        # 2. Create the HTML for all points in a single stream
        points_html = "".join([f'<div class="slide-point">• {clean_text(p)}</div>' for p in all_points])

        # 3. Use a simplified single-container Markdown
        st.markdown(f"""
             <div class="slide-stage">
             
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
            # PPTX Export Logic for 2 Columns
            prs = Presentation()
            for s in st.session_state.ppt_data:
                
                slide = prs.slides.add_slide(prs.slide_layouts[3]) 
                slide.shapes.title.text = clean_text(s.get('title', ''))
                
                slide.placeholders[1].text = "\n".join([clean_text(p) for p in s.get('left_col', [])])
                slide.placeholders[2].text = "\n".join([clean_text(p) for p in s.get('right_col', [])])
            
            buf = io.BytesIO()
            prs.save(buf)
            st.download_button("📥 Download PPTX", buf.getvalue(), "presentation.pptx", use_container_width=True)
    else:
        st.info("👋 Ask the Assistant to generate a 2-column deck!")

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

    if user_in := st.chat_input("Ex: 'Create 3 slides on the history of space flight'"):
        st.session_state.chat_history.append({"role": "user", "content": user_in})
        with st.spinner("Architecting dual columns..."):
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