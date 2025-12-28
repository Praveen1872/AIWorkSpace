import streamlit as st
from fpdf import FPDF
import datetime

st.set_page_config(
    page_title="Make Notes",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- LOGIN CHECK ---
if not st.session_state.get("logged_in", False):
    st.switch_page("pages/login.py")

# --- HEADER BUTTONS ---
h_cols = st.columns([2, 0.9, 0.9, 0.9, 1.5, 2.0, 1], vertical_alignment="center")

with h_cols[0]:
    st.markdown("<h3 style='margin:0;'>🚀 AI Mentor</h3>", unsafe_allow_html=True)

with h_cols[1]:
    if st.button("PPT 🖼️", use_container_width=True):
        st.switch_page("pages/ppt_editor.py")

with h_cols[2]:
    if st.button("Word 📝", use_container_width=True):
        st.switch_page("pages/word_editor.py")

with h_cols[3]:
    if st.button("Notes 📓", use_container_width=True,type="primary" ):
        st.switch_page("pages/note.py")

with h_cols[4]:
    if st.button("Summarizer 📝", use_container_width=True):
        st.switch_page("pages/Summarizer.py")

with h_cols[6]:
    if st.button("Logout 🚪", use_container_width=True):
        st.session_state.logged_in = False
        st.switch_page("app.py")

st.markdown(
    "<hr style='margin:0 0 20px 0; border-top: 1px solid #E0DEDD;'>",
    unsafe_allow_html=True
)

# --- STYLING ---
st.markdown("""
<style>
div[data-baseweb="input"],
div[data-baseweb="textarea"] {
    background: transparent !important;
    box-shadow: none !important;
    border: none !important;
}

input, textarea {
    border: none !important;
    box-shadow: none !important;
}

input {
    border-bottom: 1px solid #ddd !important;
    border-radius: 0 !important;
}
</style>
""", unsafe_allow_html=True)

# --- MAIN CONTENT ---
st.title("📓 Research Notebook")
st.write("Capture your personal thoughts, draft ideas, or academic notes.")

col1, col2 = st.columns([2, 1])

with col1:
    note_title = st.text_input(
        "Note Title",
        placeholder="e.g., Deep Learning – CNN Notes"
    )

    st.text_area(
        "Your Academic Notes",
        height=450,
        placeholder="Start typing your thoughts here...",
        key="note_editor"
    )

with col2:
    st.info(
        "💡 **Mentor Tip:** Writing concepts in your own words improves understanding and long-term retention."
    )

    st.subheader("Export Options")
    file_format = st.selectbox(
        "Choose Format",
        ["PDF Document (.pdf)", "Text File (.txt)"]
    )

    if st.button("🚀 Export Notebook Entry", use_container_width=True):
        content = st.session_state.get("note_editor", "")

        if content.strip():
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

            if "PDF" in file_format:
                pdf = FPDF()
                pdf.add_page()
                pdf.set_font("Arial", "B", 18)
                pdf.cell(0, 15, note_title or "Untitled Note", ln=True)
                pdf.set_font("Arial", size=10)
                pdf.cell(0, 10, f"Date: {timestamp}", ln=True)
                pdf.ln(10)
                pdf.set_font("Arial", size=12)

                clean_text = content.encode("latin-1", "ignore").decode("latin-1")
                pdf.multi_cell(0, 10, clean_text)

                pdf_bytes = pdf.output(dest="S").encode("latin-1")

                st.download_button(
                    "📥 Download PDF",
                    pdf_bytes,
                    file_name="notes.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
            else:
                txt_data = f"{note_title}\nDate: {timestamp}\n\n{content}"
                st.download_button(
                    "📥 Download Text File",
                    txt_data,
                    file_name="notes.txt",
                    mime="text/plain",
                    use_container_width=True
                )
        else:
            st.warning("Please write some notes before exporting.")

    if st.button("🗑️ Clear Page", use_container_width=True):
        st.session_state["note_editor"] = ""
        st.rerun()

st.divider()
st.caption("Notes are stored only for this session. Download to save permanently.")
