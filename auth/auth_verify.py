import streamlit as st
from firebase_admin import auth
from services.firebase_init import initialize_firebase

db = initialize_firebase()

st.set_page_config(page_title="Auth Verify", layout="centered")

token = st.query_params.get("token")

if not token:
    st.error("Invalid login attempt.")
    st.stop()

try:
    decoded = auth.verify_id_token(token)

    uid = decoded["uid"]
    email = decoded["email"]
    name = decoded.get("name", email.split("@")[0])

    # ---- Firestore auto profile ----
    user_ref = db.collection("users").document(uid)
    if not user_ref.get().exists:
        user_ref.set({
            "profile": {
                "name": name,
                "email": email,
                "level": "student"
            }
        })

    # ---- Streamlit session ----
    st.session_state.logged_in = True
    st.session_state.user_uid = uid
    st.session_state.user_email = email

    st.success("Login successful!")
    st.switch_page("AIMentor.py")

except Exception as e:
    st.error(f"Authentication failed: {e}")
