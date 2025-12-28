import streamlit as st
from fpdf import FPDF
import datetime
import os

st.set_page_config(page_title="Make Notes", layout="wide", initial_sidebar_state="collapsed")

# --- LOGIN CHECK ---
if not st.session_state.get('logged_in', False):
    st.switch_page("pages/login.py")

# --- APPEND SUMMARY CALLBACK ---
def append_summary_callback(summary_text):
    current_val = st.session_state.get("note_editor", "")
    new_val = current_val + f"\n\n--- Imported Summary ({datetime.datetime.now().strftime('%H:%M')}) ---\n{summary_text}"
    st.session_state["note_editor"] = new_val

# --- HEADER BUTTONS ---
h_cols = st.columns([2, 0.7, 0.7, 0.7, 0.9, 1.8, 1], vertical_alignment="center")
with h_cols[0]: 
    st.markdown("<h3 style='margin:0;'>🚀 AI Mentor</h3>", unsafe_allow_html=True)
with h_cols[1]: 
    if st.button("PPT 🖼️", use_container_width=True): st.switch_page("pages/ppt_editor.py")
with h_cols[2]: 
    if st.button("Word 📝", use_container_width=True): st.switch_page("pages/word_editor.py")
with h_cols[3]: 
    if st.button("Make Notes 📓", use_container_width=True, type="primary"): st.switch_page("pages/note.py")
with h_cols[4]: 
    if st.button("Summarizer 📝", use_container_width=True): st.switch_page("pages/Summarizer.py")
with h_cols[6]:
    if st.button("Logout 🚪", use_container_width=True):
        st.session_state.logged_in = False
        st.switch_page("app.py")

st.markdown("<hr style='margin:0 0 20px 0; border-top: 1px solid #E0DEDD;'>", unsafe_allow_html=True)

# --- STYLING ---
st.markdown("""
<style>
   .notebook-paper {
    background-color: #ffffff;
    border: 1px solid #e5e7eb;
    padding: 30px;
    border-radius: 12px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.06);
}

</style>
""", unsafe_allow_html=True)

# --- LATEST SUMMARY ---
latest_history = st.session_state.get("research_chat_history", [])
latest_summary = next((m["content"] for m in reversed(latest_history) if "### 📄 Summary" in m["content"]), None)

st.title("📓 Research Notebook")
st.write("Capture your personal thoughts, draft summaries, or plan your next academic steps.")

col1, col2 = st.columns([2, 1])

with col1:
    if latest_summary:
        with st.expander("✨ Latest Summary Detected"):
            st.info("Click the button below to add the latest summary into your notebook.")
            st.button(
                "📥 Append Summary to Note", 
                on_click=append_summary_callback, 
                args=(latest_summary,),
                use_container_width=True
            )

    st.markdown('<div class="notebook-paper">', unsafe_allow_html=True)
note_title = st.text_input("Note Title", placeholder="e.g., Deep Learning Chapter 1 Reflections")
st.text_area(
    "Your Academic Notes", 
    height=450, 
    placeholder="Start typing your thoughts here...",
    key="note_editor"
)
st.markdown('</div>', unsafe_allow_html=True)


with col2:
    st.info("💡 **Mentor Tip:** Use this space to synthesize what you've learned. Writing it in your own words improves retention!")
    st.subheader("Export Options")
    file_format = st.selectbox("Choose Format", ["PDF Document (.pdf)", "Text File (.txt)"])

    if st.button("🚀 Export Notebook Entry", use_container_width=True):
        final_content = st.session_state.get("note_editor", "")
        if final_content:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
            
            if "PDF" in file_format:
                pdf = FPDF()
                pdf.add_page()
                pdf.set_font("Arial", 'B', 18)
                pdf.cell(0, 15, txt=note_title if note_title else "Untitled Note", ln=True)
                pdf.set_font("Arial", size=10)
                pdf.cell(0, 10, txt=f"Date: {timestamp}", ln=True)
                pdf.ln(10)
                pdf.set_font("Arial", size=12)

                # PDF Text cleaning
                clean_text_content = final_content.encode('latin-1', 'ignore').decode('latin-1')
                pdf.multi_cell(0, 10, txt=clean_text_content)

                # Convert to bytes for Streamlit download
                pdf_bytes = pdf.output(dest='S').encode('latin-1')

                st.download_button(
                    label="📥 Download PDF",
                    data=pdf_bytes,
                    file_name=f"Note_{datetime.datetime.now().strftime('%d%m%y')}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
            else:
                txt_data = f"{note_title}\nDate: {timestamp}\n\n{final_content}"
                st.download_button(
                    label="📥 Download Text File",
                    data=txt_data,
                    file_name="my_notes.txt",
                    mime="text/plain",
                    use_container_width=True
                )
        else:
            st.warning("Please write something in your notebook before exporting!")

    if st.button("🗑️ Clear Page", use_container_width=True):
        st.session_state["note_editor"] = ""
        st.rerun()

st.divider()
st.caption("All notes created here are private to your current session. Remember to download them to save permanently.")
