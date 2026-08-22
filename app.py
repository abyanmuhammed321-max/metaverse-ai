import uuid
import streamlit as st
from google import genai
from google.genai import errors
from google.genai import types

# 1. Page Configuration & Layout
st.set_page_config(
    page_title="Metaverse AI",
    page_icon="🔮",
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
            "title": "Quantum Stream",
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

# 2. METAVERSE AI STYLING WITH BACKGROUND & REPLY ANIMATIONS
theme_css = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@500;700&family=Outfit:wght@300;400;500;600&display=swap');

    @keyframes backgroundFluid {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    @keyframes replyFadeSlide {
        0% { opacity: 0; transform: translateY(12px); filter: blur(4px); }
        100% { opacity: 1; transform: translateY(0); filter: blur(0px); }
    }

    @keyframes textGlow {
        0% { color: #00f2fe; text-shadow: 0 0 10px rgba(0, 242, 254, 0.4); }
        50% { color: #a855f7; text-shadow: 0 0 10px rgba(168, 85, 247, 0.4); }
        100% { color: #00f2fe; text-shadow: 0 0 10px rgba(0, 242, 254, 0.4); }
    }

    /* Animated Dynamic Background */
    html, body, [data-testid="stAppViewContainer"], [data-testid="stMain"] {
        background: linear-gradient(135deg, #030408, #0a0e1a, #06050a, #0f0814) !important;
        background-size: 400% 400% !important;
        animation: backgroundFluid 18s ease infinite !important;
        color: #f3f4f6 !important;
        font-family: 'Outfit', sans-serif !important;
        width: 100% !important;
    }

    .block-container {
        max-width: 820px !important;
        padding-top: 4rem !important;
        padding-bottom: 9.5rem !important;
        padding-left: 2rem !important;
        padding-right: 2rem !important;
        margin: 0 auto !important;
    }

    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background-color: #070910 !important;
        border-right: 1px solid rgba(0, 242, 254, 0.12) !important;
        padding-top: 1.5rem !important;
        padding-left: 0.6rem !important;
        padding-right: 0.6rem !important;
    }

    [data-testid="stSidebar"] * {
        color: #f3f4f6 !important;
        font-family: 'Outfit', sans-serif !important;
    }

    .metaverse-greeting {
        font-family: 'Orbitron', sans-serif;
        font-size: 2.6rem;
        font-weight: 700;
        background: linear-gradient(135deg, #00f2fe, #a855f7, #ec4899);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 4px;
    }

    .metaverse-subgreeting {
        font-size: 1.15rem;
        color: #9ca3af;
        font-weight: 400;
    }

    .metaverse-auth-card {
        background: rgba(10, 14, 24, 0.85);
        border: 1px solid rgba(0, 242, 254, 0.25);
        backdrop-filter: blur(25px);
        border-radius: 24px;
        padding: 45px 30px;
        text-align: center;
        max-width: 420px;
        margin: 50px auto;
        box-shadow: 0 15px 45px rgba(0,0,0,0.6);
    }

    .stChatMessage {
        background: transparent !important;
        border: none !important;
        padding: 14px 0px !important;
        margin-bottom: 12px !important;
    }

    /* AI Reply Text Animation */
    [data-testid="stChatMessage"]:nth-child(even) {
        animation: replyFadeSlide 0.5s cubic-bezier(0.16, 1, 0.3, 1) forwards;
    }

    .stChatMessage p, .stChatMessage span, .stChatMessage div {
        color: #f3f4f6 !important;
        font-size: 1rem !important;
        line-height: 1.75 !important;
        font-family: 'Outfit', sans-serif !important;
    }

    .stButton button {
        border-radius: 12px !important;
        font-family: 'Orbitron', sans-serif !important;
        font-weight: 500 !important;
        font-size: 0.72rem !important;
        letter-spacing: 1px !important;
        border: 1px solid rgba(0, 242, 254, 0.3) !important;
        background: rgba(12, 17, 29, 0.9) !important;
        color: #00f2fe !important;
        padding: 10px 20px !important;
        width: 100% !important;
        transition: all 0.25s ease !important;
    }

    .stButton button:hover {
        background: rgba(0, 242, 254, 0.2) !important;
        border-color: #00f2fe !important;
        color: #ffffff !important;
        box-shadow: 0 0 20px rgba(0, 242, 254, 0.35) !important;
    }

    [data-testid="stChatInput"] textarea {
        background: rgba(9, 13, 22, 0.95) !important;
        color: #f3f4f6 !important;
        border: 1px solid rgba(0, 242, 254, 0.35) !important;
        border-radius: 20px !important;
        font-family: 'Outfit', sans-serif !important;
        font-size: 1rem !important;
        padding: 16px 22px !important;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.7) !important;
    }

    .sidebar-signature {
        text-align: center;
        font-family: 'Orbitron', sans-serif;
        font-size: 0.6rem;
        letter-spacing: 2px;
        padding: 14px 4px;
        margin-top: 20px;
        margin-bottom: 20px;
        border-top: 1px solid rgba(0, 242, 254, 0.15);
        border-bottom: 1px solid rgba(0, 242, 254, 0.15);
        text-transform: uppercase;
        background: rgba(0, 242, 254, 0.04);
        animation: textGlow 5s infinite;
        font-weight: 700;
    }

    .metaverse-badge {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        padding: 6px 14px;
        margin-bottom: 12px;
        background: rgba(0, 242, 254, 0.08);
        border: 1px solid rgba(0, 242, 254, 0.35);
        border-radius: 10px;
        font-family: 'Orbitron', sans-serif;
        font-size: 0.65rem;
        color: #00f2fe;
        animation: textGlow 4s infinite;
    }
</style>
"""

st.markdown(theme_css, unsafe_allow_html=True)

# 3. Sidebar Panel Layout
with st.sidebar:
    st.markdown("<div style='font-family: Orbitron; font-size: 1.1rem; font-weight: 700; margin-bottom: 14px; padding-left: 6px; color: #00f2fe;'>🔮 Metaverse AI</div>", unsafe_allow_html=True)
    
    if not is_logged_in:
        st.write("<span style='font-size: 0.82rem; color: #9ca3af; padding-left: 6px;'>Sign in to start session.</span>", unsafe_allow_html=True)
        st.button("Connect with Google", on_click=st.login, use_container_width=True)
    else:
        st.success(f"**{user_display_name}**")
        st.write(f"<span style='font-size: 0.76rem; color: #00f2fe;'>{user_email}</span>", unsafe_allow_html=True)
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
        
        if st.button("➕ New Quantum Stream", use_container_width=True):
            new_sid = str(uuid.uuid4())
            st.session_state[storage_key][new_sid] = {
                "title": "Quantum Stream",
                "messages": []
            }
            st.session_state[f"{storage_key}_current_sid"] = new_sid
            st.rerun()
            
        st.markdown("<div style='font-family: Orbitron; font-size: 0.65rem; text-transform: uppercase; letter-spacing: 1.5px; color: #9ca3af; margin-top: 16px; margin-bottom: 6px; padding-left: 6px;'>Recent Streams</div>", unsafe_allow_html=True)
        
        for sid, sdata in list(st.session_state[storage_key].items()):
            col1, col2 = st.columns([0.78, 0.22])
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
                        st.session_state[storage_key][fresh_sid] = {"title": "Quantum Stream", "messages": []}
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
        st.markdown("#### ⚙️ AI Settings & Preferences")
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
        
        use_search_input = st.checkbox("Enable Quantum Web Search Grounding", value=use_search)
        
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
            <div class="metaverse-greeting">Hello, {user_display_name}</div>
            <div class="metaverse-subgreeting">What quantum dimension shall we explore today?</div>
        </div>
    """, unsafe_allow_html=True)
else:
    st.markdown(f"""
        <div style="margin-bottom: 25px; padding-left: 4px;">
            <div style="font-family: Orbitron; font-size: 1.6rem; font-weight: 700; color: #00f2fe;">Metaverse AI</div>
            <div style="font-size: 0.72rem; color: #9ca3af; text-transform: uppercase; letter-spacing: 1px;">{selected_model} &bull; Active</div>
        </div>
    """, unsafe_allow_html=True)

if not is_logged_in:
    st.markdown("""
        <div class="metaverse-auth-card">
            <div style="font-size: 2.2rem; margin-bottom: 16px; color: #00f2fe;">🔮</div>
            <div style="font-family: Orbitron; font-size: 1.25rem; font-weight: 700; color: #f3f4f6; margin-bottom: 6px;">Metaverse AI</div>
            <div style="font-size: 0.9rem; color: #9ca3af; line-height: 1.5; margin-bottom: 25px;">
                Connect with Google to activate Gemini intelligence.
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
            st.markdown(f"<span style='font-size:0.72rem; color:#00f2fe;'>📎 {message['file_name']}</span>", unsafe_allow_html=True)

# 6. File Upload
uploaded_file = st.file_uploader("Upload document or image artifact", type=["png", "jpg", "jpeg", "pdf", "txt", "csv", "py"])

# 7. Prompt Execution & Streaming Pipeline with Reply Animation
prompt = st.chat_input("Message Metaverse AI...")

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
            st.markdown(f"<span style='font-size:0.72rem; color:#00f2fe;'>📎 {uploaded_file.name}</span>", unsafe_allow_html=True)

    with st.chat_message("assistant"):
        loader_placeholder = st.empty()
        loader_placeholder.markdown("""
            <div class="metaverse-badge">🔮 Metaverse AI is thinking...</div>
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
