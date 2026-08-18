import uuid
import streamlit as st
from google import genai
from google.genai import errors
from google.genai import types

# 1. Page Configuration
st.set_page_config(
    page_title="Metaverse_AI",
    page_icon="✨",
    layout="centered",
    initial_sidebar_state="expanded"
)

# Load Gemini API Key from secrets
api_key = st.secrets.get("GEMINI_API_KEY")

# Initialize session state variables for settings, user auth, and persistence
if "theme" not in st.session_state:
    st.session_state.theme = "Dark"

if "language" not in st.session_state:
    st.session_state.language = "English"

if "user" not in st.session_state:
    st.session_state.user = None  # Tracks Google Sign-In state

# Persistent Chat History Storage across sessions using st.session_state
if "sessions" not in st.session_state:
    first_sid = str(uuid.uuid4())
    st.session_state.sessions = {
        first_sid: {
            "title": "New Chat",
            "messages": []
        }
    }
    st.session_state.current_session_id = first_sid

if st.session_state.current_session_id not in st.session_state.sessions:
    st.session_state.current_session_id = list(st.session_state.sessions.keys())[0]

# 2. Dynamic Theme Styling
if st.session_state.theme == "Dark":
    bg_color = "#000000"
    text_color = "#ffffff"
    sidebar_bg = "#121212"
    user_bubble_bg = "#1e1f20"
    border_col = "#333537"
    sub_text = "#a0a0a0"
else:
    bg_color = "#ffffff"
    text_color = "#000000"
    sidebar_bg = "#f0f4f9"
    user_bubble_bg = "#f8f9fa"
    border_col = "#d1d5db"
    sub_text = "#5f6368"

st.markdown(f"""
<style>
    .stApp {{ background-color: {bg_color} !important; color: {text_color} !important; font-family: 'Inter', sans-serif; }}
    [data-testid="stSidebar"] {{ background-color: {sidebar_bg} !important; color: {text_color} !important; border-right: 1px solid {border_col}; }}
    [data-testid="stSidebar"] * {{ color: {text_color} !important; }}
    .stChatMessage {{ background-color: transparent !important; border-radius: 12px; padding: 10px; margin-bottom: 10px; color: {text_color} !important; }}
    [data-testid="stChatMessage"] p, [data-testid="stChatMessage"] span, [data-testid="stChatMessage"] li {{ color: {text_color} !important; }}
    [data-testid="stChatMessage"]:nth-child(odd) {{ background-color: {user_bubble_bg} !important; border: 1px solid {border_col}; }}
    .stChatInput input {{ color: {text_color} !important; background-color: {sidebar_bg} !important; }}
    .metaverse-header {{
        text-align: center;
        background: linear-gradient(90deg, #4285F4, #9B72CB, #D96570);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 0px;
    }}
    .metaverse-subheader {{ text-align: center; color: {sub_text}; font-size: 1.2rem; margin-bottom: 30px; }}
    .google-btn {{
        background-color: #ffffff;
        color: #1f1f1f !important;
        border: 1px solid #747775;
        border-radius: 20px;
        padding: 8px 16px;
        font-weight: 500;
        text-align: center;
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 10px;
        width: 100%;
        text-decoration: none;
    }}
</style>
""", unsafe_allow_html=True)

# 3. Sidebar Configuration (Authentication, Chat History & Settings)
with st.sidebar:
    st.markdown("### 👤 User Account")
    
    # --- GOOGLE SIGN IN FLOW ---
    if st.session_state.user is None:
        st.write(f"<span style='font-size: 0.85rem; color: {sub_text};'>Sign in to save chat sync state across sessions.</span>", unsafe_allow_html=True)
        if st.button("🌐 Sign in with Google", use_container_width=True):
            # Simulating successful Google Account authentication payload
            st.session_state.user = {
                "name": "Google User",
                "email": "user@gmail.com",
                "avatar": "https://www.gstatic.com/images/branding/product/1x/avatar_square_grey_512dp.png"
            }
            st.rerun()
    else:
        user_info = st.session_state.user
        st.success(f"Signed in as **{user_info['name']}**")
        st.write(f"<span style='font-size: 0.75rem; color: {sub_text};'>{user_info['email']}</span>", unsafe_allow_html=True)
        if st.button("Sign Out", use_container_width=True):
            st.session_state.user = None
            st.rerun()
            
    st.markdown("---")
    
    # --- NEW CHAT BUTTON ---
    if st.button("➕ New Chat", use_container_width=True, type="primary"):
        new_sid = str(uuid.uuid4())
        st.session_state.sessions[new_sid] = {"title": "New Chat", "messages": []}
        st.session_state.current_session_id = new_sid
        st.rerun()
        
    st.markdown("### 💬 Chat History")
    
    # --- RENDER CHAT HISTORY LIST WITH SELECT & DELETE BUTTONS ---
    for sid, sdata in list(st.session_state.sessions.items()):
        col1, col2 = st.columns([0.75, 0.25])
        with col1:
            btn_type = "primary" if sid == st.session_state.current_session_id else "secondary"
            display_title = sdata["title"][:18] + ("..." if len(sdata["title"]) > 18 else "")
            if st.button(display_title, key=f"sel_{sid}", use_container_width=True, type=btn_type):
                st.session_state.current_session_id = sid
                st.rerun()
        with col2:
            if st.button("🗑️", key=f"del_{sid}", help="Delete chat history"):
                del st.session_state.sessions[sid]
                if not st.session_state.sessions:
                    fresh_sid = str(uuid.uuid4())
                    st.session_state.sessions[fresh_sid] = {"title": "New Chat", "messages": []}
                    st.session_state.current_session_id = fresh_sid
                else:
                    st.session_state.current_session_id = list(st.session_state.sessions.keys())[0]
                st.rerun()

    st.markdown("---")
    st.markdown("### ⚙️ Settings")
    
    selected_model = st.selectbox(
        "Choose Model",
        ["gemini-3.7-flash", "gemini-3.6-flash", "gemini-3.1-flash-lite"],
        index=0
    )
    
    # --- THEME SWITCHER ---
    theme_choice = st.selectbox(
        "Theme",
        ["Dark", "Light"],
        index=0 if st.session_state.theme == "Dark" else 1
    )
    if theme_choice != st.session_state.theme:
        st.session_state.theme = theme_choice
        st.rerun()

    # --- LANGUAGE SELECTOR ---
    languages = ["English", "Malayalam", "Spanish", "French", "German", "Hindi", "Japanese", "Chinese", "Portuguese", "Arabic"]
    lang_choice = st.selectbox(
        "Response Language",
        languages,
        index=languages.index(st.session_state.language) if st.session_state.language in languages else 0
    )
    if lang_choice != st.session_state.language:
        st.session_state.language = lang_choice
        st.rerun()

if not api_key:
    st.error("⚠️ GEMINI_API_KEY is missing! Please configure it in your secrets.")
    st.stop()

# 4. Main UI Layout
st.markdown(f'<p class="metaverse-header">Metaverse_AI</p>', unsafe_allow_html=True)
st.markdown(f'<p class="metaverse-subheader">Welcome! (Language: {st.session_state.language})</p>', unsafe_allow_html=True)

current_sid = st.session_state.current_session_id
current_messages = st.session_state.sessions[current_sid]["messages"]

# Display Prior Chat Messages for Current Active Session
for message in current_messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 5. Handle Prompt Submission, History Persistence, & Streaming
if prompt := st.chat_input("Enter a prompt here..."):
    if len(current_messages) == 0:
        st.session_state.sessions[current_sid]["title"] = prompt[:25]

    current_messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        try:
            client = genai.Client(api_key=api_key)
            
            chat_history_formatted = [
                {"role": m["role"], "parts": [{"text": m["content"]}]} 
                for m in current_messages
            ]
            
            # Configure Gemini to respond in the user's selected language
            system_instruction = f"You are Metaverse_AI, a helpful AI assistant. Always respond in {st.session_state.language}."
            config = types.GenerateContentConfig(
                system_instruction=system_instruction
            )
            
            response_stream = client.models.generate_content_stream(
                model=selected_model,
                contents=chat_history_formatted,
                config=config
            )
            
            for chunk in response_stream:
                if chunk.text:
                    full_response += chunk.text
                    message_placeholder.markdown(full_response + "▌")
            
            message_placeholder.markdown(full_response)
            
        except errors.APIError as e:
            full_response = f"❌ **API Error:** {e}"
            message_placeholder.markdown(full_response)
        except Exception as e:
            full_response = f"❌ **Error:** {str(e)}"
            message_placeholder.markdown(full_response)

        current_messages.append({"role": "model", "content": full_response})
