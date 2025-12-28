import streamlit as st
import firebase_admin
from firebase_admin import credentials, db
from google import genai
from google.genai import types
from fpdf import FPDF
import PIL.Image
import io
import os

import streamlit as st
import firebase_admin
from firebase_admin import credentials

# Use your actual database URL
DB_URL = 'https://workspace-1f516-default-rtdb.asia-southeast1.firebasedatabase.app/'

if not firebase_admin._apps:
    try:
        if "firebase_credentials" in st.secrets:
            # 1. Fetch the secret as a dictionary
            firebase_creds = dict(st.secrets["firebase_credentials"])
            
            # 2. THE CRITICAL FIX: 
            # We must ensure literal '\n' characters are treated as real newlines.
            firebase_creds["private_key"] = firebase_creds["private_key"].replace("\\n", "\n")
            
            # 3. Initialize using the dictionary
            cred = credentials.Certificate(firebase_creds)
            firebase_admin.initialize_app(cred, {'databaseURL': DB_URL})
        else:
            st.error("Secrets not found in Dashboard!")
    except Exception as e:
        st.error(f"Handshake failed: {e}")

        
client = genai.Client(api_key=API_KEY)
MODEL_ID = "gemini-2.5-flash-lite" 
st.set_page_config(page_title="AI Professional Workspace", layout="wide")
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
        background-color: #FF6042; 
        color: white;
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

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

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
    
    return bytes(pdf.output())

st.set_page_config(initial_sidebar_state="collapsed", layout="wide")

is_logged_in = st.session_state.get('logged_in', False)

current_page = os.path.basename(__file__)
is_home = (current_page == "AIMentor.py")


if not is_logged_in and not is_home and current_page not in ["login.py", "register.py"]:
    st.session_state.next_page = f"pages/{current_page}"
    st.switch_page("pages/login.py")

# 4. HEADER UI
if is_home and not is_logged_in:
    cols = st.columns([1, 2, 1], vertical_alignment="center")
    with cols[1]:
        st.markdown("<h1 style='text-align: center; margin:0;'>🚀 AI Workspace</h1>", unsafe_allow_html=True)
    with cols[2]:
        btn_cols = st.columns(2)
        with btn_cols[0]:
            if st.button("Sign In 👤", use_container_width=True, key="home_login"): 
                st.switch_page("pages/login.py")
        with btn_cols[1]:
            if st.button("Sign Up 🚀", use_container_width=True, type="primary", key="home_reg"): 
                st.switch_page("pages/register.py")
else:
    cols = st.columns([2, 0.7, 0.7, 0.7, 0.9, 1.8, 1], vertical_alignment="center")
    
    with cols[0]:
        st.markdown("<h3 style='margin:0;'>🚀 AI Mentor</h3>", unsafe_allow_html=True)

    if is_logged_in:
        with cols[1]:
            if st.button("PPT 🖼️", use_container_width=True, key="hdr_ppt"): 
                st.switch_page("pages/ppt_editor.py")
        with cols[2]:
            if st.button("Word 📝", use_container_width=True, key="hdr_word"): 
                st.switch_page("pages/word_editor.py")
        with cols[3]:
            if st.button("Note 📓", use_container_width=True, key="hdr_note"): 
                st.switch_page("pages/note.py")
        with cols[4]:
            if st.button("Summarize 📝", use_container_width=True, key="hdr_sum"): 
                st.switch_page("pages/Summarizer.py")
        with cols[6]:
            if st.button("Logout 🚪", use_container_width=True, key="hdr_out"):
                st.session_state.logged_in = False
                st.switch_page("AIMentor.py")
    else:
        
        with cols[5]:
            if st.button("Sign In 👤", use_container_width=True, key="hdr_login"): 
                st.switch_page("pages/login.py")
        with cols[6]:
            if st.button("Sign Up 🚀", use_container_width=True, type="primary", key="hdr_signup"): 
                st.switch_page("pages/register.py")

st.markdown("<hr style='margin: 0 0 20px 0; border-top: 1px solid #E0DEDD;'>", unsafe_allow_html=True)
if not st.session_state.logged_in:
    
    main_col1, main_col2 = st.columns([1.2, 1], gap="large")

    with main_col1:
        st.markdown("<br><br>", unsafe_allow_html=True) # Vertical spacing
        st.markdown("""
            <h1 style='font-size: 3rem; margin-bottom: 0;'>🚀 Welcome to</h1>
            <h1 style='font-size: 4rem; color: #FF6042; margin-top: -20px;'>AI Workspace</h1>
            <p style='font-size: 1.2rem; color: #555;'>Stop wasting hours on tasks AI can handle. 
            Your personal academic mentor is ready to help you excel.</p>
        """, unsafe_allow_html=True)
        
        st.info("💡 Please **Sign In** or **Sign Up** to access your persistent AI Mentor.")
        
        
        if st.button("Unlock Your AI Workspace ✨", use_container_width=True, key="main_unlock"):
            st.switch_page("pages/login.py")
        
        st.markdown("<p style='text-align: center; color: #888;'>Powered by <b>Google Gemini AI</b></p>", unsafe_allow_html=True)

    with main_col2:
        
        banner_path = r"C:\Users\potnu\Downloads\banner2_desktop.png"
        if os.path.exists(banner_path):
            st.image(banner_path, use_container_width=True)
        else:
            
            st.image("https://img.freepik.com/free-vector/ai-technology-brain-background-digital-transformation-concept_53876-117772.jpg", 
                     caption="Image Not Found at provided local path", use_container_width=True)

    st.stop() 
user_uid = st.session_state.user_uid
chat_ref = db.reference(f"users/{user_uid}/chunks/chat_history")

if "messages" not in st.session_state:
    saved_history = chat_ref.get()
    st.session_state.messages = list(saved_history.values()) if isinstance(saved_history, dict) else (saved_history if saved_history else [])


with st.sidebar:
    st.title("🛠️ Tools")
    feature = st.radio("Mode:", ["Doubts Solver", "Career Guide"])
    st.markdown("---")
    deep_dive = st.toggle("Detailed Mode (Deep Dive)", value=False)
    if st.button("🗑️ Clear My Learning Data"):
        st.session_state.messages = []
        chat_ref.delete()
        st.rerun()


chat_display = st.container()
with chat_display:
    for i, message in enumerate(st.session_state.messages):
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            
            if message["role"] == "assistant" and i > 0:
                user_q = st.session_state.messages[i-1]["content"]
                pdf_bytes = export_last_chat_to_pdf(user_q, message["content"])
                st.download_button("📝 Save as Note", pdf_bytes, f"note_{i}.pdf", key=f"note_{i}")


with st.expander("➕ Attach Image (Math problems, Diagrams, Notes)", expanded=False):
    up_img = st.file_uploader("Choose an image", type=["jpg", "jpeg", "png"], label_visibility="collapsed")
    if up_img:
        st.image(up_img, caption="Image ready for analysis", width=250)

if prompt := st.chat_input(f"Consulting {feature}..."):
    # Store User Message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with chat_display:
        with st.chat_message("user"):
            st.markdown(prompt)
            if up_img:
                st.image(up_img, width=250)

    # Process AI Response
    with st.chat_message("assistant"):
        resp_placeholder = st.empty()
        thought_expander = st.expander("💭 Core Intelligence Reasoning", expanded=False)
        
        SYSTEM_PROMPT = f"You are an Elite Academic Mentor. Mode: {feature}. Strategy: {'Detailed' if deep_dive else 'Concise'}."
        
        try:
            
            input_data = [prompt]
            if up_img:
                img = PIL.Image.open(up_img)
                input_data.append(img)
            
            
            response = client.models.generate_content(
                model=MODEL_ID,
                contents=input_data,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_PROMPT,
                    thinking_config=types.ThinkingConfig(include_thoughts=True)
                )
            )

            thought_text = "".join([p.text for p in response.candidates[0].content.parts if p.thought])
            final_answer = "".join([p.text for p in response.candidates[0].content.parts if not p.thought])

            if thought_text: thought_expander.markdown(thought_text)
            resp_placeholder.markdown(final_answer)
            
            # Save to history & Firebase
            st.session_state.messages.append({"role": "assistant", "content": final_answer})
            chat_ref.set(st.session_state.messages)
            st.rerun()

        except Exception as e:
            st.error(f"Connection Error: {e}")