import uuid
import streamlit as st
from google import genai
from google.genai import errors
from google.genai import types

# 1. Page Configuration & Adaptive Layout
st.set_page_config(
    page_title="Gemini",
    page_icon="✨",
    layout="centered",
    initial_sidebar_state="auto"
)

st.markdown("""
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
""", unsafe_allow_html=True)

api_key = st.secrets.get("GEMINI_API_KEY")

try:
    is_logged_in = getattr(st.user, "is_logged_in", False)
    user_email = getattr(st.user, "email", "default_guest_user")
    user_display_name = getattr(st.user, "name", "User")
except Exception:
    is_logged_in = False
    user_email = "default_guest_user"
    user_display_name = "User"

storage_key = f"gemini_master_v3_sessions_{user_email.replace('@', '_at_').replace('.', '_')}"
prefs_storage_key = f"gemini_master_v3_prefs_{user_email.replace('@', '_at_').replace('.', '_')}"
memory_storage_key = f"gemini_master_v3_memory_{user_email.replace('@', '_at_').replace('.', '_')}"

if prefs_storage_key not in st.session_state:
    st.session_state[prefs_storage_key] = {
        "selected_model": "gemini-2.5-flash",
        "lang_choice": "English",
        "use_search": True
    }

if memory_storage_key not in st.session_state:
    st.session_state[memory_storage_key] = [
        "Creator and Master Architect: Abyan Muhammed",
        "Creator Directive: Only mention 'Made by Abyan Muhammed' when explicitly greeted ('hello', 'hi') or when asked about your creator.",
        "User Session Profile: " + user_display_name
    ]

if storage_key not in st.session_state:
    first_sid = str(uuid.uuid4())
    st.session_state[storage_key] = {
        first_sid: {
            "title": "New Chat",
            "messages": []
        }
    }

if f"{storage_key}_current_sid" not in st.session_state:
    st.session_state[f"{storage_key}_current_sid"] = list(st.session_state[storage_key].keys())[0]

current_sid = st.session_state[f"{storage_key}_current_sid"]
if current_sid not in st.session_state[storage_key]:
    st.session_state[f"{storage_key}_current_sid"] = list(st.session_state[storage_key].keys())[0]
    current_sid = st.session_state[f"{storage_key}_current_sid"]

current_session_data = st.session_state[storage_key][current_sid]

if "show_settings_modal" not in st.session_state:
    st.session_state["show_settings_modal"] = False

if "show_brain_modal" not in st.session_state:
    st.session_state["show_brain_modal"] = False

# 2. OFFICIAL GOOGLE GEMINI CSS STYLING
theme_css = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Google+Sans:wght@400;500;700&display=swap');

    html, body, [data-testid="stAppViewContainer"], [data-testid="stMain"] {
        background-color: #131314 !important;
        color: #e3e3e3 !important;
        font-family: 'Google Sans', sans-serif !important;
        width: 100% !important;
    }

    .block-container {
        max-width: 820px !important;
        padding-top: 2.5rem !important;
        padding-bottom: 7.5rem !important;
        padding-left: 2rem !important;
        padding-right: 2rem !important;
        margin: 0 auto !important;
    }

    [data-testid="stSidebar"] {
        background-color: #1e1f20 !important;
        border-right: 1px solid rgba(255, 255, 255, 0.08) !important;
    }

    [data-testid="stSidebar"] * {
        color: #e3e3e3 !important;
    }

    .gemini-header {
        text-align: left;
        margin-bottom: 30px;
        padding-left: 8px;
    }

    .gemini-greeting {
        font-family: 'Google Sans', sans-serif;
        font-size: 2.3rem;
        font-weight: 500;
        background: linear-gradient(90deg, #4285f4, #9b72cb, #d96570);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 4px;
        letter-spacing: -0.5px;
    }

    .gemini-subgreeting {
        font-size: 2.3rem;
        font-weight: 400;
        color: #444746;
        margin-bottom: 8px;
        letter-spacing: -0.5px;
    }

    .gemini-auth-card {
        background: #1e1f20;
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 24px;
        padding: 44px 32px;
        text-align: center;
        max-width: 440px;
        margin: 40px auto;
        box-shadow: 0 12px 32px rgba(0, 0, 0, 0.5);
    }

    .gemini-auth-icon {
        font-size: 2rem;
        margin-bottom: 16px;
        display: inline-block;
        padding: 14px;
        background: rgba(66, 133, 244, 0.12);
        border-radius: 18px;
        color: #8ab4f8;
    }

    .stChatMessage {
        background: #1e1f20 !important;
        border: 1px solid rgba(255, 255, 255, 0.06) !important;
        border-radius: 20px !important;
        padding: 18px 24px !important;
        margin-bottom: 16px !important;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2) !important;
    }

    .stChatMessage p, .stChatMessage span, .stChatMessage div {
        color: #e3e3e3 !important;
        font-size: 0.95rem !important;
        line-height: 1.7 !important;
    }

    .stButton button {
        border-radius: 100px !important;
        font-family: 'Google Sans', sans-serif !important;
        font-weight: 500 !important;
        font-size: 0.82rem !important;
        letter-spacing: 0.3px !important;
        border: 1px solid rgba(255, 255, 255, 0.12) !important;
        background: #28292a !important;
        color: #e3e3e3 !important;
        padding: 10px 22px !important;
        width: 100% !important;
        box-shadow: none !important;
        transition: background 0.2s ease, border-color 0.2s ease !important;
    }

    .stButton button:hover {
        background: #333435 !important;
        border-color: rgba(255, 255, 255, 0.3) !important;
        color: #ffffff !important;
    }

    [data-testid="stChatInput"] textarea {
        background: #1e1f20 !important;
        color: #e3e3e3 !important;
        border: 1px solid rgba(255, 255, 255, 0.12) !important;
        border-radius: 28px !important;
        font-family: 'Google Sans', sans-serif !important;
        font-size: 0.95rem !important;
        padding: 16px 22px !important;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.4) !important;
    }

    .sidebar-signature {
        text-align: center;
        font-family: 'Google Sans', sans-serif;
        font-size: 0.65rem;
        color: #8ab4f8;
        letter-spacing: 1.5px;
        padding: 14px 4px;
        margin-top: 24px;
        margin-bottom: 24px;
        border-top: 1px solid rgba(255, 255, 255, 0.08);
        border-bottom: 1px solid rgba(255, 255, 255, 0.08);
        text-transform: uppercase;
        background: rgba(66, 133, 244, 0.05);
        font-weight: 500;
    }

    .gemini-badge {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        padding: 6px 14px;
        margin-bottom: 12px;
        background: rgba(66, 133, 244, 0.1);
        border: 1px solid rgba(66, 133, 244, 0.25);
        border-radius: 12px;
        font-family: 'Google Sans', sans-serif;
        font-size: 0.68rem;
        color: #8ab4f8;
        font-weight: 500;
    }
</style>
"""

st.markdown(theme_css, unsafe_allow_html=True)

# 3. Sidebar Panel
with st.sidebar:
    st.markdown("### ✨ Gemini")
    
    if not is_logged_in:
        st.write("<span style='font-size: 0.82rem; color: #c4c7c5;'>Sign in to start your session.</span>", unsafe_allow_html=True)
        st.button("Sign in with Google", on_click=st.login, use_container_width=True)
    else:
        st.success(f"**{user_display_name}**")
        st.write(f"<span style='font-size: 0.76rem; color: #8ab4f8;'>{user_email}</span>", unsafe_allow_html=True)
        st.button("Sign Out", on_click=st.logout, use_container_width=True)
            
        st.markdown("---")
        
        show_settings = st.checkbox("⚙️ System Preferences", value=st.session_state["show_settings_modal"])
        if show_settings != st.session_state["show_settings_modal"]:
            st.session_state["show_settings_modal"] = show_settings
            st.rerun()

        show_brain = st.checkbox("🧠 Memory Vault", value=st.session_state["show_brain_modal"])
        if show_brain != st.session_state["show_brain_modal"]:
            st.session_state["show_brain_modal"] = show_brain
            st.rerun()

        st.markdown("---")
        
        if st.button("➕ New Chat", use_container_width=True):
            new_sid = str(uuid.uuid4())
            st.session_state[storage_key][new_sid] = {
                "title": "New Chat",
                "messages": []
            }
            st.session_state[f"{storage_key}_current_sid"] = new_sid
            st.rerun()
            
        st.markdown("### Recent")
        
        for sid, sdata in list(st.session_state[storage_key].items()):
            col1, col2 = st.columns([0.75, 0.25])
            with col1:
                display_title = sdata["title"][:15] + ("..." if len(sdata["title"]) > 15 else "")
                if st.button(display_title, key=f"sel_{sid}", use_container_width=True):
                    st.session_state[f"{storage_key}_current_sid"] = sid
                    st.rerun()
            with col2:
                if st.button("✕", key=f"del_{sid}", use_container_width=True):
                    del st.session_state[storage_key][sid]
                    if not st.session_state[storage_key]:
                        fresh_sid = str(uuid.uuid4())
                        st.session_state[storage_key][fresh_sid] = {"title": "New Chat", "messages": []}
                        st.session_state[f"{storage_key}_current_sid"] = fresh_sid
                    else:
                        st.session_state[f"{storage_key}_current_sid"] = list(st.session_state[storage_key].keys())[0]
                    st.rerun()

    st.markdown(
        """<div class="sidebar-signature">
        MADE BY ABYAN MUHAMMED
        </div>""",
        unsafe_allow_html=True
    )

if not api_key:
    st.error("⚠️ GEMINI_API_KEY configuration missing in `.streamlit/secrets.toml`.")
    st.stop()

selected_model = st.session_state[prefs_storage_key].get("selected_model", "gemini-2.5-flash")
lang_choice = st.session_state[prefs_storage_key].get("lang_choice", "English")
use_search = st.session_state[prefs_storage_key].get("use_search", True)

# 4. Modals
if is_logged_in and st.session_state.get("show_settings_modal", False):
    with st.container():
        st.markdown("#### System Preferences")
        models_list = ["gemini-2.5-flash", "gemini-2.5-pro", "gemini-3.5-flash-lite"]
        model_index = models_list.index(selected_model) if selected_model in models_list else 0
        selected_model_input = st.selectbox("AI Model Core", models_list, index=model_index)

        languages = ["English", "Malayalam", "Hindi", "Spanish", "French", "German", "Japanese", "Chinese", "Arabic"]
        lang_index = languages.index(lang_choice) if lang_choice in languages else 0
        lang_choice_input = st.selectbox("Response Language", languages, index=lang_index)
        
        use_search_input = st.checkbox("Enable Google Search Grounding", value=use_search)
        
        col_s1, col_s2 = st.columns(2)
        with col_s1:
            if st.button("Apply Changes", use_container_width=True):
                st.session_state[prefs_storage_key]["selected_model"] = selected_model_input
                st.session_state[prefs_storage_key]["lang_choice"] = lang_choice_input
                st.session_state[prefs_storage_key]["use_search"] = use_search_input
                st.session_state["show_settings_modal"] = False
                st.rerun()
        with col_s2:
            if st.button("Cancel", use_container_width=True):
                st.session_state["show_settings_modal"] = False
                st.rerun()
        st.markdown("---")

if is_logged_in and st.session_state.get("show_brain_modal", False):
    with st.container():
        st.markdown("#### Memory Vault")
        memory_list = st.session_state[memory_storage_key]
        for idx, mem in enumerate(memory_list):
            col_m1, col_m2 = st.columns([0.82, 0.18])
            with col_m1:
                st.code(mem, language="text")
            with col_m2:
                if st.button("✕", key=f"del_mem_{idx}", use_container_width=True):
                    memory_list.pop(idx)
                    st.rerun()

        if st.button("Close Vault", use_container_width=True):
            st.session_state["show_brain_modal"] = False
            st.rerun()
        st.markdown("---")

selected_model = st.session_state[prefs_storage_key].get("selected_model", "gemini-2.5-flash")
lang_choice = st.session_state[prefs_storage_key].get("lang_choice", "English")
use_search = st.session_state[prefs_storage_key].get("use_search", True)

# 5. Main Content Area
if is_logged_in and len(current_session_data["messages"]) == 0:
    st.markdown(f"""
        <div class="gemini-header">
            <div class="gemini-greeting">Hello, {user_display_name}</div>
            <div class="gemini-subgreeting">How can I help you today?</div>
        </div>
    """, unsafe_allow_html=True)
else:
    st.markdown(f"""
        <div class="gemini-header">
            <div class="gemini-greeting" style="font-size: 1.8rem;">Gemini</div>
            <div style="font-size: 0.75rem; color: #8e918f; text-transform: uppercase; letter-spacing: 1px;">{selected_model} &bull; {lang_choice}</div>
        </div>
    """, unsafe_allow_html=True)

if not is_logged_in:
    st.markdown("""
        <div class="gemini-auth-card">
            <div class="gemini-auth-icon">✨</div>
            <div style="font-size: 1.25rem; font-weight: 500; color: #e3e3e3; margin-bottom: 8px;">Welcome to Gemini</div>
            <div style="font-size: 0.9rem; color: #c4c7c5; line-height: 1.6; margin-bottom: 28px;">
                Sign in with your Google account to start chatting with Gemini.
            </div>
    """, unsafe_allow_html=True)
    
    col_b1, col_b2, col_b3 = st.columns([1, 2, 1])
    with col_b2:
        st.button("Sign in with Google", on_click=st.login, use_container_width=True)
        
    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

current_messages = current_session_data["messages"]

for message in current_messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "file_name" in message:
            st.markdown(f"<span style='font-size:0.75rem; color:#8ab4f8;'>📎 Attached: {message['file_name']}</span>", unsafe_allow_html=True)

# 6. Optional File Upload Feature
uploaded_file = st.file_uploader("Upload an image, document, or file to share with Gemini", type=["png", "jpg", "jpeg", "pdf", "txt", "csv"])

# 7. Chat Execution Pipeline
prompt = st.chat_input("Enter a prompt here")

if prompt or uploaded_file:
    prompt_text = prompt if prompt else "Analyze this uploaded file."
    if len(current_messages) == 0:
        current_session_data["title"] = prompt_text[:16]

    user_msg_data = {"role": "user", "content": prompt_text}
    if uploaded_file:
        user_msg_data["file_name"] = uploaded_file.name

    current_messages.append(user_msg_data)
    with st.chat_message("user"):
        st.markdown(prompt_text)
        if uploaded_file:
            st.markdown(f"<span style='font-size:0.75rem; color:#8ab4f8;'>📎 Attached: {uploaded_file.name}</span>", unsafe_allow_html=True)

    with st.chat_message("assistant"):
        loader_placeholder = st.empty()
        loader_placeholder.markdown("""
            <div class="gemini-badge">✨ Gemini is thinking...</div>
        """, unsafe_allow_html=True)
        
        message_placeholder = st.empty()
        full_response = ""
        
        try:
            client = genai.Client(api_key=api_key)
            
            memories_str = "\n".join([f"- {m}" for m in st.session_state[memory_storage_key]])
            system_instruction = (
                f"You are Gemini, built by Google. Respond in {lang_choice}.\n"
                f"USER PROFILE:\n- Name: {user_display_name}\n- Email: {user_email}\n\n"
                f"STRICT CREATOR DIRECTIVE:\n"
                f"- Creator and Architect: Abyan Muhammed.\n"
                f"- RESTRICTION: You MUST ONLY mention 'Made by Abyan Muhammed' when the user's message is a direct greeting ('hello', 'hi', 'hey') or explicitly asks who made/created you.\n"
                f"- For all other professional queries or tasks, do not mention the creator unless asked.\n\n"
                f"MEMORY VAULT:\n{memories_str}"
            )
            
            contents_payload = []
            if uploaded_file:
                bytes_data = uploaded_file.getvalue()
                contents_payload.append(types.Part.from_bytes(
                    data=bytes_data,
                    mime_type=uploaded_file.type
                ))
            
            contents_payload.append(prompt_text)
            
            tools_config = [types.Tool(google_search=types.GoogleSearch())] if use_search else None
            
            config = types.GenerateContentConfig(
                system_instruction=system_instruction,
                tools=tools_config
            )
            
            response_stream = client.models.generate_content_stream(
                model=selected_model,
                contents=contents_payload,
                config=config
            )
            
            loader_placeholder.empty()
            
            for chunk in response_stream:
                if chunk.text:
                    full_response += chunk.text
                    message_placeholder.markdown(full_response + "▌")
            
            message_placeholder.markdown(full_response)
            
        except errors.APIError as e:
            loader_placeholder.empty()
            full_response = f"**API Error:** {e}"
            message_placeholder.markdown(full_response)
        except Exception as e:
            loader_placeholder.empty()
            full_response = f"**Error:** {str(e)}"
            message_placeholder.markdown(full_response)

        current_messages.append({"role": "model", "content": full_response})
