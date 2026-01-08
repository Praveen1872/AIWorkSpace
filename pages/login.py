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
.stApp { background-color: #FAF8F7; }
[data-testid="stVerticalBlock"] > div:nth-child(2) {
    background-color: white;
    padding: 40px;
    border-radius: 25px;
    border: 1px solid #E0DEDD;
    box-shadow: 0px 4px 20px rgba(0,0,0,0.03);
}
.title-text { text-align: center; font-weight: 800; font-size: 2.2rem; }
.subtitle-text { text-align: center; color: #666; margin-bottom: 30px; }
div.stButton > button {
    width: 100%;
    border-radius: 50px;
    height: 3.5em;
    background-color: #1A1A1A;
    color: white;
    border: none;
    font-weight: 600;
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
