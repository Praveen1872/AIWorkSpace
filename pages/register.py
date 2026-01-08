import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import requests
import os

st.set_page_config(
    page_title="AI Workspace Register",
    page_icon="🛡️",
    layout="centered"
)

# ------------------ STYLING ------------------
# st.markdown("""
# <style>
# .stApp { background-color: #FAF8F7; }
# [data-testid="stVerticalBlock"] > div:nth-child(2) {
#     background-color: white;
#     padding: 40px;
#     border-radius: 25px;
#     border: 1px solid #E0DEDD;
#     box-shadow: 0px 4px 20px rgba(0,0,0,0.03);
# }
# .title-text { text-align: center; font-weight: 800; font-size: 2.2rem; }
# .subtitle-text { text-align: center; color: #666; margin-bottom: 30px; }
# div.stButton > button {
#     width: 100%;
#     border-radius: 50px;
#     height: 3.5em;
#     background-color: #1A1A1A;
#     color: white;
#     border: none;
#     font-weight: 600;
# }
# </style>
# """, unsafe_allow_html=True)

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

# ------------------ FIREBASE SIGN-UP (REST) ------------------
def firebase_sign_up(email, password):
    url = (
        "https://identitytoolkit.googleapis.com/v1/"
        f"accounts:signUp?key={os.getenv('FIREBASE_WEB_API_KEY')}"
    )
    payload = {
        "email": email,
        "password": password,
        "returnSecureToken": True
    }
    return requests.post(url, json=payload)

# ------------------ UI ------------------
st.markdown("<h1 class='title-text'>🛡️ Create Account</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitle-text'>Join the AI Workspace</p>", unsafe_allow_html=True)

email = st.text_input("📧 Email")
password = st.text_input("🔒 Password", type="password")
confirm_password = st.text_input("🔒 Confirm Password", type="password")

# ------------------ REGISTER LOGIC ------------------
if st.button("Sign Up"):
    if not email or not password or not confirm_password:
        st.warning("Please fill in all fields")
    elif password != confirm_password:
        st.error("Passwords do not match")
    elif len(password) < 6:
        st.error("Password must be at least 6 characters")
    else:
        res = firebase_sign_up(email, password)
        if res.status_code == 200:
            data = res.json()
            uid = data["localId"]

            firestore_db.collection("users").document(uid).set({
                "profile": {
                    "email": email,
                    "name": email.split("@")[0],
                    "level": "student",
                    "created_at": firestore.SERVER_TIMESTAMP
                },
                "preferences": {
                    "font": "Poppins",
                    "tone": "professional",
                    "theme": "light"
                }
            })

            st.success("Account created successfully. Please sign in.")
            st.switch_page("pages/login.py")
        else:
            st.error(res.json()["error"]["message"].replace("_", " ").title())

# ------------------ FOOTER ------------------
st.markdown("---")
if st.button("Already have an account? Sign In"):
    st.switch_page("pages/login.py")
