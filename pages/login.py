import streamlit as st
import firebase_admin
from firebase_admin import credentials, auth
import requests

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="AI Workspace Login",
    page_icon="🔑",
    layout="centered"
)

# ---------------- STYLES ----------------
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
div.stButton > button {
    width: 100%;
    border-radius: 50px;
    height: 3.5em;
    background-color: #1A1A1A;
    color: white;
    font-weight: 600;
}
</style>
""", unsafe_allow_html=True)

# ---------------- FIREBASE INIT ----------------
def initialize_firebase():
    if not firebase_admin._apps:
        creds_dict = dict(st.secrets["firebase_credentials"])

        private_key = creds_dict["private_key"]
        private_key = private_key.strip().replace("\r\n", "\n").replace("\r", "\n")
        creds_dict["private_key"] = private_key

        cred = credentials.Certificate(creds_dict)
        firebase_admin.initialize_app(cred)

initialize_firebase()

# ---------------- FIREBASE LOGIN (PASSWORD CHECK) ----------------
def firebase_sign_in(email, password):
    api_key = st.secrets["FIREBASE_WEB_API_KEY"]
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={api_key}"

    payload = {
        "email": email,
        "password": password,
        "returnSecureToken": True
    }

    response = requests.post(url, json=payload)
    return response

# ---------------- UI ----------------
st.markdown("<h1 style='text-align:center;'>🚀 AI Mentor Workspace</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center;color:#666;'>Sign in to continue</p>", unsafe_allow_html=True)

email = st.text_input("📧 Email Address")
password = st.text_input("🔒 Password", type="password")

st.markdown("<br>", unsafe_allow_html=True)

# ---------------- LOGIN LOGIC ----------------
if st.button("Sign In"):
    if email and password:
        try:
            response = firebase_sign_in(email, password)

            if response.status_code == 200:
                data = response.json()

                st.session_state.logged_in = True
                st.session_state.user_uid = data["localId"]
                st.session_state.user_email = data["email"]
                st.session_state.id_token = data["idToken"]

                st.success("Login successful!")
                st.switch_page("AIMentor.py")

            else:
                error = response.json()["error"]["message"]

                if error == "INVALID_PASSWORD":
                    st.error("Incorrect password.")
                elif error == "EMAIL_NOT_FOUND":
                    st.error("Account not found. Please register.")
                elif error == "USER_DISABLED":
                    st.error("User account disabled.")
                else:
                    st.error(error)

        except Exception as e:
            st.error(f"Authentication failed: {e}")
    else:
        st.warning("Please enter email and password.")

# ---------------- FOOTER ----------------
st.markdown("<hr>", unsafe_allow_html=True)
st.markdown(
    "<div style='text-align:center;'>New user? <a href='/register'>Create account</a></div>",
    unsafe_allow_html=True
)
