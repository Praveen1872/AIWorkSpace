import streamlit as st
import firebase_admin
from firebase_admin import credentials, db
from google import genai  # Modern package
from google.genai import types
from fpdf import FPDF
import PIL.Image
import io
import os

# --- 1. FIREBASE & API SETUP ---
API_KEY = st.secrets["GEMINI_API_KEY"]
DB_URL = 'https://workspace-1f516-default-rtdb.asia-southeast1.firebasedatabase.app/'
MODEL_ID = "gemini-2.0-flash-exp" 
# --- THE FINAL JWT SIGNATURE REPAIR BLOCK ---
if not firebase_admin._apps:
    try:
        if "firebase_credentials" in st.secrets:
            # 1. Convert secrets object to a standard dictionary
            creds_dict = dict(st.secrets["firebase_credentials"])
            
            # 2. Get the raw key and strip any accidental whitespace
            raw_key = creds_dict["private_key"]
            
            # 3. THE CRITICAL FIX:
            # We must handle keys that are "double escaped" or contain literal \n text.
            # This handles both standard JSON exports and manual pastes.
            if "\\n" in raw_key:
                cleaned_key = raw_key.replace("\\n", "\n")
            else:
                cleaned_key = raw_key
                
            creds_dict["private_key"] = cleaned_key
            
            # 4. Initialize
            cred = credentials.Certificate(creds_dict)
            firebase_admin.initialize_app(cred, {
                'databaseURL': 'https://workspace-1f516-default-rtdb.asia-southeast1.firebasedatabase.app/'
            })
        else:
            st.error("Credentials not found in Streamlit Secrets.")
    except Exception as e:
        st.error(f"Authentication Error: {e}")

# Initialize Modern AI Client (Replaces deprecated google.generativeai)
client = genai.Client(api_key=API_KEY)

# --- 2. PAGE CONFIG & STYLING ---
st.set_page_config(page_title="AI Professional Workspace", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
    .stApp { 
        background-color: #FAF8F7; 
        color: #1A1A1A; 
        font-family: 'Inter', sans-serif;
    }
    [data-testid="column"] {
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 0px 5px !important;
    }
    div.stButton > button { 
        border-radius: 12px; 
        background-color: #FF6042; 
        color: white;
        border: none;
        height: 3.2em;
        width: 100%;
        font-weight: 600;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    div.stButton > button:hover {
        background-color: #FF4520;
        color: white !important;
        transform: translateY(-2px);
        box-shadow: 0px 6px 15px rgba(255, 96, 66, 0.3);
    }
    hr {
        margin-top: 1rem;
        margin-bottom: 2rem;
        border-top: 1px solid #E0DEDD;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. HELPER FUNCTIONS ---
def export_last_chat_to_pdf(user_text, ai_text):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt="Research Note Export", ln=True, align='C')
    pdf.ln(10)
    
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, txt="Your Question:", ln=True)
    pdf.set_font("Arial", size=11)
    pdf.multi_cell(0, 8, txt=user_text.encode('latin-1', 'ignore').decode('latin-1'))
    
    pdf.ln(5)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, txt="AI Mentor Response:", ln=True)
    pdf.set_font("Arial", size=11)
    pdf.multi_cell(0, 8, txt=ai_text.encode('latin-1', 'ignore').decode('latin-1'))
    
    return pdf.output(dest='S').encode('latin-1')

# --- 4. NAVIGATION & AUTH LOGIC ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

is_logged_in = st.session_state.logged_in

# Header UI - Updated with width="stretch" for 2026 compliance
cols = st.columns([2, 0.7, 0.7, 0.7, 0.9, 1.8, 1], vertical_alignment="center")
with cols[0]:
    st.markdown("<h3 style='margin:0;'>🚀 AI Mentor</h3>", unsafe_allow_html=True)

if is_logged_in:
    with cols[1]:
        if st.button("PPT 🖼️", key="hdr_ppt"): st.switch_page("pages/ppt_editor.py")
    with cols[2]:
        if st.button("Word 📝", key="hdr_word"): st.switch_page("pages/word_editor.py")
    with cols[3]:
        if st.button("Note 📓", key="hdr_note"): st.switch_page("pages/note.py")
    with cols[4]:
        if st.button("Summarize 📝", key="hdr_sum"): st.switch_page("pages/Summarizer.py")
    with cols[6]:
        if st.button("Logout 🚪", key="hdr_out"):
            st.session_state.logged_in = False
            st.rerun()
else:
    with cols[5]:
        if st.button("Sign In 👤", key="hdr_login"): st.switch_page("pages/login.py")
    with cols[6]:
        if st.button("Sign Up 🚀", key="hdr_signup", type="primary"): st.switch_page("pages/register.py")

st.markdown("<hr>", unsafe_allow_html=True)

# --- 5. LANDING PAGE (IF NOT LOGGED IN) ---
if not is_logged_in:
    main_col1, main_col2 = st.columns([1.2, 1], gap="large")
    with main_col1:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown("""
            <h1 style='font-size: 3rem; margin-bottom: 0;'>🚀 Welcome to</h1>
            <h1 style='font-size: 4rem; color: #FF6042; margin-top: -20px;'>AI Workspace</h1>
            <p style='font-size: 1.2rem; color: #555;'>Stop wasting hours on tasks AI can handle. 
            Your personal academic mentor is ready to help you excel.</p>
        """, unsafe_allow_html=True)
        st.info("💡 Please **Sign In** or **Sign Up** to access your persistent AI Mentor.")
        if st.button("Unlock Your AI Workspace ✨", key="main_unlock"):
            st.switch_page("pages/login.py")
    with main_col2:
        # Replaced use_container_width with width="stretch"
        st.image("https://img.freepik.com/free-vector/ai-technology-brain-background-digital-transformation-concept_53876-117772.jpg", width="stretch")
    st.stop()

# --- 6. CHAT INTERFACE (IF LOGGED IN) ---
user_uid = st.session_state.get('user_uid', 'guest_user')
chat_ref = db.reference(f"users/{user_uid}/chat_history")

if "messages" not in st.session_state:
    saved_history = chat_ref.get()
    st.session_state.messages = saved_history if saved_history else []

with st.sidebar:
    st.title("🛠️ Tools")
    feature = st.radio("Mode:", ["Doubts Solver", "Career Guide"])
    st.markdown("---")
    deep_dive = st.toggle("Detailed Mode (Deep Dive)", value=False)
    if st.button("🗑️ Clear My Learning Data"):
        st.session_state.messages = []
        chat_ref.delete()
        st.rerun()

# Display Chat History
chat_display = st.container()
with chat_display:
    for i, message in enumerate(st.session_state.messages):
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if message["role"] == "assistant" and i > 0:
                user_q = st.session_state.messages[i-1]["content"]
                pdf_bytes = export_last_chat_to_pdf(user_q, message["content"])
                st.download_button("📝 Save as Note", pdf_bytes, f"note_{i}.pdf", key=f"dl_{i}")

# Image Attachment Area
with st.expander("➕ Attach Image (Math problems, Diagrams, Notes)", expanded=False):
    up_img = st.file_uploader("Choose an image", type=["jpg", "jpeg", "png"], label_visibility="collapsed")
    if up_img:
        st.image(up_img, caption="Image ready for analysis", width=250)

# Input Processing
if prompt := st.chat_input(f"Consulting {feature}..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with chat_display:
        with st.chat_message("user"):
            st.markdown(prompt)
            if up_img: st.image(up_img, width=250)

    with st.chat_message("assistant"):
        resp_placeholder = st.empty()
        SYSTEM_PROMPT = f"You are an Elite Academic Mentor. Mode: {feature}. Strategy: {'Detailed' if deep_dive else 'Concise'}."
        
        try:
            input_data = [prompt]
            if up_img:
                img = PIL.Image.open(up_img)
                input_data.append(img)
            
            # Using modern Client structure
            response = client.models.generate_content(
                model=MODEL_ID,
                contents=input_data,
                config=types.GenerateContentConfig(system_instruction=SYSTEM_PROMPT)
            )

            final_answer = response.text
            resp_placeholder.markdown(final_answer)
            
            st.session_state.messages.append({"role": "assistant", "content": final_answer})
            chat_ref.set(st.session_state.messages)
            st.rerun()

        except Exception as e:
            st.error(f"Connection Error: {e}")