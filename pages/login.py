import streamlit as st
import firebase_admin
from firebase_admin import credentials, auth, db

# --- 1. PAGE CONFIGURATION & STYLING ---
st.set_page_config(page_title="AI Workspace Login", page_icon="🔑", layout="centered")

st.markdown("""
<style>
    .stApp { background-color: #FAF8F7; }
    
    /* Card Container */
    [data-testid="stVerticalBlock"] > div:nth-child(2) {
        background-color: white;
        padding: 40px;
        border-radius: 25px;
        border: 1px solid #E0DEDD;
        box-shadow: 0px 4px 20px rgba(0,0,0,0.03);
    }

    .title-text { text-align: center; font-weight: 800; color: #1A1A1A; font-size: 2.2rem; }
    .subtitle-text { text-align: center; color: #666; margin-bottom: 30px; }

    /* Action Button styling */
    div.stButton > button {
        display: block;
        margin: 0 auto;
        width: 100%;
        border-radius: 50px;
        height: 3.5em;
        background-color: #1A1A1A;
        color: white;
        border: none;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    div.stButton > button:hover {
        background-color: #333333;
        transform: scale(1.02);
        color: white !important;
    }

    .footer-link {
        color: #1A1A1A;
        font-weight: 700;
        text-decoration: none !important;
    }
</style>
""", unsafe_allow_html=True)
def initialize_firebase():
    if not firebase_admin._apps:
        try:
            if "firebase_credentials" in st.secrets:
                creds_dict = dict(st.secrets["firebase_credentials"])
                
                # 1. Clean all formatting (literal \n, spaces, etc.)
                raw_key = creds_dict["private_key"]
                clean_body = (
                    raw_key.replace("\\n", "")
                    .replace("-----BEGIN PRIVATE KEY-----", "")
                    .replace("-----END PRIVATE KEY-----", "")
                    .replace(" ", "")
                    .replace("\n", "")
                    .strip()
                )
                
                # 2. Re-wrap into 64-character lines (Standard PEM format)
                wrapped_body = "\n".join([clean_body[i:i+64] for i in range(0, len(clean_body), 64)])
                
                # 3. Final Reconstruction
                creds_dict["private_key"] = f"-----BEGIN PRIVATE KEY-----\n{wrapped_body}\n-----END PRIVATE KEY-----\n"
                
                cred = credentials.Certificate(creds_dict)
                firebase_admin.initialize_app(cred, {
                    'databaseURL': 'https://workspace-1f516-default-rtdb.asia-southeast1.firebasedatabase.app/'
                })
                print("🚀 Firebase Success!")
        except Exception as e:
            st.error(f"Byte Repair Failed: {e}")

initialize_firebase()
# --- 3. LOGIN UI ---
st.markdown("<h1 class='title-text'>🚀 AI Mentor Workspace</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitle-text'>Welcome back! Please sign in to access your personal AI researcher.</p>", unsafe_allow_html=True)

email = st.text_input("📧 Email Address", placeholder="name@example.com")
password = st.text_input("🔒 Password", type="password", placeholder="Enter your password")

st.markdown("<br>", unsafe_allow_html=True)

# Sign In Logic
if st.button("Sign In"):
    if email and password:
        try:
            # Check if user exists in Firebase Auth
            user = auth.get_user_by_email(email)
            
            # Set Session States for global access
            st.session_state.logged_in = True
            st.session_state.user_uid = user.uid
            st.session_state.user_email = user.email
            
            st.success("Login Successful!")
            # Redirect to the main application
            st.switch_page("AIMentor.py")
            
        except auth.UserNotFoundError:
            st.error("Account not found. Please register first.")
        except Exception as e:
            st.error(f"Authentication failed: {e}")
    else:
        st.warning("Please enter both email and password.")

# --- 4. FOOTER ---
st.markdown("<hr style='border-top: 1px solid #E0DEDD; margin-top: 50px;'>", unsafe_allow_html=True)

st.markdown(
    """
    <div style="text-align: center; color: #666;">
        New to the platform? 
        <a href="/register" target="_self" class="footer-link">
            Create an Account 🚀
        </a>
    </div>
    """, 
    unsafe_allow_html=True
)