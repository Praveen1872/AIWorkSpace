import streamlit as st
import firebase_admin
from firebase_admin import credentials, auth, firestore
from google import genai
from google.genai import types
from fpdf import FPDF
import PIL.Image
import io

API_KEY = st.secrets["GEMINI_API_KEY"]
def initialize_firebase():
    if not firebase_admin._apps:
        try:
            creds_dict = dict(st.secrets["firebase_credentials"])

        
            private_key = creds_dict["private_key"]
            private_key = private_key.strip()
            private_key = private_key.replace("\r\n", "\n").replace("\r", "\n")

            creds_dict["private_key"] = private_key

            cred = credentials.Certificate(creds_dict)

            firebase_admin.initialize_app(cred)


        except Exception as e:
            st.error(f"Firebase Initialization Failed: {e}")

initialize_firebase()

firestore_db = firestore.client()

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
        width: 112%;
        font-weight: 600;
        letter-spacing: 0.3px;
        box-shadow: 0px 2px 4px rgba(0, 0, 0, 0.05); /* Subtle depth */
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        justify-content: flex-end; /* aligns buttons to the right */
        gap: 10px;
        margin-right: 30px;
        margin-top: -50px; /* adjust vertical alignment if needed */
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


if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

is_logged_in = st.session_state.logged_in


cols = st.columns([2, 0.7, 0.7, 0.7, 0.9, 1.8, 1], vertical_alignment="center")
with cols[0]:
    st.markdown("<h3 style='margin:0; font-weight:800;'>🚀 AI WrokSpace</h3>", unsafe_allow_html=True)

if is_logged_in:
    with cols[1]:
        if st.button("PPT 🖼️", key="hdr_ppt"): st.switch_page("pages/ppt_editor.py")
    with cols[2]:
        if st.button("Word 📝", key="hdr_word"): st.switch_page("pages/word_editor.py")
    with cols[3]:
        if st.button("Note 📓", key="hdr_note"): st.switch_page("pages/note.py")
    with cols[4]:
        if st.button("Summarize📝", key="hdr_sum"): st.switch_page("pages/Summarizer.py")
    with cols[6]:
        if st.button("Logout 🚪", key="hdr_out"):
            st.session_state.logged_in = False
            st.rerun()
else:
    with cols[5]:
        if st.button("Sign In 👤", key="hdr_login"): st.switch_page("pages/login.py")
    with cols[6]:
        if st.button("Sign Up 🚀", key="hdr_signup"): st.switch_page("pages/register.py")

st.markdown("<hr>", unsafe_allow_html=True)


if not is_logged_in:
    main_col1, main_col2 = st.columns([1.2, 1], gap="large")
    with main_col1:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown("""
             <h1 style='font-size: 3rem; margin-bottom: 0;'>👋 Welcome to</h1>
            <h1 style='font-size: 4rem; color: #FF6042; margin-top: -20px;'>AI Workspace</h1>
            <p style='font-size: 1.25rem; color: #555; margin-top: 20px;'> Stop wasting hours on tasks AI can handle.  
        Your personal academic mentor is ready to help you.</p>
        """, unsafe_allow_html=True)
        st.info("💡 Please Sign In or Sign Up to access your persistent AI Mentor.")
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Unlock Your AI Workspace 👉", key="main_unlock",use_container_width=True):
            
            st.switch_page("pages/register.py")
        st.markdown("<p style='text-align: center; margin-left:60px; color: #888;'>Powered by <b>Google Gemini AI</b></p>", unsafe_allow_html=True)
    with main_col2:
        
        st.image("assets/banner2_desktop.png", use_container_width=True)


        st.stop()

if "messages" not in st.session_state:
    st.session_state.messages = []
is_logged_in = st.session_state.logged_in

user_uid = st.session_state.get("user_uid", "guest_user")

chats_col = (
    firestore_db
    .collection("users")
    .document(user_uid)
    .collection("chats")
)
memory_ref = (
    firestore_db
    .collection("users")
    .document(user_uid)
    .collection("memory")
    .document("summary")
)

memory_doc = memory_ref.get()

if memory_doc.exists:
    long_term_memory = memory_doc.to_dict().get("long_term_summary", "")
else:
    long_term_memory = ""

def update_long_term_memory(chats_col, memory_ref):
    docs = chats_col.order_by("timestamp", direction=firestore.Query.DESCENDING).limit(10).stream()
    
    recent_chats = []
    for doc in docs:
        d = doc.to_dict()
        recent_chats.append(f"{d['role']}: {d['content']}")

    recent_chats.reverse()
    chat_text = "\n".join(recent_chats)

    memory_doc = memory_ref.get()
    old_memory = memory_doc.to_dict().get("long_term_summary", "")

    prompt = f"""
You are an AI memory summarizer.

Existing memory:
{old_memory}

Recent conversation:
{chat_text}

Update the memory with:
- User goals
- Repeated topics
- Preferences
- Important context

Keep it concise (5–7 lines).
"""

    response = client.models.generate_content(
        model=MODEL_ID,
        contents=[prompt]
    )

    memory_ref.set({
        "long_term_summary": response.text,
        "updated_at": firestore.SERVER_TIMESTAMP
    })
if "messages" in st.session_state and len(st.session_state.messages) > 0:
    if len(st.session_state.messages) % 4 == 0:
        update_long_term_memory(chats_col, memory_ref)



if "messages" not in st.session_state:
    messages = []
    docs = chats_col.order_by("timestamp").stream()
    for doc in docs:
        messages.append(doc.to_dict())
    st.session_state.messages = messages


with st.sidebar:
    st.markdown("<h2 style='color: #FF6042;'>🛠️ Workspace</h2>", unsafe_allow_html=True)

    feature = st.radio("Model Context:", ["Doubts Solver", "Career Guide"])
    st.markdown("---")
    deep_dive = st.toggle("Detailed Mode (Deep Dive)", value=False)

    if st.button("🗑️ Reset All Progress"):
        for doc in chats_col.stream():
            doc.reference.delete()
        st.session_state.messages = []
        st.rerun()


       


chat_display = st.container()
with chat_display:
    for i, message in enumerate(st.session_state.messages):
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if message["role"] == "assistant" and i > 0:
                user_q = st.session_state.messages[i-1]["content"]
                pdf_bytes = export_last_chat_to_pdf(user_q, message["content"])
                st.download_button("📝 Export as PDF", pdf_bytes, f"note_{i}.pdf", key=f"dl_{i}")


with st.expander("📷 Analysis Tools (Upload Images/Diagrams)", expanded=False):
    up_img = st.file_uploader("Upload visual data for the AI to analyze", type=["jpg", "jpeg", "png"])
    if up_img:
        st.image(up_img, caption="Image Attachment Ready", width=300)


if prompt := st.chat_input(f"Ask your {feature}..."):

    # 1️⃣ Add user message to UI memory
    st.session_state.messages.append({
        "role": "user",
        "content": prompt
    })

    # 2️⃣ Store user message in Firestore
    chats_col.add({
        "role": "user",
        "content": prompt,
        "timestamp": firestore.SERVER_TIMESTAMP
    })

    with chat_display:
        with st.chat_message("user"):
            st.markdown(prompt)
            if up_img:
                st.image(up_img, width=300)

    with st.chat_message("assistant"):
        resp_placeholder = st.empty()

        SYSTEM_PROMPT = f"""You are an Elite Academic Mentor AI.
        User Memory:{long_term_memory}
        Current Mode: {feature}
        Response Style: {'Detailed Research' if deep_dive else 'Concise Insight'}Be consistent with the user's past goals and preferences.
"""

        try:
            input_data = [prompt]
            if up_img:
                img = PIL.Image.open(up_img)
                input_data.append(img)

            response = client.models.generate_content(
                model=MODEL_ID,
                contents=input_data,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_PROMPT
                )
            )

            final_answer = response.text
            resp_placeholder.markdown(final_answer)

            # 3️⃣ Add assistant message to UI memory
            st.session_state.messages.append({
                "role": "assistant",
                "content": final_answer
            })

            # 4️⃣ Store assistant message in Firestore
            chats_col.add({
                "role": "assistant",
                "content": final_answer,
                "timestamp": firestore.SERVER_TIMESTAMP
            })

            st.rerun()

        except Exception as e:
            st.error(f"AI Connection Failed: {e}")
