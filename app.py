import uuid
import time
import streamlit as st
from google import genai
from google.genai import errors
from google.genai import types

# 1. Page Configuration & Adaptive Layout
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
    user_display_name = getattr(st.user, "name", "User")
except Exception:
    is_logged_in = False
    user_email = "default_guest_user"
    user_display_name = "User"

storage_key = f"aurora_ai_sessions_{user_email.replace('@', '_at_').replace('.', '_')}"
prefs_storage_key = f"aurora_ai_prefs_{user_email.replace('@', '_at_').replace('.', '_')}"
memory_storage_key = f"aurora_ai_memory_{user_email.replace('@', '_at_').replace('.', '_')}"

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
            "title": "Aurora Stream",
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

# 2. AURORA BOREALIS CYBER-GLASS STYLING
theme_css = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700&family=Space+Grotesk:wght@500;700&display=swap');

    html, body, [data-testid="stAppViewContainer"], [data-testid="stMain"] {
        background: #050508 !important;
        background-image: 
            radial-gradient(at 10% 20%, rgba(16, 185, 129, 0.12) 0px, transparent 50%),
            radial-gradient(at 90% 10%, rgba(59, 130, 246, 0.15) 0px, transparent 50%),
            radial-gradient(at 50% 90%, rgba(147, 51, 234, 0.12) 0px, transparent 50%) !important;
        color: #f3f4f6 !important;
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        width: 100% !important;
    }

    .block-container {
        max-width: 860px !important;
        padding-top: 3.5rem !important;
        padding-bottom: 7.5rem !important;
        padding-left: 2rem !important;
        padding-right: 2rem !important;
        margin: 0 auto !important;
    }

    [data-testid="stSidebar"] {
        background-color: #07080c !important;
        border-right: 1px solid rgba(255, 255, 255, 0.06) !important;
    }

    [data-testid="stSidebar"] * {
        color: #e5e7eb !important;
    }

    @keyframes auroraFlow {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    .aurora-header {
        text-align: center;
        margin-bottom: 36px;
    }

    .aurora-title {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 2.8rem;
        font-weight: 700;
        background: linear-gradient(270deg, #34d399, #60a5fa, #c084fc, #34d399);
        background-size: 300% 300%;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: auroraFlow 8s ease infinite;
        margin-bottom: 6px;
        letter-spacing: -0.5px;
    }

    .aurora-subtitle {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 0.75rem;
        font-weight: 500;
        color: #9ca3af;
        letter-spacing: 3px;
        text-transform: uppercase;
    }

    /* Floating Glass Auth Card */
    .aurora-auth-card {
        background: rgba(18, 20, 28, 0.65);
        backdrop-filter: blur(24px);
        -webkit-backdrop-filter: blur(24px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 28px;
        padding: 48px 36px;
        text-align: center;
        max-width: 460px;
        margin: 40px auto;
        box-shadow: 0 30px 60px rgba(0, 0, 0, 0.7), inset 0 1px 0 rgba(255, 255, 255, 0.1);
    }

    .aurora-auth-icon {
        font-size: 2rem;
        margin-bottom: 16px;
        display: inline-block;
        padding: 16px;
        background: rgba(96, 165, 250, 0.1);
        border-radius: 22px;
        border: 1px solid rgba(96, 165, 250, 0.2);
    }

    .aurora-auth-heading {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 1.3rem;
        font-weight: 700;
        color: #ffffff;
        margin-bottom: 8px;
    }

    .aurora-auth-text {
        font-size: 0.9rem;
        color: #9ca3af;
        line-height: 1.6;
        margin-bottom: 30px;
    }

    /* Glass Chat Bubbles */
    .stChatMessage {
        background: rgba(18, 20, 28, 0.55) !important;
        backdrop-filter: blur(16px) !important;
        -webkit-backdrop-filter: blur(16px) !important;
        border: 1px solid rgba(255, 255, 255, 0.06) !important;
        border-radius: 20px !important;
        padding: 20px 24px !important;
        margin-bottom: 16px !important;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.4) !important;
    }

    .stChatMessage p, .stChatMessage span, .stChatMessage div {
        color: #e5e7eb !important;
        font-size: 0.95rem !important;
        line-height: 1.7 !important;
    }

    /* Smooth Modern Buttons */
    .stButton button {
        border-radius: 14px !important;
        font-family: 'Space Grotesk', sans-serif !important;
        font-weight: 600 !important;
        font-size: 0.8rem !important;
        letter-spacing: 0.5px !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        background: linear-gradient(135deg, rgba(255,255,255,0.08) 0%, rgba(255,255,255,0.02) 100%) !important;
        color: #ffffff !important;
        padding: 12px 24px !important;
        width: 100% !important;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3) !important;
        transition: all 0.25s ease !important;
    }

    .stButton button:hover {
        background: linear-gradient(135deg, rgba(96, 165, 250, 0.25) 0%, rgba(52, 211, 153, 0.25) 100%) !important;
        border-color: rgba(96, 165, 250, 0.4) !important;
        box-shadow: 0 6px 25px rgba(96, 165, 250, 0.2) !important;
        transform: translateY(-1px);
    }

    /* Fixed Chat Input */
    [data-testid="stChatInput"] textarea {
        background: rgba(14, 16, 23, 0.9) !important;
        color: #ffffff !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 18px !important;
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        font-size: 0.95rem !important;
        padding: 16px 20px !important;
        box-shadow: 0 15px 35px rgba(0, 0, 0, 0.6) !important;
    }

    .sidebar-signature {
        text-align: center;
        font-family: 'Space Grotesk', sans-serif;
        font-size: 0.65rem;
        color: #9ca3af;
        letter-spacing: 2px;
        padding: 16px 4px;
        margin-top: 24px;
        margin-bottom: 24px;
        border-top: 1px solid rgba(255, 255, 255, 0.06);
        border-bottom: 1px solid rgba(255, 255, 255, 0.06);
        text-transform: uppercase;
        background: rgba(255, 255, 255, 0.01);
        font-weight: 600;
    }

    .aurora-badge {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        padding: 6px 14px;
        margin-bottom: 12px;
        background: rgba(52, 211, 153, 0.08);
        border: 1px solid rgba(52, 211, 153, 0.2);
        border-radius: 10px;
        font-family: 'Space Grotesk', sans-serif;
        font-size: 0.65rem;
        color: #34d399;
        font-weight: 600;
        letter-spacing: 1px;
        text-transform: uppercase;
    }
</style>
"""

st.markdown(theme_css, unsafe_allow_html=True)

# 3. Sidebar Panel
with st.sidebar:
    st.markdown("### ✨ Aurora Nexus")
    
    if not is_logged_in:
        st.write("<span style='font-size: 0.82rem; color: #9ca3af;'>Sign in to start your session.</span>", unsafe_allow_html=True)
        st.button("Sign in with Google", on_click=st.login, use_container_width=True)
    else:
        st.success(f"**{user_display_name}**")
        st.write(f"<span style='font-size: 0.76rem; color: #34d399;'>{user_email}</span>", unsafe_allow_html=True)
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
        
        if st.button("➕ New Aurora Stream", use_container_width=True):
            new_sid = str(uuid.uuid4())
            st.session_state[storage_key][new_sid] = {
                "title": "Aurora Stream",
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
                        st.session_state[storage_key][fresh_sid] = {"title": "Aurora Stream", "messages": []}
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
        st.markdown("#### System Preferences")
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

selected_model = st.session_state[prefs_storage_key].get("selected_model", "gemini-3.5-flash-lite")
lang_choice = st.session_state[prefs_storage_key].get("lang_choice", "English")

# 5. Main Content Area
st.markdown(f"""
    <div class="aurora-header">
        <div class="aurora-title">Metaverse AI</div>
        <div class="aurora-subtitle">{selected_model} &bull; {lang_choice}</div>
    </div>
""", unsafe_allow_html=True)

if not is_logged_in:
    st.markdown("""
        <div class="aurora-auth-card">
            <div class="aurora-auth-icon">✨</div>
            <div class="aurora-auth-heading">Welcome to Metaverse AI</div>
            <div class="aurora-auth-text">
                Authenticate with Google to unlock glass-morphic AI chat streams, memory vaults, and multi-model support.
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
prompt = st.chat_input("Ask or command anything...")

if prompt:
    if len(current_messages) == 0:
        current_session_data["title"] = prompt[:16]

    current_messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        loader_placeholder = st.empty()
        loader_placeholder.markdown("""
            <div class="aurora-badge">✨ Generating Response...</div>
        """, unsafe_allow_html=True)
        
        message_placeholder = st.empty()
        full_response = ""
        animated_response = ""
        
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
            
            # Typewriter / Replaying Animation Stream Loop
            for chunk in response_stream:
                if chunk.text:
                    full_response += chunk.text
                    # Smoothly animate typing character by character or word by word
                    for char in chunk.text:
                        animated_response += char
                        message_placeholder.markdown(animated_response + "▌")
                        time.sleep(0.005) # Adjust typing speed here (lower = faster)
            
            # Final output rendering without cursor
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
