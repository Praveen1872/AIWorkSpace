import streamlit as st
import io, re, os
from google import genai
import PyPDF2
from docx import Document
from pptx import Presentation
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
        width: 139%;
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

st.set_page_config(page_title="Summarizer Lab", layout="wide", initial_sidebar_state="collapsed")

is_logged_in = st.session_state.get('logged_in', False)
if not is_logged_in:
    st.switch_page("pages/login.py")


h_cols = st.columns([2, 0.9, 0.9, 0.9, 1.5, 0.8, 1], vertical_alignment="center")
with h_cols[0]: 
    st.markdown("<h3 style='margin:0;'>🚀 AI Mentor</h3>", unsafe_allow_html=True)

with h_cols[1]: 
    if st.button("PPT 🖼️", use_container_width=True): st.switch_page("pages/ppt_editor.py")
with h_cols[2]: 
    if st.button("Word 📝", use_container_width=True): st.switch_page("pages/word_editor.py")
with h_cols[3]: 
    
    if st.button("Notes 📓", use_container_width=True): st.switch_page("pages/note.py")
with h_cols[4]: 
    
    if st.button("Summarizer📝", use_container_width=True): st.switch_page("pages/Summarizer.py")

with h_cols[6]:
    if st.button("Logout 🚪", use_container_width=True):
        st.session_state.logged_in = False
        st.switch_page("AIMentor.py")

st.markdown("<hr style='margin:0 0 20px 0; border-top: 1px solid #E0DEDD;'>", unsafe_allow_html=True)

client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

def extract_text_from_any(uploaded_file):
    fname = uploaded_file.name.lower()
    text = ""
    try:
        if fname.endswith('.pdf'):
            reader = PyPDF2.PdfReader(uploaded_file)
            text = "\n".join([page.extract_text() or "" for page in reader.pages])
        elif fname.endswith('.docx'):
            doc = Document(uploaded_file)
            text = "\n".join([para.text for para in doc.paragraphs])
        elif fname.endswith('.pptx'):
            prs = Presentation(uploaded_file)
            for slide in prs.slides:
                for shape in slide.shapes:
                    if hasattr(shape, "text"): text += shape.text + " "
        return text.strip()
    except Exception as e:
        st.error(f"Error reading {fname}: {e}")
        return None

def call_research_ai(user_query, context_text=None, is_summary=False):
    system_instr = "You are an Academic Research Mentor."
    if context_text:
        system_instr += f" Context: {context_text[:18000]}."
    if is_summary:
        user_query = "Provide a comprehensive summary: Abstract, Key Findings, and Technical Implications."
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash-lite", 
            contents=user_query, 
            config={"system_instruction": system_instr}
        )
        return response.text
    except Exception as e: return f"AI Error: {e}"

if "research_chat_history" not in st.session_state: st.session_state.research_chat_history = []
if "active_context" not in st.session_state: st.session_state.active_context = ""
if "active_filename" not in st.session_state: st.session_state.active_filename = ""


col_left, col_right = st.columns([2, 1], gap="large")

with col_left:
    st.title("📑 Summarizer Lab")
    chat_container = st.container(height=500)
    
    with chat_container:
        if not st.session_state.research_chat_history:
            st.info("👋 Upload a document on the right to start your research session.")
        for message in st.session_state.research_chat_history:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    if user_input := st.chat_input("Ask about the document..."):
        st.session_state.research_chat_history.append({"role": "user", "content": user_input})
        with chat_container:
            with st.chat_message("user"): st.markdown(user_input)
            with st.chat_message("assistant"):
                with st.spinner("Consulting source..."):
                    ai_response = call_research_ai(user_input, st.session_state.active_context)
                    st.markdown(ai_response)
                    st.session_state.research_chat_history.append({"role": "assistant", "content": ai_response})
                    st.rerun()

with col_right:
    st.markdown("### 📎 Research Sources")
    with st.container(border=True):
        att_file = st.file_uploader("Upload PDF, DOCX, or PPTX", type=["pdf", "docx", "pptx"])
        
        if att_file:
            if st.button("📥 ready", use_container_width=True):
                with st.spinner("Analyzing..."):
                    content = extract_text_from_any(att_file)
                    if content:
                        st.session_state.active_context = content
                        st.session_state.active_filename = att_file.name
                        st.success(f"Ready: {att_file.name}")

    if st.session_state.active_context:
        st.write(f"📄 **Active:** {st.session_state.active_filename}")
        if st.button("✨ Summarize", type="primary", use_container_width=True):
            with st.spinner("Synthesizing..."):
                summary = call_research_ai("Summarize", st.session_state.active_context, is_summary=True)
                st.session_state.research_chat_history.append({
                    "role": "assistant", 
                    "content": f"### 📄 Summary of {st.session_state.active_filename}\n\n{summary}"
                })
                st.rerun()
        
        if st.button("🗑️ Clear Workspace", use_container_width=True):
            st.session_state.active_context = ""
            st.session_state.active_filename = ""
            st.session_state.research_chat_history = []
            st.rerun()