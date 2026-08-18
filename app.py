import uuid
import streamlit as st
from google import genai
from google.genai import errors
from google.genai import types

# 1. Page Configuration (Optimized for Modern Minimalist Layout)
st.set_page_config(
    page_title="METAVERSE AI",
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

# Initialize default preferences
if prefs_storage_key not in st.session_state:
    st.session_state[prefs_storage_key] = {
        "selected_model": "gemini-3.1-flash-lite",
        "lang_choice": "English"
    }

# Initialize Persistent Brain / Memory Bank
if memory_storage_key not in st.session_state:
    st.session_state[memory_storage_key] = [
        "Creator and Master Developer: Abyan Muhammed",
        "Creator Display Rule: Only mention 'Made by Abyan Muhammed' when the user explicitly greets ('hello', 'hi', 'hey') or asks who built/made the AI.",
        "User signed in as Google Identity: " + user_display_name,
        "Core Objective: Deliver a pristine, futuristic experience inspired by modern AI aesthetics."
    ]

# 2. Comprehensive Persistent Storage (Chats & State Sync)
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

# Initialize Settings & Brain Modal State
if "show_settings_modal" not in st.session_state:
    st.session_state["show_settings_modal"] = False

if "show_brain_modal" not in st.session_state:
    st.session_state["show_brain_modal"] = False

# 3. Modern Gemini-Inspired Clean UI Style with Smooth Mobile-Optimized Neon Border Animation & Scrolling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Google+Sans:wght@400;500;600;700&family=Inter:wght@400;500;600&display=swap');

    .stApp {
        background-color: #131314 !important;
        color: #e3e3e3 !important;
        font-family: 'Google Sans', 'Inter', sans-serif;
        position: relative;
        min-height: 100vh;
    }

    /* --- SLEEK CONTINUOUS MOVING NEON EDGE BORDER ANIMATION (ALL EDGES) --- */
    @keyframes moveNeonBorder {
        0% {
            border-color: #4285f4;
            box-shadow: inset 0 0 30px rgba(66, 133, 244, 0.2), 0 0 20px rgba(66, 133, 244, 0.4);
        }
        33% {
            border-color: #ea4335;
            box-shadow: inset 0 0 30px rgba(234, 67, 53, 0.2), 0 0 20px rgba(234, 67, 53, 0.4);
        }
        66% {
            border-color: #fbbc05;
            box-shadow: inset 0 0 30px rgba(251, 188, 5, 0.2), 0 0 20px rgba(251, 188, 5, 0.4);
        }
        100% {
            border-color: #4285f4;
            box-shadow: inset 0 0 30px rgba(66, 133, 244, 0.2), 0 0 20px rgba(66, 133, 244, 0.4);
        }
    }

    .stApp::before {
        content: "";
        position: fixed;
        top: 0;
        left: 0;
        width: 100vw;
        height: 100vh;
        border: 3px solid #4285f4;
        pointer-events: none;
        z-index: 999;
        animation: moveNeonBorder 6s infinite linear;
        border-radius: 4px;
    }

    /* --- SIDEBAR SCROLL OPTIMIZATION FOR PHONES & MOBILE DEVICES --- */
    [data-testid="stSidebar"] {
        background-color: #1e1f20 !important;
        border-right: 1px solid #333537;
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
    }
    
    .gemini-subtitle {
        color: #8e918f;
        font-size: clamp(0.75rem, 2vw, 0.85rem);
        margin-bottom: 25px;
        font-weight: 500;
    }

    /* --- MINIMALIST CLEAN CHAT BUBBLES --- */
    .stChatMessage {
        background-color: #1e1f20 !important;
        border: 1px solid #333537 !important;
        border-radius: 16px !important;
        padding: 16px !important;
        margin-bottom: 16px !important;
        box-shadow: 0 1px 3px rgba(0,0,0,0.3);
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
        border: 1px solid #444746 !important;
        background-color: #28292a !important;
        color: #e3e3e3 !important;
        transition: all 0.2s ease !important;
    }
    
    .stButton button:hover {
        background-color: #333537 !important;
        border-color: #8e918f !important;
    }

    /* --- FLOATING CHAT INPUT BOX STYLE --- */
    [data-testid="stChatInput"] {
        padding: 0 10px 10px 10px !important;
    }

    [data-testid="stChatInput"] textarea {
        background-color: #1e1f20 !important;
        color: #e3e3e3 !important;
        border: 1px solid #444746 !important;
        border-radius: 24px !important;
        font-family: 'Google Sans', sans-serif !important;
        font-size: 0.95rem !important;
        padding: 12px 16px !important;
    }

    /* --- CREATOR SIGNATURE IN SIDEBAR --- */
    .sidebar-signature {
        text-align: center;
        font-family: 'Google Sans', sans-serif;
        font-size: 0.72rem;
        color: #8e918f;
        letter-spacing: 0.5px;
        padding: 12px 5px;
        margin-top: 30px;
        margin-bottom: 30px;
        border-top: 1px solid #333537;
        border-bottom: 1px solid #333537;
        text-transform: uppercase;
    }

    /* --- STREAMING & LOADING INDICATORS --- */
    .ai-streaming-badge {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        padding: 4px 12px;
        margin-bottom: 10px;
        background-color: rgba(66, 133, 244, 0.1);
        border: 1px solid rgba(66, 133, 244, 0.3);
        border-radius: 12px;
        font-family: 'Google Sans', sans-serif;
        font-size: 0.75rem;
        color: #8ab4f8;
    }

    .sparkle-icon {
        display: inline-block;
        animation: pulseSparkle 1.5s infinite ease-in-out;
    }

    @keyframes pulseSparkle {
        0%, 100% { transform: scale(1); opacity: 0.7; }
        50% { transform: scale(1.2); opacity: 1; }
    }

    .gemini-loader {
        display: flex;
        align-items: center;
        gap: 10px;
        padding: 12px 16px;
        background-color: #1e1f20;
        border: 1px solid #333537;
        border-radius: 12px;
        width: fit-content;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

# 4. Sidebar Navigation & Feature Control
with st.sidebar:
    st.markdown("### ✨ GEMINI WORKSPACE")
    
    if not is_logged_in:
        st.write("<span style='font-size: 0.8rem; color: #8e918f;'>Sign in with Google to unlock all features and chats.</span>", unsafe_allow_html=True)
        st.button("🔑 Sign in with Google", on_click=st.login, use_container_width=True, type="primary")
    else:
        st.success(f"**{user_display_name}**")
        st.write(f"<span style='font-size: 0.75rem; color: #8e918f;'>{user_email}</span>", unsafe_allow_html=True)
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
        
        if st.button("➕ New Chat", use_container_width=True, type="primary"):
            new_sid = str(uuid.uuid4())
            st.session_state[storage_key][new_sid] = {
                "title": "New Chat",
                "messages": []
            }
            st.session_state[f"{storage_key}_current_sid"] = new_sid
            st.rerun()
            
        st.markdown("### 💬 RECENT CHATS")
        
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
                        st.session_state[storage_key][fresh_sid] = {"title": "New Chat", "messages": []}
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

selected_model = st.session_state[prefs_storage_key].get("selected_model", "gemini-3.1-flash-lite")
lang_choice = st.session_state[prefs_storage_key].get("lang_choice", "English")

# 5. Settings Modal Panel
if is_logged_in and st.session_state.get("show_settings_modal", False):
    with st.container():
        st.markdown("""
            <div style="background-color: #1e1f20; border: 1px solid #333537; border-radius: 16px; padding: 20px; margin-bottom: 20px;">
                <h3 style="font-family: 'Google Sans', sans-serif; color: #e3e3e3; margin-top: 0; font-size: 1.1rem;">⚙️ Settings & Preferences</h3>
            </div>
        """, unsafe_allow_html=True)
        
        models_list = ["gemini-3.1-flash-lite", "gemini-2.5-flash", "gemini-2.5-pro", "gemini-2.0-flash"]
        model_index = models_list.index(selected_model) if selected_model in models_list else 0
        selected_model_input = st.selectbox("Model Engine", models_list, index=model_index, key="modal_model_select")

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
            <div style="background-color: #1e1f20; border: 1px solid #333537; border-radius: 16px; padding: 20px; margin-bottom: 20px;">
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
selected_model = st.session_state[prefs_storage_key].get("selected_model", "gemini-3.1-flash-lite")
lang_choice = st.session_state[prefs_storage_key].get("lang_choice", "English")

# 7. Main Canvas Layout
st.markdown(f'<div class="gemini-title">Gemini</div>', unsafe_allow_html=True)
st.markdown(f'<div class="gemini-subtitle">Engine: {selected_model} • Language: {lang_choice}</div>', unsafe_allow_html=True)

# Feature gate: Hide all chat capabilities when logged out
if not is_logged_in:
    st.markdown("""
        <div style="background-color: #1e1f20; border: 1px solid #333537; border-radius: 16px; padding: 35px; text-align: center; margin-top: 40px;">
            <h2 style="font-family: 'Google Sans', sans-serif; color: #e3e3e3; font-size: 1.3rem; margin-bottom: 15px;">Welcome to Gemini</h2>
            <p style="color: #8e918f; font-size: 0.95rem; line-height: 1.6; margin-bottom: 25px;">
                Please sign in from the sidebar to access your workspace, start conversations, and interact with advanced AI features.
            </p>
        </div>
    """, unsafe_allow_html=True)
    st.stop()

current_messages = current_session_data["messages"]

for message in current_messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 8. Realtime Message Handling & Creator Rules
if prompt := st.chat_input("Enter a prompt here..."):
    if len(current_messages) == 0:
        current_session_data["title"] = prompt[:22]

    current_messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        loader_placeholder = st.empty()
        loader_placeholder.markdown("""
            <div class="gemini-loader">
                <span class="sparkle-icon">✨</span>
                <span style="font-size: 0.85rem; color: #8e918f;">Thinking...</span>
            </div>
        """, unsafe_allow_html=True)
        
        message_placeholder = st.empty()
        full_response = ""
        
        try:
            client = genai.Client(api_key=api_key)
            
            brain_memories_str = "\n".join([f"- {m}" for m in st.session_state[memory_storage_key]])
            system_instruction = (
                f"You are Gemini, a large language model built by Google. Respond natively in {lang_choice}.\n"
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
                        f"""<div class="ai-streaming-badge"><span class="sparkle-icon">✨</span>Gemini</div>\n\n{full_response}▌""",
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
