import streamlit as st
from google import genai
from docx import Document
from io import BytesIO
import re


is_logged_in = st.session_state.get('logged_in', False)
if not is_logged_in:
    st.switch_page("pages/login.py")


h_cols = st.columns([2, 0.7, 0.7, 0.7, 0.9, 1.8, 1], vertical_alignment="center")
with h_cols[0]: 
    st.markdown("<h3 style='margin:0;'>🚀 AI Mentor</h3>", unsafe_allow_html=True)

with h_cols[1]: 
    if st.button("PPT 🖼️", use_container_width=True): st.switch_page("pages/ppt_editor.py")
with h_cols[2]: 
    if st.button("Word 📝", use_container_width=True,type="primary"): st.switch_page("pages/word_editor.py")
with h_cols[3]: 
    if st.button("Notes 📓", use_container_width=True): st.switch_page("pages/note.py")
with h_cols[4]: 
    if st.button("Summarizer 📝", use_container_width=True): st.switch_page("pages/Summarizer.py")
with h_cols[6]:
    if st.button("Logout 🚪", use_container_width=True):
        st.session_state.logged_in = False
        st.switch_page("AIMentor.py")

st.markdown("<hr style='margin:0 0 20px 0; border-top: 1px solid #E0DEDD;'>", unsafe_allow_html=True)


def clean_text(text):
    return re.sub(r'\**\*|#+', '', text).strip()

def create_docx(content):
    doc = Document()
    
    for line in content.split('\n'):
        line = line.strip()
        if not line: continue
        
        if line.startswith('---'):
            doc.add_page_break()
            continue
        if line.startswith('#'):
            level = 0
            if line.startswith('###'): level = 2
            elif line.startswith('##'): level = 1
            doc.add_heading(clean_text(line), level=level)
        else:
            is_bullet = line.startswith('* ') or line.startswith('- ')
            working_text = line.lstrip('* -').strip() if is_bullet else line
            p = doc.add_paragraph(style='List Bullet' if is_bullet else None)
            
            parts = re.split(r'(\*\*.*?\*\*)', working_text)
            for part in parts:
                if part.startswith('**') and part.endswith('**'):
                    clean_part = part.replace('**', '')
                    p.add_run(clean_part).bold = True
                else:
                    p.add_run(part)
    
    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer


try:
    client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
except Exception as e:
    st.error(f"Gemini Initialization Failed: {e}")

st.title("📄 Report Assistant")
st.write("Refine and export your research into polished Microsoft Word documents.")

topic = st.text_input("Report Topic", placeholder="e.g., The impact of renewable energy on global economy")

if st.button("Generate Report ", use_container_width=True):
    if topic:
        with st.spinner("AI Mentor is drafting your report..."):
            try:
                prompt = f"Write a comprehensive formal academic report about: {topic}. Use ## for section headings."
                response = client.models.generate_content(
                    model="gemini-2.5-flash-lite",
                    contents=[prompt],
                    config=genai.types.GenerateContentConfig(
                        system_instruction="You are a professional academic mentor. Write formal, well-structured reports. Do not use markdown bolding (**) in titles or headers."
                    )
                )
                st.session_state.report_text = response.text
                st.success("Draft completed!")
            except Exception as e:
                st.error(f"Generation failed: {e}")
    else:
        st.warning("Please enter a topic to begin.")


if "report_text" in st.session_state:
    final_text = st.text_area("Review & Edit Draft", value=st.session_state.report_text, height=500)
    word_file = create_docx(final_text)
    safe_filename = clean_text(topic).replace(' ', '_')[:20]
    
    st.download_button(
        label="📥 Download as Microsoft Word (.docx)",
        data=word_file,
        file_name=f"Report_{safe_filename}.docx",
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        use_container_width=True
    )
