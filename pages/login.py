import streamlit as st
import firebase_admin
from firebase_admin import credentials, auth, firestore
import requests

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
.title-text { text-align: center; font-weight: 800; color: #1A1A1A; font-size: 2.2rem; }
.subtitle-text { text-align: center; color: #666; margin-bottom: 30px; }
div.stButton > button {
    display: block; margin: 0 auto; width: 100%;
    border-radius: 50px; height: 3.5em;
    background-color: #1A1A1A; color: white;
    border: none; font-weight: 600;
}
div.stButton > button:hover {
    background-color: #333333;
    transform: scale(1.02);
}
.footer-link { color: #1A1A1A; font-weight: 700; text-decoration: none !important; }
</style>
""", unsafe_allow_html=True)

# ------------------ FIREBASE INIT (FIRESTORE ONLY) ------------------
def initialize_firebase():
    if not firebase_admin._apps:
        creds_dict = dict(st.secrets["firebase_credentials"])
        creds_dict["private_key"] = creds_dict["private_key"].replace("\\n", "\n")
        cred = credentials.Certificate(creds_dict)
        firebase_admin.initialize_app(cred)

initialize_firebase()
firestore_db = firestore.client()

# ------------------ FIREBASE SIGN-IN (REST API) ------------------
def firebase_sign_in(email, password):
    api_key = st.secrets["FIREBASE_WEB_API_KEY"]
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={api_key}"

    payload = {
        "email": email,
        "password": password,
        "returnSecureToken": True
    }

    return requests.post(url, json=payload)

# ------------------ UI ------------------
st.markdown("<h1 class='title-text'>🚀 AI Mentor Workspace</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitle-text'>Welcome back! Sign in to access your personalized AI mentor.</p>", unsafe_allow_html=True)

email = st.text_input("📧 Email Address")
password = st.text_input("🔒 Password", type="password")

st.markdown("<br>", unsafe_allow_html=True)

# ------------------ LOGIN LOGIC (FIXED) ------------------
if st.button("Sign In"):
    if email and password:
        try:
            response = firebase_sign_in(email, password)

            if response.status_code == 200:
                data = response.json()
                uid = data["localId"]

                # 🔥 AUTO-HEAL FIRESTORE PROFILE
                user_ref = firestore_db.collection("users").document(uid)
                user_doc = user_ref.get()

                if not user_doc.exists:
                    user_ref.set({
                        "profile": {
                            "name": data["email"].split("@")[0],
                            "email": data["email"],
                            "level": "student",
                            "created_at": firestore.SERVER_TIMESTAMP
                        },
                        "preferences": {
                            "font": "Poppins",
                            "tone": "professional",
                            "theme": "light"
                        }
                    })

                # 🔹 Set session
                st.session_state.logged_in = True
                st.session_state.user_uid = uid
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

# ------------------ FOOTER ------------------
st.markdown("<hr>", unsafe_allow_html=True)
st.markdown("""
<div style="text-align: center; color: #666;">
    New to the platform?
    <a href="/register" target="_self" class="footer-link">
        Create an Account 🚀
    </a>
</div>
""", unsafe_allow_html=True)
