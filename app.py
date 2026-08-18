import uuid
import streamlit as st
from google import genai
from google.genai import errors
from google.genai import types

# 1. Page Configuration (Optimized for Modern Minimalist Layout & Speed)
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

# Initialize default preferences (Defaulting to ultra-fast flash model)
if prefs_storage_key not in st.session_state:
    st.session_state[prefs_storage_key] = {
        "selected_model": "gemini-2.0-flash",
        "lang_choice": "English"
    }

# Initialize Persistent Brain / Memory Bank
if memory_storage_key not in st.session_state:
    st.session_state[memory_storage_key] = [
        "Creator and Master Developer: Abyan Muhammed",
        "Creator Display Rule: Only mention 'Made by Abyan Muhammed' when the user explicitly greets ('hello', 'hi', 'hey') or asks who built/made the AI.",
        "User signed in as Google Identity: " + user_display_name,
        "Core Objective: Deliver a lightning-fast, futuristic experience inspired by modern AI aesthetics."
    ]

# 2. Comprehensive Persistent Storage (Chats & State Sync)
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

# Initialize Settings & Brain Modal State
if "show_settings_modal" not in st.session_state:
    st.session_state["show_settings_modal"] = False

if "show_brain_modal" not in st.session_state:
    st.session_state["show_brain_modal"] = False

# 3. Enhanced Ultra-Futuristic UI with Full-Screen Neon Background, Dynamic Grid & High-Speed Optimizations
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Google+Sans:wght@400;500;600;700&family=Inter:wght@400;500;600&display=swap');

    /* --- FULL SCREEN 4-COLOR ANIMATED NEON GRADIENT BASE --- */
    html, body, [data-testid="stAppViewContainer"], [data-testid="stMain"], .stApp {
        background: linear-gradient(135deg, #070913, #100b17, #0b131a, #170b16) !important;
        background-size: 400% 400% !important;
        animation: ultimateNeonFlow 8s ease infinite !important;
        color: #e3e3e3 !important;
        font-family: 'Google Sans', 'Inter', sans-serif;
        min-height: 100vh;
        overflow-x: hidden;
    }

    @keyframes ultimateNeonFlow {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    /* --- FULL VIEWPORT ANIMATED NEON ORBS --- */
    @keyframes orbMotion1 {
        0% { transform: translate(0px, 0px) scale(1); opacity: 0.5; }
        33% { transform: translate(350px, 450px) scale(1.6); opacity: 0.7; }
        66% { transform: translate(-200px, 300px) scale(1.35); opacity: 0.55; }
        100% { transform: translate(0px, 0px) scale(1); opacity: 0.5; }
    }

    @keyframes orbMotion2 {
        0% { transform: translate(0px, 0px) scale(1); opacity: 0.5; }
        33% { transform: translate(-400px, -350px) scale(1.7); opacity: 0.7; }
        66% { transform: translate(-250px, 220px) scale(1.4); opacity: 0.6; }
        100% { transform: translate(0px, 0px) scale(1); opacity: 0.5; }
    }

    @keyframes centerCorePulse {
        0% { transform: translate(-50%, -50%) scale(1); opacity: 0.4; filter: hue-rotate(0deg); }
        50% { transform: translate(-50%, -50%) scale(1.45); opacity: 0.65; filter: hue-rotate(180deg); }
        100% { transform: translate(-50%, -50%) scale(1); opacity: 0.4; filter: hue-rotate(360deg); }
    }

    .stApp::after {
        content: "";
        position: fixed;
        top: -300px;
        left: -300px;
        width: 900px;
        height: 900px;
        background: radial-gradient(circle, rgba(66, 133, 244, 0.75) 0%, rgba(52, 168, 83, 0.4) 50%, transparent 75%);
        border-radius: 50%;
        pointer-events: none;
        z-index: 1;
        animation: orbMotion1 7s infinite ease-in-out;
    }

    .stApp::before {
        content: "";
        position: fixed;
        bottom: -300px;
        right: -300px;
        width: 950px;
        height: 950px;
        background: radial-gradient(circle, rgba(234, 67, 53, 0.7) 0%, rgba(251, 188, 5, 0.45) 50%, transparent 75%);
        border-radius: 50%;
        pointer-events: none;
        z-index: 1;
        animation: orbMotion2 9s infinite ease-in-out;
    }

    .neon-center-pulsar {
        position: fixed;
        top: 50%;
        left: 50%;
        width: 800px;
        height: 800px;
        background: radial-gradient(circle, rgba(138, 43, 226, 0.45) 0%, rgba(0, 255, 255, 0.3) 55%, transparent 80%);
        border-radius: 50%;
        pointer-events: none;
        z-index: 1;
        transform: translate(-50%, -50%);
        animation: centerCorePulse 10s infinite ease-in-out;
    }

    /* --- SCANNING NEON GRID OVERLAY --- */
    @keyframes gridScanMotion {
        0% { background-position: 0 0, 0 0; }
        100% { background-position: 50px 50px, 50px 50px; }
    }

    .neon-grid-overlay {
        position: fixed;
        top: 0;
        left: 0;
        width: 100vw;
        height: 100vh;
        background-image: 
            linear-gradient(rgba(255, 255, 255, 0.04) 1px, transparent 1px),
            linear-gradient(90deg, rgba(255, 255, 255, 0.04) 1px, transparent 1px);
        background-size: 45px 45px;
        pointer-events: none;
        z-index: 1;
        animation: gridScanMotion 15s linear infinite;
    }

    /* --- SIDEBAR SCROLL OPTIMIZATION & GLASS STYLE --- */
    [data-testid="stSidebar"] {
        background-color: rgba(15, 17, 23, 0.9) !important;
        backdrop-filter: blur(18px);
        border-right: 1px solid rgba(255, 255, 255, 0.12);
        z-index: 1000;
        overflow-y: auto !important;
        max-height: 100vh !important;
        -webkit-overflow-scrolling: touch;
    }
    
    [data-testid="stSidebar"] * {
        color: #e3e3e3 !important;
    }

    /* --- MODERN CLEAN TYPOGRAPHY HEADER --- */
    .gemini-title {
        font-family: 'Google Sans', sans-serif;
        font-size: clamp(1.6rem, 5vw, 2.4rem);
        font-weight: 600;
        background: linear-gradient(90deg, #4285f4, #ea4335, #fbbc05, #34a853);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0px;
        padding-top: 10px;
        letter-spacing: -0.5px;
        position: relative;
        z-index: 2;
    }
    
    .gemini-subtitle {
        color: #b0b3b0;
        font-size: clamp(0.75rem, 2vw, 0.85rem);
        margin-bottom: 25px;
        font-weight: 500;
        position: relative;
        z-index: 2;
    }

    /* --- MINIMALIST CLEAN CHAT BUBBLES WITH GLASSMORPHISM --- */
    .stChatMessage {
        background-color: rgba(20, 22, 30, 0.85) !important;
        backdrop-filter: blur(14px);
        border: 1px solid rgba(255, 255, 255, 0.15) !important;
        border-radius: 16px !important;
        padding: 16px !important;
        margin-bottom: 16px !important;
        box-shadow: 0 10px 35px rgba(0,0,0,0.55);
        position: relative;
        z-index: 2;
    }

    .stChatMessage p, .stChatMessage span, .stChatMessage div, .stMarkdown {
        color: #e3e3e3 !important;
        font-size: 0.98rem !important;
        line-height: 1.6 !important;
    }

    /* --- MODERN ROUNDED BUTTONS --- */
    .stButton button {
        border-radius: 20px !important;
        font-family: 'Google Sans', sans-serif !important;
        font-weight: 500 !important;
        font-size: 0.82rem !important;
        border: 1px solid rgba(255, 255, 255, 0.18) !important;
        background-color: rgba(30, 34, 44, 0.9) !important;
        color: #e3e3e3 !important;
        transition: all 0.2s ease !important;
        position: relative;
        z-index: 2;
    }
    
    .stButton button:hover {
        background-color: rgba(50, 55, 70, 0.95) !important;
        border-color: #8ab4f8 !important;
        box-shadow: 0 0 20px rgba(66, 133, 244, 0.65);
    }

    /* --- FLOATING CHAT INPUT BOX STYLE WITH GEMINI SPARKLE BORDER GLOW --- */
    @keyframes inputNeonBorderGlow {
        0% { border-color: rgba(66, 133, 244, 0.6); box-shadow: 0 0 14px rgba(66, 133, 244, 0.3); }
        33% { border-color: rgba(234, 67, 53, 0.6); box-shadow: 0 0 18px rgba(234, 67, 53, 0.4); }
        66% { border-color: rgba(251, 188, 5, 0.6); box-shadow: 0 0 18px rgba(251, 188, 5, 0.4); }
        100% { border-color: rgba(52, 168, 83, 0.6); box-shadow: 0 0 14px rgba(52, 168, 83, 0.3); }
    }

    [data-testid="stChatInput"] {
        padding: 0 10px 10px 10px !important;
        position: relative;
        z-index: 2;
    }

    [data-testid="stChatInput"] textarea {
        background-color: rgba(16, 18, 26, 0.95) !important;
        backdrop-filter: blur(14px);
        color: #e3e3e3 !important;
        border: 1.5px solid rgba(255, 255, 255, 0.25) !important;
        border-radius: 24px !important;
        font-family: 'Google Sans', sans-serif !important;
        font-size: 0.95rem !important;
        padding: 12px 18px !important;
        box-shadow: 0 10px 35px rgba(0,0,0,0.65);
        animation: inputNeonBorderGlow 6s infinite ease-in-out;
    }

    /* --- CREATOR SIGNATURE IN SIDEBAR --- */
    .sidebar-signature {
        text-align: center;
        font-family: 'Google Sans', sans-serif;
        font-size: 0.72rem;
        color: #b0b3b0;
        letter-spacing: 0.5px;
        padding: 12px 5px;
        margin-top: 30px;
        margin-bottom: 30px;
        border-top: 1px solid rgba(255, 255, 255, 0.1);
        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        text-transform: uppercase;
    }

    /* --- AUTHENTIC GEMINI MULTICOLOR SPARKLE LOADING ANIMATION --- */
    .gemini-loading-container {
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 14px 18px;
        background-color: rgba(20, 22, 30, 0.9);
        backdrop-filter: blur(14px);
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 16px;
        width: fit-content;
        margin: 10px 0;
        box-shadow: 0 10px 30px rgba(0,0,0,0.45);
        position: relative;
        z-index: 2;
    }

    @keyframes geminiSparkleGlow {
        0% { transform: scale(0.85) rotate(0deg); filter: drop-shadow(0 0 4px #4285f4); opacity: 0.7; }
        50% { transform: scale(1.35) rotate(180deg); filter: drop-shadow(0 0 18px #ea4335) drop-shadow(0 0 26px #fbbc05); opacity: 1; }
        100% { transform: scale(0.85) rotate(360deg); filter: drop-shadow(0 0 4px #34a853); opacity: 0.7; }
    }

    .gemini-sparkle-loader {
        font-size: 1.4rem;
        display: inline-block;
        animation: geminiSparkleGlow 1.5s infinite ease-in-out;
    }

    @keyframes geminiTextShimmer {
        0% { background-position: -200% 0; }
        100% { background-position: 200% 0; }
    }

    .gemini-loading-text {
        font-family: 'Google Sans', sans-serif;
        font-size: 0.9rem;
        font-weight: 500;
        background: linear-gradient(90deg, #4285f4, #ea4335, #fbbc05, #34a853, #4285f4);
        background-size: 200% auto;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: geminiTextShimmer 2s linear infinite;
    }

    .ai-streaming-badge {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        padding: 4px 12px;
        margin-bottom: 10px;
        background-color: rgba(66, 133, 244, 0.2);
        border: 1px solid rgba(66, 133, 244, 0.5);
        border-radius: 12px;
        font-family: 'Google Sans', sans-serif;
        font-size: 0.75rem;
        color: #8ab4f8;
    }
</style>

<!-- Injecting Dual-Layer Animated Background Elements -->
<div class="neon-grid-overlay"></div>
<div class="neon-center-pulsar"></div>
""", unsafe_allow_html=True)

# 4. Sidebar Navigation & Feature Control
with st.sidebar:
    st.markdown("### ✨ Metaverse_AI Workspace")
    
    if not is_logged_in:
        st.write("<span style='font-size: 0.8rem; color: #b0b3b0;'>Sign in with Google to unlock all features and chats.</span>", unsafe_allow_html=True)
        st.button("🔑 Sign in with Google", on_click=st.login, use_container_width=True, type="primary")
    else:
        st.success(f"**{user_display_name}**")
        st.write(f"<span style='font-size: 0.75rem; color: #b0b3b0;'>{user_email}</span>", unsafe_allow_html=True)
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

    # Sidebar Creator Signature
    st.markdown(
        """<div class="sidebar-signature">
        MADE BY ABYAN MUHAMMED
        </div>""",
        unsafe_allow_html=True
    )

if not api_key:
    st.error("⚠️ GEMINI_API_KEY configuration missing in `.streamlit/secrets.toml`.")
    st.stop()

selected_model = st.session_state[prefs_storage_key].get("selected_model", "gemini-2.0-flash")
lang_choice = st.session_state[prefs_storage_key].get("lang_choice", "English")

# 5. Settings Modal Panel
if is_logged_in and st.session_state.get("show_settings_modal", False):
    with st.container():
        st.markdown("""
            <div style="background-color: rgba(20, 22, 30, 0.95); backdrop-filter: blur(14px); border: 1px solid rgba(255, 255, 255, 0.2); border-radius: 16px; padding: 20px; margin-bottom: 20px; position: relative; z-index: 2;">
                <h3 style="font-family: 'Google Sans', sans-serif; color: #e3e3e3; margin-top: 0; font-size: 1.1rem;">⚙️ Settings & Preferences</h3>
            </div>
        """, unsafe_allow_html=True)
        
        models_list = ["gemini-2.0-flash", "gemini-2.5-flash", "gemini-3.1-flash-lite", "gemini-2.5-pro"]
        model_index = models_list.index(selected_model) if selected_model in models_list else 0
        selected_model_input = st.selectbox("Model Engine (Fast Flash Recommended)", models_list, index=model_index, key="modal_model_select")

        languages = ["English", "Malayalam", "Spanish", "French", "German", "Hindi", "Japanese", "Chinese", "Arabic"]
        lang_index = languages.index(lang_choice) if lang_choice in languages else 0
        lang_choice_input = st.selectbox("Response Language", languages, index=lang_index, key="modal_lang_select")
        
        col_s1, col_s2 = st.columns(2)
        with col_s1:
            if st.button("Save Changes", use_container_width=True, type="primary"):
                st.session_state[prefs_storage_key]["selected_model"] = selected_model_input
                st.session_state[prefs_storage_key]["lang_choice"] = lang_choice_input
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
            <div style="background-color: rgba(20, 22, 30, 0.95); backdrop-filter: blur(14px); border: 1px solid rgba(255, 255, 255, 0.2); border-radius: 16px; padding: 20px; margin-bottom: 20px; position: relative; z-index: 2;">
                <h3 style="font-family: 'Google Sans', sans-serif; color: #e3e3e3; margin-top: 0; font-size: 1.1rem;">🧠 Memory & Context</h3>
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
selected_model = st.session_state[prefs_storage_key].get("selected_model", "gemini-2.0-flash")
lang_choice = st.session_state[prefs_storage_key].get("lang_choice", "English")

# 7. Main Canvas Layout
st.markdown(f'<div class="gemini-title">Metaverse_AI</div>', unsafe_allow_html=True)
st.markdown(f'<div class="gemini-subtitle">Engine: {selected_model} (Ultra-Fast Stream) • Language: {lang_choice}</div>', unsafe_allow_html=True)

# Feature gate: Hide all chat capabilities when logged out
if not is_logged_in:
    st.markdown("""
        <div style="background-color: rgba(20, 22, 30, 0.85); backdrop-filter: blur(14px); border: 1px solid rgba(255, 255, 255, 0.2); border-radius: 16px; padding: 35px; text-align: center; margin-top: 40px; position: relative; z-index: 2;">
            <h2 style="font-family: 'Google Sans', sans-serif; color: #e3e3e3; font-size: 1.3rem; margin-bottom: 15px;">Welcome to Metaverse_AI</h2>
            <p style="color: #b0b3b0; font-size: 0.95rem; line-height: 1.6; margin-bottom: 25px;">
                Please sign in from the sidebar to access your workspace, start conversations, and interact with advanced AI features.
            </p>
        </div>
    """, unsafe_allow_html=True)
    st.stop()

current_messages = current_session_data["messages"]

for message in current_messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 8. Realtime High-Speed Message Handling & Creator Rules
if prompt := st.chat_input("Enter a prompt here..."):
    if len(current_messages) == 0:
        current_session_data["title"] = prompt[:22]

    current_messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        loader_placeholder = st.empty()
        loader_placeholder.markdown("""
            <div class="gemini-loading-container">
                <span class="gemini-sparkle-loader">✨</span>
                <span class="gemini-loading-text">Instant processing...</span>
            </div>
        """, unsafe_allow_html=True)
        
        message_placeholder = st.empty()
        full_response = ""
        
        try:
            client = genai.Client(api_key=api_key)
            
            brain_memories_str = "\n".join([f"- {m}" for m in st.session_state[memory_storage_key]])
            system_instruction = (
                f"You are Metaverse_AI, an advanced ultra-fast AI assistant built on Google architecture. Respond natively in {lang_choice}.\n"
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
                        f"""<div class="ai-streaming-badge"><span class="gemini-sparkle-loader" style="font-size: 0.9rem;">✨</span>Metaverse_AI</div>\n\n{full_response}▌""",
                        unsafe_allow_html=True
                    )
            
            message_placeholder.markdown(full_response)
            
        except errors.APIError as e:
            loader_placeholder.empty()
            full_response = f"❌ **API Error:** {e}"
            message_placeholder.markdown(full_response)
        except Exception as e:
            loader_placeholder.empty()
            full_response = f"❌ **Error:** {str(e)}"
            message_placeholder.markdown(full_response)

        current_messages.append({"role": "model", "content": full_response})
