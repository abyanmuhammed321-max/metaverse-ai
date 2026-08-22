import uuid
import streamlit as st
from google import genai
from google.genai import errors
from google.genai import types

# 1. Page Configuration & Layout
st.set_page_config(
    page_title="Metaverse AI",
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
    user_display_name = getattr(st.user, "name", "Traveler")
except Exception:
    is_logged_in = False
    user_email = "default_guest_user"
    user_display_name = "Traveler"

storage_key = f"metaverse_ai_sessions_{user_email.replace('@', '_at_').replace('.', '_')}"
prefs_storage_key = f"metaverse_ai_prefs_{user_email.replace('@', '_at_').replace('.', '_')}"
memory_storage_key = f"metaverse_ai_memory_{user_email.replace('@', '_at_').replace('.', '_')}"

if prefs_storage_key not in st.session_state:
    st.session_state[prefs_storage_key] = {
        "selected_model": "gemini-3.1-flash-lite",
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

# 2. ICONIC GEMINI-INSPIRED BRAND STYLING
theme_css = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Google+Sans:wght@400;500;600;700&family=Inter:wght@300;400;500;600&display=swap');

    @keyframes backgroundFluid {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    @keyframes replyFadeSlide {
        0% { opacity: 0; transform: translateY(14px); filter: blur(3px); }
        100% { opacity: 1; transform: translateY(0); filter: blur(0px); }
    }

    @keyframes geminiGlow {
        0% { filter: hue-rotate(0deg); }
        50% { filter: hue-rotate(45deg); }
        100% { filter: hue-rotate(0deg); }
    }

    /* Iconic Clean Background with Animated Gradient Mesh */
    html, body, [data-testid="stAppViewContainer"], [data-testid="stMain"] {
        background: linear-gradient(135deg, #131518, #1a1e26, #121824, #181422) !important;
        background-size: 400% 400% !important;
        animation: backgroundFluid 20s ease infinite !important;
        color: #e3e3e3 !important;
        font-family: 'Inter', sans-serif !important;
        width: 100% !important;
    }

    .block-container {
        max-width: 840px !important;
        padding-top: 4.5rem !important;
        padding-bottom: 10rem !important;
        padding-left: 2rem !important;
        padding-right: 2rem !important;
        margin: 0 auto !important;
    }

    /* Sleek Sidebar */
    [data-testid="stSidebar"] {
        background-color: #171a21 !important;
        border-right: 1px solid rgba(255, 255, 255, 0.08) !important;
        padding-top: 1.5rem !important;
        padding-left: 0.8rem !important;
        padding-right: 0.8rem !important;
    }

    [data-testid="stSidebar"] * {
        color: #e3e3e3 !important;
        font-family: 'Inter', sans-serif !important;
    }

    /* Iconic Brand Typography */
    .brand-title {
        font-family: 'Google Sans', sans-serif;
        font-size: 2.8rem;
        font-weight: 700;
        background: linear-gradient(135deg, #4285f4, #9b72cb, #d96570);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 6px;
        letter-spacing: -0.5px;
    }

    .brand-subheading {
        font-size: 1.15rem;
        color: #9aa0a6;
        font-weight: 400;
    }

    .gemini-auth-card {
        background: rgba(26, 30, 38, 0.85);
        border: 1px solid rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(20px);
        border-radius: 28px;
        padding: 50px 35px;
        text-align: center;
        max-width: 440px;
        margin: 50px auto;
        box-shadow: 0 20px 50px rgba(0,0,0,0.5);
    }

    .stChatMessage {
        background: transparent !important;
        border: none !important;
        padding: 16px 0px !important;
        margin-bottom: 14px !important;
    }

    /* AI Reply Fade-in Animation */
    [data-testid="stChatMessage"]:nth-child(even) {
        animation: replyFadeSlide 0.45s cubic-bezier(0.16, 1, 0.3, 1) forwards;
    }

    .stChatMessage p, .stChatMessage span, .stChatMessage div {
        color: #e3e3e3 !important;
        font-size: 1rem !important;
        line-height: 1.8 !important;
        font-family: 'Inter', sans-serif !important;
    }

    /* Rounded Pill Buttons */
    .stButton button {
        border-radius: 24px !important;
        font-family: 'Google Sans', sans-serif !important;
        font-weight: 500 !important;
        font-size: 0.8rem !important;
        letter-spacing: 0.3px !important;
        border: 1px solid rgba(255, 255, 255, 0.12) !important;
        background: rgba(32, 38, 49, 0.9) !important;
        color: #8ab4f8 !important;
        padding: 10px 22px !important;
        width: 100% !important;
        transition: all 0.2s ease !important;
    }

    .stButton button:hover {
        background: rgba(138, 180, 248, 0.15) !important;
        border-color: #8ab4f8 !important;
        color: #ffffff !important;
        box-shadow: 0 0 15px rgba(138, 180, 248, 0.2) !important;
    }

    /* Modern Chat Input Box */
    [data-testid="stChatInput"] textarea {
        background: rgba(22, 27, 34, 0.95) !important;
        color: #ffffff !important;
        border: 1px solid rgba(255, 255, 255, 0.15) !important;
        border-radius: 28px !important;
        font-family: 'Inter', sans-serif !important;
        font-size: 1rem !important;
        padding: 16px 24px !important;
        box-shadow: 0 12px 35px rgba(0, 0, 0, 0.6) !important;
    }

    .sidebar-signature {
        text-align: center;
        font-family: 'Google Sans', sans-serif;
        font-size: 0.65rem;
        letter-spacing: 2.5px;
        padding: 16px 6px;
        margin-top: 24px;
        margin-bottom: 20px;
        border-top: 1px solid rgba(255, 255, 255, 0.08);
        border-bottom: 1px solid rgba(255, 255, 255, 0.08);
        text-transform: uppercase;
        background: linear-gradient(135deg, rgba(66, 133, 244, 0.05), rgba(155, 114, 203, 0.05));
        color: #8ab4f8 !important;
        font-weight: 700;
    }

    .gemini-badge {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        padding: 6px 14px;
        margin-bottom: 14px;
        background: rgba(138, 180, 248, 0.08);
        border: 1px solid rgba(138, 180, 248, 0.25);
        border-radius: 16px;
        font-family: 'Google Sans', sans-serif;
        font-size: 0.72rem;
        color: #8ab4f8;
    }
</style>
"""

st.markdown(theme_css, unsafe_allow_html=True)

# 3. Sidebar Panel Layout
with st.sidebar:
    st.markdown("<div style='font-family: Google Sans; font-size: 1.15rem; font-weight: 700; margin-bottom: 14px; padding-left: 6px; color: #8ab4f8;'>✨ Metaverse AI</div>", unsafe_allow_html=True)
    
    if not is_logged_in:
        st.write("<span style='font-size: 0.82rem; color: #9aa0a6; padding-left: 6px;'>Sign in to start session.</span>", unsafe_allow_html=True)
        st.button("Connect with Google", on_click=st.login, use_container_width=True)
    else:
        st.success(f"**{user_display_name}**")
        st.write(f"<span style='font-size: 0.76rem; color: #8ab4f8;'>{user_email}</span>", unsafe_allow_html=True)
        st.button("Disconnect", on_click=st.logout, use_container_width=True)
            
        st.markdown("---")
        
        show_settings = st.checkbox("⚙️ AI Settings", value=st.session_state["show_settings_modal"])
        if show_settings != st.session_state["show_settings_modal"]:
            st.session_state["show_settings_modal"] = show_settings
            st.rerun()

        show_brain = st.checkbox("🧠 Memory Core", value=st.session_state["show_brain_modal"])
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
            
        st.markdown("<div style='font-family: Google Sans; font-size: 0.7rem; text-transform: uppercase; letter-spacing: 1.2px; color: #9aa0a6; margin-top: 18px; margin-bottom: 8px; padding-left: 6px;'>Recent Chats</div>", unsafe_allow_html=True)
        
        for sid, sdata in list(st.session_state[storage_key].items()):
            col1, col2 = st.columns([0.78, 0.22])
            with col1:
                display_title = sdata["title"][:16] + ("..." if len(sdata["title"]) > 16 else "")
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

selected_model = st.session_state[prefs_storage_key].get("selected_model", "gemini-3.1-flash-lite")
lang_choice = st.session_state[prefs_storage_key].get("lang_choice", "English")
use_search = st.session_state[prefs_storage_key].get("use_search", True)

# 4. Settings & Memory Modals
if is_logged_in and st.session_state.get("show_settings_modal", False):
    with st.container():
        st.markdown("#### ⚙️ AI Configuration & Model Settings")
        models_list = [
            "gemini-3.1-flash-lite", 
            "gemini-3.1-pro-preview", 
            "gemini-2.5-flash"
        ]
        model_index = models_list.index(selected_model) if selected_model in models_list else 0
        selected_model_input = st.selectbox("AI Model Core", models_list, index=model_index)

        languages = ["English", "Malayalam", "Hindi", "Spanish", "French", "German", "Arabic", "Chinese", "Japanese"]
        lang_index = languages.index(lang_choice) if lang_choice in languages else 0
        lang_choice_input = st.selectbox("Response Language", languages, index=lang_index)
        
        use_search_input = st.checkbox("Enable Google Search Grounding", value=use_search)
        
        col_s1, col_s2 = st.columns(2)
        with col_s1:
            if st.button("Save Settings", use_container_width=True):
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
        st.markdown("#### 🧠 Memory Core Vault")
        memory_list = st.session_state[memory_storage_key]
        for idx, mem in enumerate(memory_list):
            col_m1, col_m2 = st.columns([0.82, 0.18])
            with col_m1:
                st.code(mem, language="text")
            with col_m2:
                if st.button("✕", key=f"del_mem_{idx}", use_container_width=True):
                    memory_list.pop(idx)
                    st.rerun()

        if st.button("Close Memory Core", use_container_width=True):
            st.session_state["show_brain_modal"] = False
            st.rerun()
        st.markdown("---")

selected_model = st.session_state[prefs_storage_key].get("selected_model", "gemini-3.1-flash-lite")
lang_choice = st.session_state[prefs_storage_key].get("lang_choice", "English")
use_search = st.session_state[prefs_storage_key].get("use_search", True)

# 5. Main Viewport Header
if is_logged_in and len(current_session_data["messages"]) == 0:
    st.markdown(f"""
        <div style="margin-bottom: 35px; padding-left: 4px;">
            <div class="brand-title">Hello, {user_display_name}</div>
            <div class="brand-subheading">What would you like to create or explore today?</div>
        </div>
    """, unsafe_allow_html=True)
else:
    st.markdown(f"""
        <div style="margin-bottom: 25px; padding-left: 4px;">
            <div style="font-family: Google Sans; font-size: 1.6rem; font-weight: 700; color: #8ab4f8;">Metaverse AI</div>
            <div style="font-size: 0.75rem; color: #9aa0a6; text-transform: uppercase; letter-spacing: 1px;">{selected_model} &bull; Ready</div>
        </div>
    """, unsafe_allow_html=True)

if not is_logged_in:
    st.markdown("""
        <div class="gemini-auth-card">
            <div style="font-size: 2.5rem; margin-bottom: 16px; color: #8ab4f8;">✨</div>
            <div style="font-family: Google Sans; font-size: 1.35rem; font-weight: 700; color: #ffffff; margin-bottom: 8px;">Metaverse AI</div>
            <div style="font-size: 0.95rem; color: #9aa0a6; line-height: 1.6; margin-bottom: 28px;">
                Connect with Google to unlock Gemini intelligence.
            </div>
    """, unsafe_allow_html=True)
    
    col_b1, col_b2, col_b3 = st.columns([1, 2, 1])
    with col_b2:
        st.button("Connect with Google", on_click=st.login, use_container_width=True)
        
    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

current_messages = current_session_data["messages"]

for message in current_messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "file_name" in message:
            st.markdown(f"<span style='font-size:0.75rem; color:#8ab4f8;'>📎 {message['file_name']}</span>", unsafe_allow_html=True)

# 6. File Upload
uploaded_file = st.file_uploader("Upload file or image", type=["png", "jpg", "jpeg", "pdf", "txt", "csv", "py"])

# 7. Prompt Execution & Streaming Pipeline with Reply Animation
prompt = st.chat_input("Ask Metaverse AI...")

if prompt or uploaded_file:
    prompt_text = prompt if prompt else "Analyze this file."
    if len(current_messages) == 0:
        current_session_data["title"] = prompt_text[:18]

    user_msg_data = {"role": "user", "content": prompt_text}
    if uploaded_file:
        user_msg_data["file_name"] = uploaded_file.name

    current_messages.append(user_msg_data)
    with st.chat_message("user"):
        st.markdown(prompt_text)
        if uploaded_file:
            st.markdown(f"<span style='font-size:0.75rem; color:#8ab4f8;'>📎 {uploaded_file.name}</span>", unsafe_allow_html=True)

    with st.chat_message("assistant"):
        loader_placeholder = st.empty()
        loader_placeholder.markdown("""
            <div class="gemini-badge">✨ Metaverse AI is thinking...</div>
        """, unsafe_allow_html=True)
        
        message_placeholder = st.empty()
        full_response = ""
        
        try:
            client = genai.Client(api_key=api_key)
            
            memories_str = "\n".join([f"- {m}" for m in st.session_state[memory_storage_key]])
            system_instruction = (
                f"You are Metaverse AI, powered by Google's Gemini architecture. Respond in {lang_choice}.\n"
                f"USER PROFILE:\n- Name: {user_display_name}\n- Email: {user_email}\n\n"
                f"STRICT CREATOR DIRECTIVE:\n"
                f"- Creator and Architect: Abyan Muhammed.\n"
                f"- RESTRICTION: You MUST ONLY mention 'Made by Abyan Muhammed' when the user's message is a direct greeting ('hello', 'hi', 'hey') or explicitly asks who made/created you.\n"
                f"- For all other professional queries or tasks, do not mention the creator unless asked.\n\n"
                f"MEMORY CORE:\n{memories_str}"
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
