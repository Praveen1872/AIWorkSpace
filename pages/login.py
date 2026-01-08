import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import requests
import os

st.set_page_config(
    page_title="AI Workspace Login",
    page_icon="🔑",
    layout="centered"
)

# ------------------ STYLING ------------------
st.markdown("""
<style>
/* App-wide theme for AI Workspace */
.stApp { 
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
    min-height: 100vh;
}

/* Main container - responsive padding and shadow */
[data-testid="stVerticalBlock"] > div:nth-child(2) {
    background: rgba(255, 255, 255, 0.95);
    backdrop-filter: blur(10px);
    padding: 3rem;
    border-radius: 24px;
    border: 1px solid rgba(255, 255, 255, 0.2);
    box-shadow: 0 20px 40px rgba(0,0,0,0.1);
    max-width: 450px;
    margin: 2rem auto;
}

/* Title - larger, with glow effect */
.title-text { 
    text-align: center; 
    font-weight: 900; 
    font-size: clamp(2rem, 5vw, 3rem); 
    background: linear-gradient(45deg, #667eea, #764ba2);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 1rem;
}

/* Subtitle */
.subtitle-text { 
    text-align: center; 
    color: #6b7280; 
    font-size: 1.1rem;
    margin-bottom: 2rem;
}

/* Input fields - modern glassmorphism */
.stTextInput > div > div > input {
    border-radius: 16px !important;
    border: 2px solid #e5e7eb !important;
    padding: 1rem 1.5rem !important;
    font-size: 1rem;
    transition: all 0.3s ease;
    background: rgba(255, 255, 255, 0.8);
}
.stTextInput > div > div > input:focus {
    border-color: #667eea !important;
    box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    transform: translateY(-2px);
}

/* Buttons - gradient, hover lift */
div.stButton > button {
    width: 100%;
    border-radius: 50px;
    height: 3.5rem;
    background: linear-gradient(45deg, #667eea, #764ba2);
    color: white;
    border: none;
    font-weight: 700;
    font-size: 1.1rem;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    box-shadow: 0 10px 20px rgba(102, 126, 234, 0.3);
}
div.stButton > button:hover {
    transform: translateY(-4px);
    box-shadow: 0 15px 30px rgba(102, 126, 234, 0.4);
}
div.stButton > button:active {
    transform: translateY(-2px);
}

/* Messages - styled */
.stSuccess > div, .stError > div, .stWarning > div {
    border-radius: 12px;
    border-left: 4px solid #10b981;
}

/* Register button separator */
hr {
    border: none;
    height: 1px;
    background: linear-gradient(90deg, transparent, #e5e7eb, transparent);
    margin: 2rem 0;
}

/* Mobile responsiveness */
@media (max-width: 768px) {
    [data-testid="stVerticalBlock"] > div:nth-child(2) {
        padding: 2rem 1.5rem;
        margin: 1rem;
        border-radius: 20px;
    }
    .title-text {
        font-size: 2rem;
    }
    div.stButton > button {
        height: 3rem;
        font-size: 1rem;
    }
}

/* Dark mode support (optional enhancement) */
@media (prefers-color-scheme: dark) {
    .stApp { background: linear-gradient(135deg, #1e293b 0%, #334155 100%); }
    [data-testid="stVerticalBlock"] > div:nth-child(2) {
        background: rgba(30, 41, 59, 0.95);
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# ------------------ FIREBASE INIT ------------------
def initialize_firebase():
    if not firebase_admin._apps:
        cred = credentials.Certificate({
            "type": "service_account",
            "project_id": os.getenv("FIREBASE_PROJECT_ID"),
            "client_email": os.getenv("FIREBASE_CLIENT_EMAIL"),
            "private_key": os.getenv("FIREBASE_PRIVATE_KEY").replace("\\n", "\n"),
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        })
        firebase_admin.initialize_app(cred)

    return firestore.client()

firestore_db = initialize_firebase()

# ------------------ FIREBASE SIGN-IN ------------------
def firebase_sign_in(email, password):
    url = (
        "https://identitytoolkit.googleapis.com/v1/"
        f"accounts:signInWithPassword?key={os.getenv('FIREBASE_WEB_API_KEY')}"
    )
    payload = {
        "email": email,
        "password": password,
        "returnSecureToken": True
    }
    return requests.post(url, json=payload)

# ------------------ SESSION INIT ------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# ------------------ UI ------------------
st.markdown("<h1 class='title-text'>🚀 AI Workspace</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitle-text'>Sign in to continue</p>", unsafe_allow_html=True)

email = st.text_input("📧 Email")
password = st.text_input("🔒 Password", type="password")

# ------------------ LOGIN LOGIC ------------------
if st.button("Sign In"):
    if not email or not password:
        st.warning("Please enter email and password")
    else:
        res = firebase_sign_in(email, password)
        if res.status_code == 200:
            data = res.json()
            uid = data["localId"]

            user_ref = firestore_db.collection("users").document(uid)
            if not user_ref.get().exists:
                user_ref.set({
                    "profile": {
                        "email": email,
                        "name": email.split("@")[0],
                        "level": "student",
                        "created_at": firestore.SERVER_TIMESTAMP
                    }
                })

            st.session_state.logged_in = True
            st.session_state.user_uid = uid
            st.session_state.user_email = email

            st.success("Login successful")
            st.switch_page("AIMentor.py")
        else:
            st.error(res.json()["error"]["message"].replace("_", " ").title())

# ------------------ REGISTER LINK ------------------
st.markdown("---")
if st.button("Create New Account 🚀"):
    st.switch_page("pages/register.py")
