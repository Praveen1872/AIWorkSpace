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
if not firebase_admin._apps:
    try:
        if "firebase_credentials" in st.secrets:
            creds_dict = dict(st.secrets["firebase_credentials"])
            
            # 1. Clean the key of all literal escapings and existing headers
            raw_key = creds_dict["private_key"]
            
            # Remove literal \n, headers, footers, and quotes to get the raw base64 string
            clean_key = (
                raw_key.replace("\\n", "\n")
                .replace("-----BEGIN PRIVATE KEY-----", "")
                .replace("-----END PRIVATE KEY-----", "")
                .strip()
                .strip('"')
                .strip("'")
            )
            
            # 2. Re-wrap the key with proper, physical newlines
            # The library MUST see the header on its own line.
            formatted_key = f"-----BEGIN PRIVATE KEY-----\n{clean_key}\n-----END PRIVATE KEY-----\n"
            
            creds_dict["private_key"] = formatted_key
            
            # 3. Initialize using the repaired dictionary
            cred = credentials.Certificate(creds_dict)
            firebase_admin.initialize_app(cred, {
                'databaseURL': 'https://workspace-1f516-default-rtdb.asia-southeast1.firebasedatabase.app/'
            })
        else:
            st.error("Credentials not found in Streamlit Secrets.")
    except Exception as e:
        # This will now show us exactly what the library is seeing if it fails
        st.error(f"PEM Reconstruction Failed: {e}")

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