import streamlit as st
import io, re
from google import genai
import PyPDF2
from docx import Document
from pptx import Presentation

# -------------------- Page Config --------------------
st.set_page_config(
    page_title="Summarizer Lab",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# -------------------- Styling --------------------
st.markdown("""
<style>
.stApp {
    background-color: #FAF8F7;
    color: #1A1A1A;
    font-family: 'Inter', sans-serif;
}
div.stButton > button {
    border-radius: 12px;
    background-color: white;
    color: black;
    border: none;
    height: 3.2em;
    width: 100%;
    font-weight: 600;
    transition: all 0.3s ease;
}
div.stButton > button:hover {
    background-color: #FF4520;
    color: white !important;
}
hr {
    border-top: 1px solid #E0DEDD;
}
</style>
""", unsafe_allow_html=True)

# -------------------- Session State Init --------------------
if "active_context" not in st.session_state:
    st.session_state.active_context = ""

if "active_filename" not in st.session_state:
    st.session_state.active_filename = ""

if "summary_output" not in st.session_state:
    st.session_state.summary_output = ""

if "assistant_chat" not in st.session_state:
    st.session_state.assistant_chat = []

# -------------------- AI Client --------------------
client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

# -------------------- Helpers --------------------
def extract_text_from_any(uploaded_file):
    name = uploaded_file.name.lower()
    text = ""

    if name.endswith(".pdf"):
        reader = PyPDF2.PdfReader(uploaded_file)
        text = "\n".join([p.extract_text() or "" for p in reader.pages])

    elif name.endswith(".docx"):
        doc = Document(uploaded_file)
        text = "\n".join([p.text for p in doc.paragraphs])

    elif name.endswith(".pptx"):
        prs = Presentation(uploaded_file)
        for slide in prs.slides:
            for shape in slide.shapes:
                if hasattr(shape, "text"):
                    text += shape.text + " "

    return text.strip()

def call_research_ai(prompt, context):
    system = (
        "You are an academic research assistant. "
        "Answer clearly and concisely based ONLY on the provided context."
    )

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config={
            "system_instruction": f"{system}\n\nContext:\n{context[:18000]}"
        }
    )
    return response.text

# -------------------- Layout --------------------
col_left, col_right = st.columns([2, 1], gap="large")

# ==================== LEFT: SUMMARIZER ====================
with col_left:
    st.title("📑 Summarizer Lab")

    # Attach file
    with st.container(border=True):
        file = st.file_uploader(
            "📎 Attach PDF / DOCX / PPTX",
            type=["pdf", "docx", "pptx"]
        )

        if file and st.button("📥 Attach", use_container_width=True):
            with st.spinner("Reading document..."):
                content = extract_text_from_any(file)
                if content:
                    st.session_state.active_context = content
                    st.session_state.active_filename = file.name
                    st.session_state.summary_output = ""
                    st.success(f"Attached: {file.name}")

    # Generate summary
    if st.session_state.active_context:
        if st.button("✨ Generate Summary", type="primary", use_container_width=True):
            with st.spinner("Generating summary..."):
                st.session_state.summary_output = call_research_ai(
                    "Provide a structured summary with Abstract, Key Findings, and Technical Implications.",
                    st.session_state.active_context
                )

    # Summary output (ONLY HERE)
    if st.session_state.summary_output:
        with st.container(border=True):
            st.markdown("### 📄 Summary")
            st.markdown(st.session_state.summary_output)

# ==================== RIGHT: AI ASSISTANT ====================
with col_right:
    st.title("🤖 AI Assistant")
    st.caption("Instant doubt clarification from the attached document")

    if not st.session_state.active_context:
        st.info("📎 Attach a document from the left panel to begin.")
    else:
        chat_box = st.container(height=420)

        with chat_box:
            for msg in st.session_state.assistant_chat:
                with st.chat_message(msg["role"]):
                    st.markdown(msg["content"])

        question = st.chat_input("Ask a question about this document")

        if question:
            st.session_state.assistant_chat.append({
                "role": "user",
                "content": question
            })

            with st.spinner("Thinking..."):
                answer = call_research_ai(
                    question,
                    st.session_state.active_context
                )

            st.session_state.assistant_chat.append({
                "role": "assistant",
                "content": answer
            })

            st.rerun()
