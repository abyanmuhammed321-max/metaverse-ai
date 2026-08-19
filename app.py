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
    initial_sidebar_state="auto"
)

api_key = st.secrets.get("GEMINI_API_KEY")

try:
    is_logged_in = getattr(st.user, "is_logged_in", False)
    user_email = getattr(st.user, "email", "default_guest_user")
    user_display_name = getattr(st.user, "name", "User")
except Exception:
    is_logged_in = False
    user_email = "default_guest_user"
    user_display_name = "User"

storage_key = f"metaverse_ai_sessions_{user_email.replace('@', '_at_').replace('.', '_')}"
prefs_storage_key = f"metaverse_ai_prefs_{user_email.replace('@', '_at_').replace('.', '_')}"
memory_storage_key = f"metaverse_ai_memory_{user_email.replace('@', '_at_').replace('.', '_')}"

# Initialize preferences with theme toggle support
if prefs_storage_key not in st.session_state:
    st.session_state[prefs_storage_key] = {
        "selected_model": "gemini-3.1-flash-lite",
        "lang_choice": "English",
        "theme": "Dark"
    }

if "theme" not in st.session_state[prefs_storage_key]:
    st.session_state[prefs_storage_key]["theme"] = "Dark"

current_theme = st.session_state[prefs_storage_key]["theme"]

# Initialize Memory Bank
if memory_storage_key not in st.session_state:
    st.session_state[memory_storage_key] = [
        "Creator and Master Developer: Abyan Muhammed",
        "Creator Display Rule: Only mention 'Made by Abyan Muhammed' when the user explicitly greets ('hello', 'hi', 'hey') or asks who built/made the AI.",
        "User signed in as Google Identity: " + user_display_name,
        "Core Objective: Flawless responsive layout optimized for mobile phone screens with full viewport scaling and touch-friendly padding."
    ]

if storage_key not in st.session_state:
    first_sid = str(uuid.uuid4())
    st.session_state[storage_key] = {
        first_sid: {
            "title": "New chat",
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

# 3. FULLY RESPONSIVE & MOBILE-OPTIMIZED COLORFUL STYLING
if current_theme == "Light":
    theme_css = """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Google+Sans:wght@400;500;600;700&family=Inter:wght@400;500;600&display=swap');

        /* Force responsive box-sizing & mobile zoom prevention */
        html {
            box-sizing: border-box;
            -webkit-text-size-adjust: 100%;
        }
        *, *:before, *:after {
            box-sizing: inherit;
        }

        html, body, [data-testid="stAppViewContainer"], [data-testid="stMain"], .stApp {
            background: linear-gradient(135deg, #f0fdf4 0%, #eff6ff 50%, #fdf4ff 100%) !important;
            background-attachment: fixed !important;
            color: #0f172a !important;
            font-family: 'Google Sans', 'Inter', sans-serif;
            min-height: 100vh;
            width: 100vw;
            max-width: 100%;
            overflow-x: hidden !important;
            margin: 0 !important;
            padding: 0 !important;
        }

        .block-container {
            max-width: 860px !important;
            width: 100% !important;
            padding-left: 1.5rem !important;
            padding-right: 1.5rem !important;
            padding-top: 2rem !important;
            padding-bottom: 7rem !important;
            margin: 0 auto !important;
        }

        [data-testid="stMain"] > div {
            background-color: rgba(255, 255, 255, 0.9) !important;
            backdrop-filter: blur(12px) !important;
            border: 1px solid rgba(226, 232, 240, 0.8) !important;
            border-radius: 36px !important;
            padding: 32px !important;
            margin: 10px auto !important;
            box-shadow: 0 15px 35px rgba(0, 0, 0, 0.05) !important;
            width: 100% !important;
        }

        /* Mobile Phone Optimization */
        @media (max-width: 768px) {
            .block-container {
                padding-left: 10px !important;
                padding-right: 10px !important;
                padding-top: 0.5rem !important;
                padding-bottom: 7rem !important;
            }
            [data-testid="stMain"] > div {
                padding: 16px !important;
                margin: 4px auto !important;
                border-radius: 20px !important;
                border: none !important;
                box-shadow: none !important;
                background-color: transparent !important;
            }
            .gemini-title {
                font-size: 1.6rem !important;
            }
            .gemini-subtitle {
                font-size: 0.72rem !important;
                margin-bottom: 12px !important;
            }
            .stChatMessage {
                padding: 14px !important;
                border-radius: 18px !important;
                margin-bottom: 12px !important;
            }
            [data-testid="stChatInput"] {
                bottom: 8px !important;
                left: 6px !important;
                right: 6px !important;
                width: calc(100% - 12px) !important;
            }
        }

        [data-testid="stSidebar"] {
            background-color: #f8fafc !important;
            border-right: 1px solid #e2e8f0 !important;
            z-index: 1000;
        }
        
        [data-testid="stSidebar"] * {
            color: #0f172a !important;
        }

        .gemini-title {
            font-family: 'Google Sans', sans-serif;
            font-size: 2.3rem;
            font-weight: 700;
            background: linear-gradient(135deg, #0284c7, #c026d3, #16a34a);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 0px;
            padding-top: 4px;
            letter-spacing: -0.5px;
        }
        
        .gemini-subtitle {
            color: #64748b;
            font-size: 0.8rem;
            margin-bottom: 20px;
            font-weight: 500;
            letter-spacing: 0.3px;
        }

        .stChatMessage {
            background-color: #ffffff !important;
            border: 1px solid #e2e8f0 !important;
            border-radius: 26px !important;
            padding: 20px !important;
            margin-bottom: 16px !important;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.02) !important;
        }

        .stChatMessage p, .stChatMessage span, .stChatMessage div, .stMarkdown {
            color: #0f172a !important;
            font-size: 0.95rem !important;
            line-height: 1.6 !important;
            word-break: break-word;
        }

        .stButton button {
            border-radius: 18px !important;
            font-family: 'Google Sans', sans-serif !important;
            font-weight: 500 !important;
            font-size: 0.82rem !important;
            border: 1px solid #cbd5e1 !important;
            background-color: #ffffff !important;
            color: #0f172a !important;
            box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05) !important;
            transition: all 0.2s ease !important;
        }
        
        .stButton button:hover {
            background-color: #f1f5f9 !important;
            border-color: #0284c7 !important;
            transform: translateY(-1px);
        }

        [data-testid="stChatInput"] {
            padding: 0 4px 8px 4px !important;
        }

        [data-testid="stChatInput"] textarea {
            background-color: #ffffff !important;
            color: #0f172a !important;
            border: 1px solid #cbd5e1 !important;
            border-radius: 30px !important;
            font-family: 'Google Sans', sans-serif !important;
            font-size: 0.95rem !important;
            padding: 16px 22px !important;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05) !important;
        }

        [data-testid="stChatInput"] textarea:focus {
            border-color: #0284c7 !important;
            box-shadow: 0 0 0 2px rgba(2, 132, 199, 0.15) !important;
        }

        .sidebar-signature {
            text-align: center;
            font-family: 'Google Sans', sans-serif;
            font-size: 0.7rem;
            color: #64748b;
            letter-spacing: 1.2px;
            padding: 14px 5px;
            margin-top: 25px;
            margin-bottom: 25px;
            border-top: 1px solid #e2e8f0;
            border-bottom: 1px solid #e2e8f0;
            background-color: transparent;
            text-transform: uppercase;
        }

        .ai-thinking-box {
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 14px 20px;
            background-color: #f1f5f9;
            border: 1px solid #e2e8f0;
            border-radius: 22px;
            width: fit-content;
            margin: 10px 0;
        }

        .ai-thinking-dots {
            display: flex;
            gap: 6px;
            align-items: center;
        }

        .ai-dot {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background-color: #0284c7;
            animation: aiDotBounce 1.4s infinite ease-in-out both;
        }

        .ai-dot:nth-child(1) { animation-delay: -0.32s; }
        .ai-dot:nth-child(2) { animation-delay: -0.16s; background-color: #c026d3; }
        .ai-dot:nth-child(3) { animation-delay: 0s; background-color: #16a34a; }

        @keyframes aiDotBounce {
            0%, 80%, 100% { transform: scale(0); opacity: 0.4; }
            40% { transform: scale(1.3); opacity: 1; }
        }

        .ai-thinking-text {
            font-family: 'Google Sans', sans-serif;
            font-size: 0.85rem;
            font-weight: 500;
            color: #0284c7;
        }

        .ai-replying-badge {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            padding: 6px 14px;
            margin-bottom: 12px;
            background-color: #e0f2fe;
            border: 1px solid #bae6fd;
            border-radius: 16px;
            font-family: 'Google Sans', sans-serif;
            font-size: 0.74rem;
            color: #0369a1;
        }
    </style>
    """
else:
    theme_css = """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Google+Sans:wght@400;500;600;700&family=Inter:wght@400;500;600&display=swap');

        /* Force responsive box-sizing & mobile zoom prevention */
        html {
            box-sizing: border-box;
            -webkit-text-size-adjust: 100%;
        }
        *, *:before, *:after {
            box-sizing: inherit;
        }

        html, body, [data-testid="stAppViewContainer"], [data-testid="stMain"], .stApp {
            background: linear-gradient(135deg, #090d16 0%, #111e2e 35%, #1a102f 70%, #0f172a 100%) !important;
            background-attachment: fixed !important;
            color: #f8fafc !important;
            font-family: 'Google Sans', 'Inter', sans-serif;
            min-height: 100vh;
            width: 100vw;
            max-width: 100%;
            overflow-x: hidden !important;
            margin: 0 !important;
            padding: 0 !important;
        }

        .block-container {
            max-width: 860px !important;
            width: 100% !important;
            padding-left: 1.5rem !important;
            padding-right: 1.5rem !important;
            padding-top: 2rem !important;
            padding-bottom: 7rem !important;
            margin: 0 auto !important;
        }

        [data-testid="stMain"] > div {
            background-color: rgba(17, 24, 39, 0.85) !important;
            backdrop-filter: blur(16px) !important;
            border: 1px solid rgba(56, 189, 248, 0.25) !important;
            border-radius: 36px !important;
            padding: 32px !important;
            margin: 10px auto !important;
            box-shadow: 0 25px 60px rgba(0, 0, 0, 0.7), 0 0 40px rgba(120, 50, 255, 0.1) !important;
            width: 100% !important;
        }

        /* Mobile Phone Optimization */
        @media (max-width: 768px) {
            .block-container {
                padding-left: 10px !important;
                padding-right: 10px !important;
                padding-top: 0.5rem !important;
                padding-bottom: 7rem !important;
            }
            [data-testid="stMain"] > div {
                padding: 16px !important;
                margin: 4px auto !important;
                border-radius: 20px !important;
                border: none !important;
                box-shadow: none !important;
                background-color: transparent !important;
            }
            .gemini-title {
                font-size: 1.6rem !important;
            }
            .gemini-subtitle {
                font-size: 0.72rem !important;
                margin-bottom: 12px !important;
            }
            .stChatMessage {
                padding: 14px !important;
                border-radius: 18px !important;
                margin-bottom: 12px !important;
            }
            [data-testid="stChatInput"] {
                bottom: 8px !important;
                left: 6px !important;
                right: 6px !important;
                width: calc(100% - 12px) !important;
            }
        }

        [data-testid="stSidebar"] {
            background-color: #060913 !important;
            border-right: 1px solid rgba(56, 189, 248, 0.15) !important;
            z-index: 1000;
        }
        
        [data-testid="stSidebar"] * {
            color: #f8fafc !important;
        }

        .gemini-title {
            font-family: 'Google Sans', sans-serif;
            font-size: 2.3rem;
            font-weight: 700;
            background: linear-gradient(135deg, #38bdf8, #e879f9, #34d399, #fb7185);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 0px;
            padding-top: 4px;
            letter-spacing: -0.5px;
        }
        
        .gemini-subtitle {
            color: #94a3b8;
            font-size: 0.8rem;
            margin-bottom: 20px;
            font-weight: 500;
            letter-spacing: 0.3px;
        }

        .stChatMessage {
            background-color: rgba(30, 41, 59, 0.8) !important;
            backdrop-filter: blur(8px) !important;
            border: 1px solid rgba(56, 189, 248, 0.2) !important;
            border-radius: 26px !important;
            padding: 20px !important;
            margin-bottom: 16px !important;
            box-shadow: 0 10px 25px rgba(0, 0, 0, 0.3) !important;
        }

        .stChatMessage p, .stChatMessage span, .stChatMessage div, .stMarkdown {
            color: #f8fafc !important;
            font-size: 0.95rem !important;
            line-height: 1.6 !important;
            word-break: break-word;
        }

        .stButton button {
            border-radius: 18px !important;
            font-family: 'Google Sans', sans-serif !important;
            font-weight: 500 !important;
            font-size: 0.82rem !important;
            border: 1px solid rgba(56, 189, 248, 0.3) !important;
            background-color: rgba(30, 41, 59, 0.9) !important;
            color: #f8fafc !important;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3) !important;
            transition: all 0.2s ease !important;
        }
        
        .stButton button:hover {
            background-color: rgba(51, 65, 85, 1) !important;
            border-color: #38bdf8 !important;
            transform: translateY(-1px);
            box-shadow: 0 6px 16px rgba(56, 189, 248, 0.25) !important;
        }

        [data-testid="stChatInput"] {
            padding: 0 4px 8px 4px !important;
        }

        [data-testid="stChatInput"] textarea {
            background-color: rgba(30, 41, 59, 0.9) !important;
            color: #f8fafc !important;
            border: 1px solid rgba(56, 189, 248, 0.3) !important;
            border-radius: 30px !important;
            font-family: 'Google Sans', sans-serif !important;
            font-size: 0.95rem !important;
            padding: 16px 22px !important;
            box-shadow: 0 8px 24px rgba(0, 0, 0, 0.5) !important;
        }

        [data-testid="stChatInput"] textarea:focus {
            border-color: #38bdf8 !important;
            box-shadow: 0 0 0 3px rgba(56, 189, 248, 0.3) !important;
        }

        .sidebar-signature {
            text-align: center;
            font-family: 'Google Sans', sans-serif;
            font-size: 0.7rem;
            color: #94a3b8;
            letter-spacing: 1.2px;
            padding: 14px 5px;
            margin-top: 25px;
            margin-bottom: 25px;
            border-top: 1px solid rgba(56, 189, 248, 0.15);
            border-bottom: 1px solid rgba(56, 189, 248, 0.15);
            background-color: transparent;
            text-transform: uppercase;
        }

        .ai-thinking-box {
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 14px 20px;
            background-color: rgba(30, 41, 59, 0.9);
            border: 1px solid rgba(56, 189, 248, 0.3);
            border-radius: 22px;
            width: fit-content;
            margin: 10px 0;
        }

        .ai-thinking-dots {
            display: flex;
            gap: 6px;
            align-items: center;
        }

        .ai-dot {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background-color: #38bdf8;
            animation: aiDotBounce 1.4s infinite ease-in-out both;
        }

        .ai-dot:nth-child(1) { animation-delay: -0.32s; }
        .ai-dot:nth-child(2) { animation-delay: -0.16s; background-color: #e879f9; }
        .ai-dot:nth-child(3) { animation-delay: 0s; background-color: #34d399; }

        @keyframes aiDotBounce {
            0%, 80%, 100% { transform: scale(0); opacity: 0.4; }
            40% { transform: scale(1.3); opacity: 1; }
        }

        .ai-thinking-text {
            font-family: 'Google Sans', sans-serif;
            font-size: 0.85rem;
            font-weight: 500;
            color: #38bdf8;
        }

        .ai-replying-badge {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            padding: 6px 14px;
            margin-bottom: 12px;
            background-color: rgba(56, 189, 248, 0.15);
            border: 1px solid rgba(56, 189, 248, 0.35);
            border-radius: 16px;
            font-family: 'Google Sans', sans-serif;
            font-size: 0.74rem;
            color: #38bdf8;
        }
    </style>
    """

st.markdown(theme_css, unsafe_allow_html=True)

# 4. Sidebar Navigation & Feature Control
with st.sidebar:
    st.markdown("### ✨ Metaverse_AI Workspace")
    
    if not is_logged_in:
        st.write("<span style='font-size: 0.8rem;'>Sign in with Google to unlock all features and chats.</span>", unsafe_allow_html=True)
        st.button("🔑 Sign in with Google", on_click=st.login, use_container_width=True, type="primary")
    else:
        st.success(f"**{user_display_name}**")
        st.write(f"<span style='font-size: 0.75rem;'>{user_email}</span>", unsafe_allow_html=True)
        st.button("Sign Out", on_click=st.logout, use_container_width=True)
            
        st.markdown("---")
        
        show_settings = st.checkbox("⚙️ Settings & Models", value=st.session_state["show_settings_modal"])
        if show_settings != st.session_state["show_settings_modal"]:
            st.session_state["show_settings_modal"] = show_settings
            st.rerun()

        show_brain = st.checkbox("🧠 Memory & Context", value=st.session_state["show_brain_modal"])
        if show_brain != st.session_state["show_brain_modal"]:
            st.session_state["show_brain_modal"] = show_brain
            st.rerun()

        st.markdown("---")
        
        if st.button("➕ New chat", use_container_width=True, type="primary"):
            new_sid = str(uuid.uuid4())
            st.session_state[storage_key][new_sid] = {
                "title": "New chat",
                "messages": []
            }
            st.session_state[f"{storage_key}_current_sid"] = new_sid
            st.rerun()
            
        st.markdown("### 💬 Recent chats")
        
        for sid, sdata in list(st.session_state[storage_key].items()):
            col1, col2 = st.columns([0.78, 0.22])
            with col1:
                btn_type = "primary" if sid == current_sid else "secondary"
                display_title = sdata["title"][:16] + ("..." if len(sdata["title"]) > 16 else "")
                if st.button(display_title, key=f"sel_{sid}", use_container_width=True, type=btn_type):
                    st.session_state[f"{storage_key}_current_sid"] = sid
                    st.rerun()
            with col2:
                if st.button("🗑️", key=f"del_{sid}", help="Delete chat"):
                    del st.session_state[storage_key][sid]
                    if not st.session_state[storage_key]:
                        fresh_sid = str(uuid.uuid4())
                        st.session_state[storage_key][fresh_sid] = {"title": "New chat", "messages": []}
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

# 5. Settings Modal Panel with Live Theme Switcher
if is_logged_in and st.session_state.get("show_settings_modal", False):
    with st.container():
        st.markdown("""
            <div style="border-radius: 22px; padding: 22px; margin-bottom: 20px;">
                <h3 style="font-family: 'Google Sans', sans-serif; margin-top: 0; font-size: 1.1rem;">⚙️ Settings & Preferences</h3>
            </div>
        """, unsafe_allow_html=True)
        
        models_list = ["gemini-3.1-flash-lite", "gemini-2.0-flash", "gemini-2.5-flash", "gemini-2.5-pro"]
        model_index = models_list.index(selected_model) if selected_model in models_list else 0
        selected_model_input = st.selectbox("Model Engine", models_list, index=model_index, key="modal_model_select")

        languages = ["English", "Malayalam", "Hindi", "Spanish", "French", "German", "Japanese", "Chinese", "Arabic"]
        lang_index = languages.index(lang_choice) if lang_choice in languages else 0
        lang_choice_input = st.selectbox("Response Language", languages, index=lang_index, key="modal_lang_select")

        themes_list = ["Dark", "Light"]
        theme_index = themes_list.index(current_theme) if current_theme in themes_list else 0
        theme_choice_input = st.radio("Interface Theme Mode", themes_list, index=theme_index, horizontal=True, key="modal_theme_radio")
        
        col_s1, col_s2 = st.columns(2)
        with col_s1:
            if st.button("Save Changes", use_container_width=True, type="primary"):
                st.session_state[prefs_storage_key]["selected_model"] = selected_model_input
                st.session_state[prefs_storage_key]["lang_choice"] = lang_choice_input
                st.session_state[prefs_storage_key]["theme"] = theme_choice_input
                st.session_state["show_settings_modal"] = False
                st.rerun()
        with col_s2:
            if st.button("Close", use_container_width=True):
                st.session_state["show_settings_modal"] = False
                st.rerun()
        st.markdown("---")

# 6. Memory Bank Modal Panel
if is_logged_in and st.session_state.get("show_brain_modal", False):
    with st.container():
        st.markdown("""
            <div style="border-radius: 22px; padding: 22px; margin-bottom: 20px;">
                <h3 style="font-family: 'Google Sans', sans-serif; margin-top: 0; font-size: 1.1rem;">🧠 Memory & Context</h3>
            </div>
        """, unsafe_allow_html=True)
        
        memory_list = st.session_state[memory_storage_key]
        for idx, mem in enumerate(memory_list):
            col_m1, col_m2 = st.columns([0.85, 0.15])
            with col_m1:
                st.code(mem, language="text")
            with col_m2:
                if st.button("🗑️", key=f"del_mem_{idx}"):
                    memory_list.pop(idx)
                    st.rerun()

        if st.button("Close Memory Bank", use_container_width=True):
            st.session_state["show_brain_modal"] = False
            st.rerun()
        st.markdown("---")

# Refresh preferences
selected_model = st.session_state[prefs_storage_key].get("selected_model", "gemini-3.1-flash-lite")
lang_choice = st.session_state[prefs_storage_key].get("lang_choice", "English")
current_theme = st.session_state[prefs_storage_key].get("theme", "Dark")

# 7. Main Canvas Layout
st.markdown(f'<div class="gemini-title">Metaverse_AI</div>', unsafe_allow_html=True)
st.markdown(f'<div class="gemini-subtitle">Engine: {selected_model} • Theme: {current_theme} Mode • Language: {lang_choice}</div>', unsafe_allow_html=True)

if not is_logged_in:
    st.markdown("""
        <div style="border-radius: 28px; padding: 40px; text-align: center; margin-top: 40px;">
            <h2 style="font-family: 'Google Sans', sans-serif; font-size: 1.4rem; margin-bottom: 15px;">Welcome to Metaverse_AI</h2>
            <p style="font-size: 0.95rem; line-height: 1.6; margin-bottom: 25px;">
                Please sign in from the sidebar to access your workspace, start conversations, and interact with advanced AI features.
            </p>
        </div>
    """, unsafe_allow_html=True)
    st.stop()

current_messages = current_session_data["messages"]

for message in current_messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 8. Realtime Message Handling & Animated AI Reply Engine
prompt = st.chat_input("Type your message here...")

if prompt:
    if len(current_messages) == 0:
        current_session_data["title"] = prompt[:22]

    current_messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        loader_placeholder = st.empty()
        loader_placeholder.markdown("""
            <div class="ai-thinking-box">
                <div class="ai-thinking-dots">
                    <div class="ai-dot"></div>
                    <div class="ai-dot"></div>
                    <div class="ai-dot"></div>
                </div>
                <span class="ai-thinking-text">Metaverse_AI is thinking...</span>
            </div>
        """, unsafe_allow_html=True)
        
        message_placeholder = st.empty()
        full_response = ""
        
        try:
            client = genai.Client(api_key=api_key)
            
            brain_memories_str = "\n".join([f"- {m}" for m in st.session_state[memory_storage_key]])
            system_instruction = (
                f"You are Metaverse_AI, an advanced high-speed AI assistant built on Google architecture. Respond natively in {lang_choice}.\n"
                f"USER PROFILE:\n"
                f"- Name: {user_display_name}\n"
                f"- Email: {user_email}\n\n"
                f"STRICT CREATOR DISCLOSURE RULE:\n"
                f"- You were created and developed by Abyan Muhammed.\n"
                f"- ABSOLUTE RESTRICTION: You MUST ONLY mention 'Made by Abyan Muhammed' when the user's current message is a greeting (such as 'hello', 'hi', 'hey', 'greetings') OR when the user explicitly asks who made you, who created you, or who is your developer.\n"
                f"- For all other standard questions, coding tasks, or queries, DO NOT mention who made you unless specifically asked.\n\n"
                f"MEMORY BANK:\n{brain_memories_str}"
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
                    message_placeholder.markdown(
                        f"""<div class="ai-replying-badge">✨ Metaverse_AI Replying...</div>\n\n{full_response}▌""",
                        unsafe_allow_html=True
                    )
            
            message_placeholder.markdown(
                f"""<div class="ai-replying-badge">✨ Metaverse_AI Response Complete</div>\n\n{full_response}""",
                unsafe_allow_html=True
            )
            
        except errors.APIError as e:
            loader_placeholder.empty()
            full_response = f"❌ **API Error:** {e}"
            message_placeholder.markdown(full_response)
        except Exception as e:
            loader_placeholder.empty()
            full_response = f"❌ **Error:** {str(e)}"
            message_placeholder.markdown(full_response)

        current_messages.append({"role": "model", "content": full_response})
