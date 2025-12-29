import streamlit as st
import firebase_admin
from firebase_admin import credentials, auth
import requests


st.set_page_config(
    page_title="AI Workspace Login",
    page_icon="🔑",
    layout="centered"
)

st.markdown(
    """
    <div style="
        text-align: center;
        margin-top: 30px;
        font-size: 0.95rem;
        color: #555;
    ">
        New user?
        <a href="/register" style="
            margin-left: 6px;
            color: #1A1A1A;
            font-weight: 700;
            text-decoration: none;
            border-bottom: 2px solid transparent;
            transition: all 0.3s ease;
        "
        onmouseover="this.style.borderBottom='2px solid #1A1A1A'"
        onmouseout="this.style.borderBottom='2px solid transparent'"
        >
            Create account →
        </a>
    </div>
    """,
    unsafe_allow_html=True
)



def initialize_firebase():
    if not firebase_admin._apps:
        creds_dict = dict(st.secrets["firebase_credentials"])

        private_key = creds_dict["private_key"]
        private_key = private_key.strip().replace("\r\n", "\n").replace("\r", "\n")
        creds_dict["private_key"] = private_key

        cred = credentials.Certificate(creds_dict)
        firebase_admin.initialize_app(cred)

initialize_firebase()


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


st.markdown("<h1 style='text-align:center;'>🚀 AI Mentor Workspace</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitle-text'>Welcome back! Please sign in to access your personal AI researcher.</p>", unsafe_allow_html=True)
email = st.text_input("📧 Email Address")
password = st.text_input("🔒 Password", type="password")

st.markdown("<br>", unsafe_allow_html=True)


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


st.markdown("<hr>", unsafe_allow_html=True)
st.markdown( """ <div style="text-align: center; color: #666;"> New to the platform? <a href="/register" target="_self" class="footer-link"> Create an Account 🚀 </a> </div> """, unsafe_allow_html=True )
