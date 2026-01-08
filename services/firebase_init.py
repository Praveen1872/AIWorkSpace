import firebase_admin
from firebase_admin import credentials, auth, firestore
import streamlit as st

def initialize_firebase():
    if not firebase_admin._apps:
        creds = dict(st.secrets["firebase_credentials"])
        creds["private_key"] = creds["private_key"].replace("\\n", "\n")
        cred = credentials.Certificate(creds)
        firebase_admin.initialize_app(cred)

    return firestore.client()
