import streamlit as st
import firebase_admin
from firebase_admin import credentials, auth, db

# --- 1. PAGE CONFIGURATION & STYLING ---
st.set_page_config(page_title="AI Workspace Register", page_icon="🛡️", layout="centered")

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

# --- 2. FIREBASE INITIALIZATION ---
DB_URL = 'https://workspace-1f516-default-rtdb.asia-southeast1.firebasedatabase.app/'
# --- THE SURGICAL PEM REPAIR ---
import streamlit as st
import firebase_admin
from firebase_admin import credentials, auth, db

# --- THE CLEAN-ROOM REPAIR BLOCK ---
def initialize_firebase():
    if not firebase_admin._apps:
        try:
            if "firebase_credentials" in st.secrets:
                # 1. Standardize the dictionary
                creds_dict = dict(st.secrets["firebase_credentials"])
                
                # 2. SURGICAL REPAIR OF THE PRIVATE KEY
                # This removes all literal backslashes and ensures proper PEM wrapping
                raw_key = creds_dict["private_key"]
                
                # Replace literal \n and remove any stray quotes or spaces
                clean_key = raw_key.replace("\\n", "\n").strip().strip('"').strip("'")
                
                # Ensure the header and footer are exactly on their own lines
                if "-----BEGIN PRIVATE KEY-----" not in clean_key:
                    clean_key = f"-----BEGIN PRIVATE KEY-----\n{clean_key}"
                if "-----END PRIVATE KEY-----" not in clean_key:
                    clean_key = f"{clean_key}\n-----END PRIVATE KEY-----"
                
                # Final normalization: Ensure no double headers/footers
                clean_key = clean_key.replace("\n\n", "\n")
                creds_dict["private_key"] = clean_key
                
                # 3. Initialize
                cred = credentials.Certificate(creds_dict)
                firebase_admin.initialize_app(cred, {
                    'databaseURL': 'https://workspace-1f516-default-rtdb.asia-southeast1.firebasedatabase.app/'
                })
            else:
                st.error("Credentials key missing in Streamlit Secrets!")
        except Exception as e:
            st.error(f"JWT Signature Fix Failed: {e}")

initialize_firebase()

# --- 3. REGISTRATION UI ---
st.markdown("<h1 class='title-text'>🛡️ Join the Workspace</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitle-text'>Create your secure account to start your AI-powered research.</p>", unsafe_allow_html=True)

email = st.text_input("📧 Work Email", placeholder="name@company.com")
password = st.text_input("🔒 Password", type="password", placeholder="Create a strong password")

st.markdown("<br>", unsafe_allow_html=True)

if st.button("Sign Up"):
    if email and password:
        try:
            user = auth.create_user(email=email, password=password)
            db.reference(f"users/{user.uid}").set({
                "email": email,
                "chat_history": []
            })
            st.balloons()
            st.success("Account created! Redirecting to login...")
            st.switch_page("pages/login.py")
        except Exception as e:
            st.error(f"Registration failed: {e}")
    else:
        st.warning("Please fill in all fields.")

st.markdown("<hr style='border-top: 1px solid #E0DEDD; margin-top: 40px;'>", unsafe_allow_html=True)
st.markdown("<div style='text-align: center; color: #666;'>Already have an account? <a href='/login' target='_self' class='footer-link'>Log In here 🚀</a></div>", unsafe_allow_html=True)