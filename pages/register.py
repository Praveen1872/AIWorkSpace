import streamlit as st
import firebase_admin
from firebase_admin import credentials, auth, firestore
from datetime import datetime

st.set_page_config(page_title="AI Workspace Register", page_icon="🛡️", layout="centered")

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
    .title-text { text-align: center; font-weight: 800; color: #1A1A1A; font-size: 2.2rem; }
    .subtitle-text { text-align: center; color: #666; margin-bottom: 30px; }
    div.stButton > button {
        display: block; margin: 0 auto; width: 100%; border-radius: 50px;
        height: 3.5em; background-color: #1A1A1A; color: white; border: none;
        font-weight: 600; transition: all 0.3s ease;
    }
    div.stButton > button:hover { background-color: #333333; transform: scale(1.02); color: white !important; }
    .footer-link { color: #1A1A1A; font-weight: 700; text-decoration: none !important; }
</style>
""", unsafe_allow_html=True)

st.markdown("<h1 class='title-text'>🛡️ Join the Workspace</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitle-text'>Create your secure account to start your AI-powered research.</p>", unsafe_allow_html=True)

email = st.text_input("📧 Work Email", placeholder="name@company.com")
password = st.text_input("🔒 Password", type="password", placeholder="Create a strong password")

# ------------------ FIREBASE INITIALIZATION ------------------
def initialize_firebase():
    if not firebase_admin._apps:
        try:
            creds_dict = dict(st.secrets["firebase_credentials"])

            # Fix multiline private key
            private_key = creds_dict["private_key"]
            private_key = private_key.strip().replace("\r\n", "\n").replace("\r", "\n")
            creds_dict["private_key"] = private_key

            cred = credentials.Certificate(creds_dict)
            firebase_admin.initialize_app(cred)

        except Exception as e:
            st.error(f"Firebase Initialization Failed: {e}")

initialize_firebase()
firestore_db = firestore.client()

# ------------------ SIGN UP LOGIC ------------------
if st.button("Sign Up"):
    if email and password:
        try:
            # 1️⃣ Create Firebase Auth User
            user = auth.create_user(
                email=email,
                password=password
            )

            # 2️⃣ Create Firestore User Document
            firestore_db.collection("users").document(user.uid).set({
                "profile": {
                    "name": email.split("@")[0],
                    "email": email,
                    "level": "student",
                    "created_at": firestore.SERVER_TIMESTAMP
                },
                "preferences": {
                    "font": "Poppins",
                    "tone": "professional",
                    "theme": "light"
                }
            })

            st.balloons()
            st.success("Account created successfully! Please log in.")
            st.switch_page("pages/login.py")

        except Exception as e:
            st.error(f"Registration failed: {str(e)}")
    else:
        st.warning("Please fill in all fields.")

# ------------------ FOOTER ------------------
st.markdown("<hr style='border-top: 1px solid #E0DEDD; margin-top: 40px;'>", unsafe_allow_html=True)
st.markdown("""
<div style="text-align: center; color: #666;">
    Already have an account? 
    <a href="/login" target="_self" class="footer-link">
        Log In here 🚀
    </a>
</div>
""", unsafe_allow_html=True)
