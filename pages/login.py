import streamlit as st
import firebase_admin
from firebase_admin import auth


st.set_page_config(page_title="AI Workspace Login", page_icon="🔑", layout="centered")

st.markdown("""
<style>
    /* Center the entire login block */
    .stApp {
        background-color: #FAF8F7;
    }
    
    /* Create a card effect on the second div of the vertical block */
    [data-testid="stVerticalBlock"] > div:nth-child(2) {
        background-color: white;
        padding: 40px;
        border-radius: 25px;
        border: 1px solid #E0DEDD;
        box-shadow: 0px 4px 20px rgba(0,0,0,0.03);
    }

    /* Style titles */
    .title-text {
        text-align: center;
        font-weight: 800;
        color: #1A1A1A;
        font-size: 2.2rem;
        margin-bottom: 0px;
    }
    .subtitle-text {
        text-align: center;
        color: #666;
        margin-bottom: 30px;
    }

    /* Primary Action Button (Sign In) */
    div.stButton > button {
        display: block;
        margin: 0 auto;
        width: 100%;
        border-radius: 50px;
        height: 3.2em;
        background-color: #1A1A1A;
        color: white;
        border: none;
        font-weight: 600;
        transition: 0.3s ease;
    }
    
    div.stButton > button {
        display: block;
        margin: -20px 30px -30px;
        width: 100%;
        border-radius: 50px;
        
        
        padding: 10px 24px; 
        height: 3.5em; 
        
        background-color: #1A1A1A;
        color: white;
        border: none;
        font-weight: 600;
        font-size: 16px;
        transition: all 0.3s ease;
    }
    /* Clean Hyperlink Style */
    .footer-link {
        color: #1A1A1A;
        font-weight: 700;
        text-decoration: none !important;
        border-bottom: 1px solid transparent;
        transition: 0.3s;
            color: #1A1A1A; font-weight: 700; text-decoration: none !important; border: none;
    }
    .footer-link:hover {
        border-bottom: 1px solid #1A1A1A;
    }
</style>
""", unsafe_allow_html=True)


st.markdown("<h1 class='title-text'>🚀 AI Mentor Workspace</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitle-text'>Welcome back! Please sign in to access your personal AI researcher.</p>", unsafe_allow_html=True)


email = st.text_input("📧 Email Address", placeholder="name@example.com")
password = st.text_input("🔒 Password", type="password", placeholder="Enter your Password")

st.markdown("<br>", unsafe_allow_html=True)


col1, col2, col3 = st.columns([1, 1.2, 1])
with col2:
    if st.button("Sign In"):
        if email and password:
            try:
                user = auth.get_user_by_email(email)
                st.session_state.logged_in = True
                st.session_state.user_uid = user.uid
                st.success("Login Successful!")
                st.switch_page("AIMentor.py")
            except Exception:
                st.error("Account not found. Please register.")
        else:
            st.warning("Please fill in all fields.")


st.markdown("<hr style='border-top: 1px solid #E0DEDD; margin-top: 50px;'>", unsafe_allow_html=True)

st.markdown(
    """
    <div style="text-align: center; color: #666; font-family: sans-serif;">
        New to the platform? 
        <a href="/register" target="_self" class="footer-link">
            Create an Account 🚀
        </a>
    </div>
    """, 
    unsafe_allow_html=True
)