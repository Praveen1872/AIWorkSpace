import streamlit as st
import firebase_admin
from firebase_admin import credentials, auth, firestore
from google import genai
from google.genai import types
from fpdf import FPDF
from PIL import Image
import io
import os
import streamlit.components.v1 as components
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from llm_router import call_llm
import ollama
st.set_page_config(page_title="AI Workspace", layout="wide")
def initialize_firebase():
    if not firebase_admin._apps:
        cred = credentials.Certificate({
            "type": "service_account",
            "project_id": os.getenv("FIREBASE_PROJECT_ID"),
            "private_key": os.getenv("FIREBASE_PRIVATE_KEY").replace("\\n", "\n"),
            "client_email": os.getenv("FIREBASE_CLIENT_EMAIL"),
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        })
        firebase_admin.initialize_app(cred)
    return firestore.client()

firestore_db = initialize_firebase()

def get_career_profile(user_uid):
    ref = (
        firestore_db
        .collection("users")
        .document(user_uid)
        .collection("career")
        .document("profile")
    )
    doc = ref.get()
    return ref, doc.to_dict() if doc.exists else None
CAREER_STEPS = [
    ("interests", "What are your interests?"),
    ("skills", "What skills do you currently have?"),
    ("academic_background", "What is your academic background?"),
    ("career_goals", "What are your career goals?")
]


API_KEY = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=API_KEY)


MODEL_ID = "gemini-2.5-flash-lite"

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

st.set_page_config(page_title="AI Professional Workspace", layout="wide")
# st.markdown("""
# <style>
#     /* 1. Global App & Font Polish */
#     .stApp { 
#         background-color: #FAF8F7; 
#         color: #1A1A1A; 
#         font-family: 'Inter', sans-serif;
#     }

#     /* 2. Column Alignment Logic */
#     [data-testid="column"] {
#         display: flex;
#         align-items: center;
#         justify-content: center;
#         padding: 0px 5px !important; /* Tightens the gap between buttons */
#     }

#     /* 3. Button Design (Orange Professional Theme) */
#     div.stButton > button { 
#         border-radius: 12px; 
#         background-color: #FF6042; 
#         color: white;
#         border: none;
#         height: 3.2em; /* Slightly taller for better touch/click experience */
#         width: 112%;
#         font-weight: 600;
#         letter-spacing: 0.3px;
#         box-shadow: 0px 2px 4px rgba(0, 0, 0, 0.05); /* Subtle depth */
#         transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
#         justify-content: flex-end; /* aligns buttons to the right */
#         gap: 10px;
#         margin-right: 30px;
#         margin-top: -50px; /* adjust vertical alignment if needed */
#     }

#     /* 4. Interactive Hover & Active States */
#     div.stButton > button:hover {
#         background-color: #FF4520;
#         color: white !important;
#         transform: translateY(-2px); /* Lift effect */
#         box-shadow: 0px 6px 15px rgba(255, 96, 66, 0.3); /* Glowing shadow */
#     }

#     div.stButton > button:active {
#         transform: translateY(0px); /* Pressed effect */
#         box-shadow: 0px 2px 4px rgba(255, 96, 66, 0.2);
#     }

#     /* 5. Custom Horizontal Rule */
#     hr {
#         margin-top: 1rem;
#         margin-bottom: 2rem;
#         border: 0;
#         border-top: 1px solid #E0DEDD;
#     }
# </style>
# """, unsafe_allow_html=True)

# --- 3. HELPER FUNCTIONS ---
def export_last_chat_to_pdf(user_text, ai_text):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt="Research Note Export", ln=True, align='C')
    pdf.ln(10)
    
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, txt="Your Question:", ln=True)
    pdf.set_font("Arial", size=11)
    pdf.multi_cell(0, 8, txt=user_text.encode('latin-1', 'ignore').decode('latin-1'))
    
    pdf.ln(5)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, txt="AI Mentor Response:", ln=True)
    pdf.set_font("Arial", size=11)
    pdf.multi_cell(0, 8, txt=ai_text.encode('latin-1', 'ignore').decode('latin-1'))
    
    return pdf.output(dest='S').encode('latin-1')



# ------------------ SESSION INIT ------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

is_logged_in = st.session_state.logged_in

# ------------------ HEADER ------------------
cols = st.columns([2, 0.7, 0.7, 0.7, 0.9, 1.8, 1], vertical_alignment="center")

with cols[0]:
    st.markdown("<h3 style='margin:0; font-weight:800;'>🚀 AI Workspace</h3>", unsafe_allow_html=True)

# ------------------ AUTHENTICATED NAV ------------------
if is_logged_in:
    with cols[1]:
        if st.button("PPT 🖼️", key="hdr_ppt"):
            st.switch_page("pages/ppt_editor.py")
    with cols[2]:
        if st.button("Word 📝", key="hdr_word"):
            st.switch_page("pages/word_editor.py")
    with cols[3]:
        if st.button("Notes 📓", key="hdr_note"):
            st.switch_page("pages/note.py")
    with cols[4]:
        if st.button("Summarize 📝", key="hdr_sum"):
            st.switch_page("pages/Summarizer.py")
    with cols[6]:
        if st.button("Logout 🚪", key="hdr_out"):
            # Clear ALL auth-related state
            for k in ["logged_in", "user_uid", "user_email"]:
                st.session_state.pop(k, None)
            st.rerun()

# ------------------ NOT LOGGED IN ------------------
else:
    with cols[5]:
        if st.button("Sign In 👤", key="hdr_login"):
            st.switch_page("pages/login.py")
    with cols[6]:
        if st.button("Sign Up 🚀", key="hdr_signup"):
            st.switch_page("pages/register.py")

st.markdown("<hr>", unsafe_allow_html=True)

# ------------------ LANDING PAGE ------------------
if not is_logged_in:
    main_col1, main_col2 = st.columns([1.2, 1], gap="large")

    with main_col1:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown("""
            <h1 style='font-size:3rem;'>👋 Welcome to</h1>
            <h1 style='font-size:4rem; color:#FF6042; margin-top:-20px;'>AI Workspace</h1>
            <p style='font-size:1.25rem; color:#555; margin-top:20px;'>
                Stop wasting hours on tasks AI can handle.<br>
                Your personal academic mentor is ready to help you.
            </p>
        """, unsafe_allow_html=True)

        st.info("💡 Please sign in or sign up to access your AI mentor.")

        if st.button("Unlock Your AI Workspace 👉", use_container_width=True):
            st.switch_page("pages/register.py")

        st.markdown(
            "<p style='text-align:center; '>Powered by <b>Google Gemini AI</b></p>",
            unsafe_allow_html=True
        )

    with main_col2:
        st.image("assets/banner2_desktop.png", use_container_width=True)

    st.stop()

# ------------------ AI MENTOR CORE ------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

user_uid = st.session_state["user_uid"]

career_ref = (
    firestore_db
    .collection("users")
    .document(user_uid)
    .collection("career")
    .document("profile")
)
career_doc = career_ref.get()

career_profile = career_doc.to_dict() if career_doc.exists else None

st.success(f"Welcome back! ({st.session_state.get('user_email')})")
st.write("Ask your AI Mentor anything 👇")



chats_col = (
    firestore_db
    .collection("users")
    .document(user_uid)
    .collection("chats")
)
memory_ref = (
    firestore_db
    .collection("users")
    .document(user_uid)
    .collection("memory")
    .document("summary")
)

memory_doc = memory_ref.get()
long_term_memory = (
    memory_doc.to_dict().get("long_term_summary", "")
    if memory_doc.exists
    else ""
)


def update_long_term_memory(chats_col, memory_ref):
    docs = (
        chats_col
        .order_by("timestamp", direction=firestore.Query.DESCENDING)
        .limit(10)
        .stream()
    )

    recent_chats = []
    for doc in docs:
        d = doc.to_dict()
        recent_chats.append(f"{d['role']}: {d['content']}")

    recent_chats.reverse()
    chat_text = "\n".join(recent_chats)

    old_memory = ""
    old_doc = memory_ref.get()
    if old_doc.exists:
        old_memory = old_doc.to_dict().get("long_term_summary", "")

    prompt = f"""
You are an AI memory summarizer.

Existing memory:
{old_memory}

Recent conversation:
{chat_text}

Update memory with:
- User goals
- Repeated topics
- Preferences
- Important context

Keep it concise (5–7 lines).
"""

    response = client.models.generate_content(
        model=MODEL_ID,
        contents=[prompt]
    )

    memory_ref.set({
        "long_term_summary": response.text,
        "updated_at": firestore.SERVER_TIMESTAMP
    })

if "messages" in st.session_state:
    if len(st.session_state.messages) > 0 and len(st.session_state.messages) % 4 == 0:
        update_long_term_memory(chats_col, memory_ref)




if "messages" not in st.session_state:
    msgs = []
    docs = chats_col.order_by("timestamp").stream()
    for doc in docs:
        msgs.append(doc.to_dict())
    st.session_state.messages = msgs
def retrieve_rag_context(question, user_uid, top_k=5):
    chunks = []

    for dtype in ["ppt", "summary", "word"]:
        items = (
            firestore_db
            .collection("users")
            .document(user_uid)
            .collection("documents")
            .document(dtype)
            .collection("items")
            .stream()
        )

        for item in items:
            for c in item.reference.collection("chunks").stream():
                d = c.to_dict()
                if d.get("text"):
                    chunks.append(d["text"])

    return "\n".join(chunks[:top_k])
def web_search_context(query):
    response = client.models.generate_content(
        model=MODEL_ID,
        contents=[
            f"""
Search the web and provide factual, up-to-date information.

Query:
{query}
"""
        ],
        config=types.GenerateContentConfig(
            tools=[{"google_search": {}}],
            temperature=0.2
        )
    )

    return response.text



def build_career_system_prompt(profile):
    return f"""
You are a PROFESSIONAL CAREER GUIDANCE AI.

User Profile:
Interests: {profile['interests']}
Skills: {profile['skills']}
Academic Background: {profile['academic_background']}
Career Goals: {profile['career_goals']}

STRICT RULES:
- DO NOT answer academic doubts
- DO NOT explain random topics
- ONLY career guidance
- Avoid generic advice

Output format:
1. Personalized Career Suggestions
2. Required Skills (gap analysis)
3. Learning Roadmap (step-by-step)
4. Resources (courses, platforms)
"""

with st.sidebar:
    st.markdown("<h2>🛠️ Workspace</h2>", unsafe_allow_html=True)

    feature = st.radio("Model Context:", ["Doubts Solver", "Career Guide"])
    st.markdown("---")
    deep_dive = st.toggle("Detailed Mode (Deep Dive)", value=False)

    if st.button("🗑️ Reset All Progress"):
        for doc in chats_col.stream():
            doc.reference.delete()
        st.session_state.messages = []
        st.rerun()

def build_recent_chat_context(messages, max_turns=6):
    recent = messages[-max_turns:]
    lines = []
    for m in recent:
        role = "User" if m["role"] == "user" else "Assistant"
        lines.append(f"{role}: {m['content']}")
    return "\n".join(lines)

def extract_career_field(user_input, last_ai_message):
    last_ai_message = last_ai_message.lower()

    if "interest" in last_ai_message:
        return "interests", user_input

    if "skill" in last_ai_message:
        return "skills", user_input

    if "academic" in last_ai_message or "education" in last_ai_message:
        return "academic_background", user_input

    if "career goal" in last_ai_message or "goal" in last_ai_message:
        return "career_goals", user_input

    return None, None

# ================= CAREER GUIDE PROMPTS =================

CAREER_INTAKE_PROMPT = """
You are a Career Guidance AI.

Your task:
Ask the user ONLY these questions, one by one:
1. Interests
2. Skills
3. Academic Background
4. Career Goals

Rules:
- Ask ONE question at a time
- Do NOT give advice yet
- Do NOT answer doubts
- Keep questions short and clear
"""

chat_display = st.container()
with chat_display:
    for i, message in enumerate(st.session_state.messages):
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if message["role"] == "assistant" and i > 0:
                user_q = st.session_state.messages[i-1]["content"]
                pdf_bytes = export_last_chat_to_pdf(user_q, message["content"])
                st.download_button("📝 Export as PDF", pdf_bytes, f"note_{i}.pdf", key=f"dl_{i}")


with st.expander("📷 Analysis Tools (Upload Images/Diagrams)", expanded=False):
    up_img = st.file_uploader("Upload visual data for the AI to analyze", type=["jpg", "jpeg", "png"])
    if up_img:
        st.image(up_img, caption="Image Attachment Ready", width=300)
if prompt := st.chat_input(f"Ask your {feature}..."):

    # ---------------- STORE USER MESSAGE ----------------
    st.session_state.messages.append({
        "role": "user",
        "content": prompt
    })

    chats_col.add({
        "role": "user",
        "content": prompt,
        "timestamp": firestore.SERVER_TIMESTAMP
    })

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):

            # ================= CAREER GUIDE MODE =================
            if feature == "Career Guide":

                career_ref, career_profile = get_career_profile(user_uid)

                # 🔐 Initialize profile
                if not career_profile:
                    career_profile = {
                        "career_step": 0,
                        "completed": False
                    }
                    career_ref.set(career_profile)

                step = career_profile.get("career_step", 0)

                # 🟢 SAVE PREVIOUS ANSWER
                if step > 0 and step <= len(CAREER_STEPS):
                    prev_field, _ = CAREER_STEPS[step - 1]
                    career_profile[prev_field] = prompt

                # 🟢 INTAKE PHASE
                if step < len(CAREER_STEPS):
                    career_profile["career_step"] = step + 1
                    career_profile["updated_at"] = firestore.SERVER_TIMESTAMP
                    career_ref.set(career_profile, merge=True)

                    _, next_question = CAREER_STEPS[step]
                    final_answer = next_question

                # 🟢 GUIDANCE PHASE
                else:
                    career_profile["completed"] = True
                    career_ref.set(career_profile, merge=True)

                    SYSTEM_PROMPT = build_career_system_prompt(career_profile)

                    response = client.models.generate_content(
                        model=MODEL_ID,
                        contents=[prompt],
                        config=types.GenerateContentConfig(
                            system_instruction=SYSTEM_PROMPT
                        )
                    )
                    final_answer = response.text

            # ================= DOUBT SOLVER MODE =================
            else:
                recent_chat_context = build_recent_chat_context(
                    st.session_state.messages, 6
                )

                rag_context = retrieve_rag_context(prompt, user_uid)
                if not rag_context.strip():
                    rag_context = web_search_context(prompt)

                SYSTEM_PROMPT = f"""
You are an Elite Academic Mentor AI.

RECENT CONVERSATION:
{recent_chat_context}

LONG-TERM USER MEMORY:
{long_term_memory}

RETRIEVED CONTEXT:
{rag_context}

Rules:
- Resolve references using conversation
- Be accurate and concise
"""

                try:
                    response = client.models.generate_content(
                        model=MODEL_ID,
                        contents=[prompt],
                        config=types.GenerateContentConfig(
                            system_instruction=SYSTEM_PROMPT
                        )
                    )
                    final_answer = response.text
                except:
                    ollama_response = ollama.chat(
                        model="llama3",
                        messages=[
                            {"role": "system", "content": SYSTEM_PROMPT},
                            {"role": "user", "content": prompt}
                        ]
                    )
                    final_answer = ollama_response["message"]["content"]

            # ---------------- DISPLAY + SAVE AI RESPONSE ----------------
            st.markdown(final_answer)

            st.session_state.messages.append({
                "role": "assistant",
                "content": final_answer
            })

            chats_col.add({
                "role": "assistant",
                "content": final_answer,
                "timestamp": firestore.SERVER_TIMESTAMP
            })

            st.rerun()
with st.sidebar:
    if feature == "Career Guide":

        career_ref, career_profile = get_career_profile(user_uid)

        if career_profile and career_profile.get("completed"):

            st.markdown("### ✏️ Edit Career Profile")

            interests = st.text_area(
                "Interests",
                career_profile.get("interests", "")
            )

            skills = st.text_area(
                "Skills",
                career_profile.get("skills", "")
            )

            academic_background = st.text_area(
                "Academic Background",
                career_profile.get("academic_background", "")
            )

            career_goals = st.text_area(
                "Career Goals",
                career_profile.get("career_goals", "")
            )

            if st.button("💾 Save Changes"):
                career_ref.set({
                    "interests": interests,
                    "skills": skills,
                    "academic_background": academic_background,
                    "career_goals": career_goals,
                    "completed": True,
                    "updated_at": firestore.SERVER_TIMESTAMP
                }, merge=True)

                st.success("Career profile updated successfully ✅")
                st.rerun()
