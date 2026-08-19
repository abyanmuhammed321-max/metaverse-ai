import uuid
import streamlit as st
from google import genai
from google.genai import errors
from google.genai import types

# 1. Page Configuration & Adaptive Layout
st.set_page_config(
    page_title="Metaverse AI",
    page_icon="⚡",
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

storage_key = f"animated_ai_sessions_{user_email.replace('@', '_at_').replace('.', '_')}"
prefs_storage_key = f"animated_ai_prefs_{user_email.replace('@', '_at_').replace('.', '_')}"
memory_storage_key = f"animated_ai_memory_{user_email.replace('@', '_at_').replace('.', '_')}"

if prefs_storage_key not in st.session_state:
    st.session_state[prefs_storage_key] = {
        "selected_model": "gemini-3.5-flash-lite",
        "lang_choice": "English"
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
            "title": "Prism Stream",
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

# 2. CYBER-NEON ANIMATED STYLING
theme_css = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@500;700;900&family=Plus+Jakarta+Sans:wght@300;400;500;600;700&display=swap');

    html, body, [data-testid="stAppViewContainer"], [data-testid="stMain"] {
        background: radial-gradient(circle at 50% 0%, #0a0b10 0%, #030406 60%, #010203 100%) !important;
        color: #f8fafc !important;
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        width: 100% !important;
    }

    .block-container {
        max-width: 880px !important;
        padding-top: 3.5rem !important;
        padding-bottom: 7.5rem !important;
        padding-left: 2rem !important;
        padding-right: 2rem !important;
        margin: 0 auto !important;
    }

    [data-testid="stSidebar"] {
        background-color: #030406 !important;
        border-right: 1px solid rgba(0, 243, 255, 0.2) !important;
    }

    [data-testid="stSidebar"] * {
        color: #f1f5f9 !important;
    }

    /* Animated Neon Gradient Keyframes */
    @keyframes neonGlowShift {
        0% {
            background-position: 0% 50%;
        }
        50% {
            background-position: 100% 50%;
        }
        100% {
            background-position: 0% 50%;
        }
    }

    .cyber-header {
        text-align: center;
        margin-bottom: 40px;
    }

    .cyber-animated-title {
        font-family: 'Orbitron', sans-serif;
        font-size: 2.6rem;
        font-weight: 900;
        background: linear-gradient(270deg, #00f3ff, #b026ff, #00ff66, #00f3ff);
        background-size: 300% 300%;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: neonGlowShift 6s ease infinite;
        margin-bottom: 8px;
        letter-spacing: 2px;
        filter: drop-shadow(0 0 20px rgba(0, 243, 255, 0.4));
    }

    .cyber-subtitle {
        font-family: 'Orbitron', sans-serif;
        font-size: 0.72rem;
        font-weight: 700;
        color: #00f3ff;
        letter-spacing: 4px;
        text-transform: uppercase;
        opacity: 0.9;
        text-shadow: 0 0 10px rgba(0, 243, 255, 0.5);
    }

    /* Holographic Glass Auth Card */
    .cyber-auth-card {
        background: rgba(8, 11, 18, 0.85);
        backdrop-filter: blur(30px);
        border: 1px solid rgba(0, 243, 255, 0.35);
        border-radius: 24px;
        padding: 48px 36px;
        text-align: center;
        max-width: 480px;
        margin: 40px auto;
        box-shadow: 0 25px 60px rgba(0, 0, 0, 0.8), 0 0 40px rgba(0, 243, 255, 0.15);
        position: relative;
        overflow: hidden;
    }

    .cyber-auth-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 2px;
        background: linear-gradient(90deg, transparent, #00f3ff, transparent);
    }

    .cyber-auth-icon {
        font-size: 2.2rem;
        margin-bottom: 18px;
        display: inline-block;
        padding: 16px;
        background: rgba(0, 243, 255, 0.08);
        border-radius: 20px;
        border: 1px solid rgba(0, 243, 255, 0.3);
        box-shadow: 0 0 25px rgba(0, 243, 255, 0.3);
    }

    .cyber-auth-heading {
        font-family: 'Orbitron', sans-serif;
        font-size: 1.2rem;
        font-weight: 700;
        color: #ffffff;
        margin-bottom: 10px;
        letter-spacing: 1px;
    }

    .cyber-auth-text {
        font-size: 0.9rem;
        color: #94a3b8;
        line-height: 1.6;
        margin-bottom: 32px;
    }

    /* Cyber-Neon Chat Bubbles */
    .stChatMessage {
        background: rgba(8, 11, 18, 0.82) !important;
        backdrop-filter: blur(20px) !important;
        border: 1px solid rgba(0, 243, 255, 0.25) !important;
        border-radius: 18px !important;
        padding: 20px 22px !important;
        margin-bottom: 18px !important;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.6), inset 0 1px 0 rgba(255, 255, 255, 0.1) !important;
    }

    .stChatMessage p, .stChatMessage span, .stChatMessage div {
        color: #f1f5f9 !important;
        font-size: 0.96rem !important;
        line-height: 1.7 !important;
    }

    /* Animated Gradient Buttons */
    .stButton button {
        border-radius: 12px !important;
        font-family: 'Orbitron', sans-serif !important;
        font-weight: 700 !important;
        font-size: 0.72rem !important;
        letter-spacing: 1.5px !important;
        border: 1px solid rgba(0, 243, 255, 0.5) !important;
        background: linear-gradient(135deg, #00f3ff 0%, #0066ff 100%) !important;
        color: #030406 !important;
        padding: 12px 24px !important;
        width: 100% !important;
        box-shadow: 0 6px 25px rgba(0, 243, 255, 0.35) !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    }

    .stButton button:hover {
        background: linear-gradient(135deg, #ffffff 0%, #00f3ff 100%) !important;
        border-color: #ffffff !important;
        box-shadow: 0 10px 30px rgba(0, 243, 255, 0.6) !important;
        transform: translateY(-2px);
    }

    /* Fixed Chat Input */
    [data-testid="stChatInput"] textarea {
        background: rgba(8, 11, 18, 0.95) !important;
        color: #ffffff !important;
        border: 1px solid rgba(0, 243, 255, 0.35) !important;
        border-radius: 16px !important;
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        font-size: 0.95rem !important;
        padding: 16px 20px !important;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.6) !important;
    }

    .sidebar-signature {
        text-align: center;
        font-family: 'Orbitron', sans-serif;
        font-size: 0.58rem;
        color: #00f3ff;
        letter-spacing: 2px;
        padding: 18px 4px;
        margin-top: 24px;
        margin-bottom: 24px;
        border-top: 1px solid rgba(0, 243, 255, 0.2);
        border-bottom: 1px solid rgba(0, 243, 255, 0.2);
        text-transform: uppercase;
        background: rgba(0, 243, 255, 0.04);
        font-weight: 700;
        text-shadow: 0 0 8px rgba(0, 243, 255, 0.4);
    }

    .cyber-status-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 6px 14px;
        margin-bottom: 12px;
        background: rgba(0, 243, 255, 0.1);
        border: 1px solid rgba(0, 243, 255, 0.3);
        border-radius: 8px;
        font-family: 'Orbitron', sans-serif;
        font-size: 0.6rem;
        color: #00f3ff;
        font-weight: 700;
        letter-spacing: 1px;
        text-transform: uppercase;
        text-shadow: 0 0 8px rgba(0, 243, 255, 0.5);
    }
</style>
"""

st.markdown(theme_css, unsafe_allow_html=True)

# 3. Sidebar Panel
with st.sidebar:
    st.markdown("### ⚡ Cyber Nexus")
    
    if not is_logged_in:
        st.write("<span style='font-size: 0.82rem; color: #94a3b8;'>Authenticate to initialize your session.</span>", unsafe_allow_html=True)
        st.button("Sign in with Google", on_click=st.login, use_container_width=True)
    else:
        st.success(f"**{user_display_name}**")
        st.write(f"<span style='font-size: 0.76rem; color: #00f3ff;'>{user_email}</span>", unsafe_allow_html=True)
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
        
        if st.button("➕ New Cyber Stream", use_container_width=True):
            new_sid = str(uuid.uuid4())
            st.session_state[storage_key][new_sid] = {
                "title": "Prism Stream",
                "messages": []
            }
            st.session_state[f"{storage_key}_current_sid"] = new_sid
            st.rerun()
            
        st.markdown("### Active Streams")
        
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
                        st.session_state[storage_key][fresh_sid] = {"title": "Prism Stream", "messages": []}
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

selected_model = st.session_state[prefs_storage_key].get("selected_model", "gemini-3.5-flash-lite")
lang_choice = st.session_state[prefs_storage_key].get("lang_choice", "English")

# 4. Modals
if is_logged_in and st.session_state.get("show_settings_modal", False):
    with st.container():
        st.markdown("#### Cyber Configuration")
        models_list = ["gemini-3.5-flash-lite", "gemini-3.1-flash-lite", "gemini-2.5-flash", "gemini-2.5-pro"]
        model_index = models_list.index(selected_model) if selected_model in models_list else 0
        selected_model_input = st.selectbox("AI Model Core", models_list, index=model_index)

        languages = ["English", "Malayalam", "Hindi", "Spanish", "French", "German", "Japanese", "Chinese", "Arabic"]
        lang_index = languages.index(lang_choice) if lang_choice in languages else 0
        lang_choice_input = st.selectbox("Response Language", languages, index=lang_index)
        
        col_s1, col_s2 = st.columns(2)
        with col_s1:
            if st.button("Apply Changes", use_container_width=True):
                st.session_state[prefs_storage_key]["selected_model"] = selected_model_input
                st.session_state[prefs_storage_key]["lang_choice"] = lang_choice_input
                st.session_state["show_settings_modal"] = False
                st.rerun()
        with col_s2:
            if st.button("Cancel", use_container_width=True):
                st.session_state["show_settings_modal"] = False
                st.rerun()
        st.markdown("---")

if is_logged_in and st.session_state.get("show_brain_modal", False):
    with st.container():
        st.markdown("#### Cyber Memory Vault")
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

selected_model = st.session_state[prefs_storage_key].get("selected_model", "gemini-3.5-flash-lite")
lang_choice = st.session_state[prefs_storage_key].get("lang_choice", "English")

# 5. Main Content Area
st.markdown(f"""
    <div class="cyber-header">
        <div class="cyber-animated-title">Metaverse AI</div>
        <div class="cyber-subtitle">{selected_model} &bull; {lang_choice}</div>
    </div>
""", unsafe_allow_html=True)

if not is_logged_in:
    st.markdown("""
        <div class="cyber-auth-card">
            <div class="cyber-auth-icon">⚡</div>
            <div class="cyber-auth-heading">Enter the Cyber Gateway</div>
            <div class="cyber-auth-text">
                Authenticate with Google to unlock animated neon intelligence, persistent memory vaults, and luxury cyber streams.
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

# 6. Chat Execution Pipeline
prompt = st.chat_input("Command the cyber intelligence...")

if prompt:
    if len(current_messages) == 0:
        current_session_data["title"] = prompt[:16]

    current_messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        loader_placeholder = st.empty()
        loader_placeholder.markdown("""
            <div class="cyber-status-badge">⚡ Synthesizing Cyber Output...</div>
        """, unsafe_allow_html=True)
        
        message_placeholder = st.empty()
        full_response = ""
        
        try:
            client = genai.Client(api_key=api_key)
            
            memories_str = "\n".join([f"- {m}" for m in st.session_state[memory_storage_key]])
            system_instruction = (
                f"You are Metaverse AI, built on Google architecture. Respond in {lang_choice}.\n"
                f"USER PROFILE:\n- Name: {user_display_name}\n- Email: {user_email}\n\n"
                f"STRICT CREATOR DIRECTIVE:\n"
                f"- Creator and Architect: Abyan Muhammed.\n"
                f"- RESTRICTION: You MUST ONLY mention 'Made by Abyan Muhammed' when the user's message is a direct greeting ('hello', 'hi', 'hey') or explicitly asks who made/created you.\n"
                f"- For all other professional queries or tasks, do not mention the creator unless asked.\n\n"
                f"MEMORY VAULT:\n{memories_str}"
            )
            
            chat_history_formatted = [
                {"role": m["role"], "parts": [{"text": m["content"]}]} 
                for m in current_messages
            ]
            
            config = types.GenerateContentConfig(
                system_instruction=system_instruction
            )
            
            response_stream = client.models.generate_content_stream(
                model=selected_model,
                contents=chat_history_formatted,
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
