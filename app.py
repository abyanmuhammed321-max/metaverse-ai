import uuid
import streamlit as st
from google import genai
from google.genai import errors
from google.genai import types

# 1. Page Configuration with Adaptive Layout
st.set_page_config(
    page_title="Metaverse_AI",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="auto"
)

# Enforce flawless mobile scaling and viewport containment
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

storage_key = f"metaverse_ai_sessions_{user_email.replace('@', '_at_').replace('.', '_')}"
prefs_storage_key = f"metaverse_ai_prefs_{user_email.replace('@', '_at_').replace('.', '_')}"
memory_storage_key = f"metaverse_ai_memory_{user_email.replace('@', '_at_').replace('.', '_' )}"

# Initialize preferences
if prefs_storage_key not in st.session_state:
    st.session_state[prefs_storage_key] = {
        "selected_model": "gemini-3.1-flash-lite",
        "lang_choice": "English",
        "chat_alignment": "Centered Hologram Card"
    }

# Initialize Memory Bank
if memory_storage_key not in st.session_state:
    st.session_state[memory_storage_key] = [
        "Creator and Master Developer: Abyan Muhammed",
        "Creator Display Rule: Only mention 'Made by Abyan Muhammed' when the user explicitly greets ('hello', 'hi', 'hey') or asks who built/made the AI.",
        "User signed in as Google Identity: " + user_display_name,
        "Core Objective: Futuristic immersive UI with customizable multi-style chat alignments (Centered Hologram Card, Full-Width Cyber Stream, Split Workspace Grid)."
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

# Retrieve current alignment setting
current_alignment = st.session_state[prefs_storage_key].get("chat_alignment", "Centered Hologram Card")

# Dynamic layout structure injection based on alignment preference
if current_alignment == "Full-Width Cyber Stream":
    desktop_container_css = """
        .block-container {
            max-width: 100% !important;
            padding-left: 3rem !important;
            padding-right: 3rem !important;
            padding-top: 2rem !important;
            padding-bottom: 7.5rem !important;
            margin: 0 !important;
        }
        [data-testid="stMain"] > div {
            background: rgba(13, 19, 38, 0.6) !important;
            backdrop-filter: blur(20px) !important;
            border: 1px solid rgba(56, 189, 248, 0.2) !important;
            border-radius: 24px !important;
            padding: 32px !important;
            margin: 12px 0 !important;
            width: 100% !important;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5) !important;
        }
    """
elif current_alignment == "Split Workspace Grid":
    desktop_container_css = """
        .block-container {
            max-width: 1280px !important;
            padding-left: 2.5rem !important;
            padding-right: 2.5rem !important;
            padding-top: 2rem !important;
            padding-bottom: 7.5rem !important;
            margin: 0 auto !important;
        }
        [data-testid="stMain"] > div {
            background: linear-gradient(135deg, rgba(13, 19, 38, 0.85) 0%, rgba(30, 27, 75, 0.85) 100%) !important;
            backdrop-filter: blur(24px) !important;
            border: 1px solid rgba(192, 132, 252, 0.3) !important;
            border-radius: 36px !important;
            padding: 42px !important;
            margin: 16px auto !important;
            width: 100% !important;
            box-shadow: 0 35px 90px rgba(0, 0, 0, 0.8), inset 0 1px 0 rgba(255, 255, 255, 0.15) !important;
        }
    """
else: # Centered Hologram Card (Default)
    desktop_container_css = """
        .block-container {
            max-width: 980px !important;
            padding-left: 2rem !important;
            padding-right: 2rem !important;
            padding-top: 2rem !important;
            padding-bottom: 7.5rem !important;
            margin: 0 auto !important;
        }
        [data-testid="stMain"] > div {
            background: rgba(13, 19, 38, 0.75) !important;
            backdrop-filter: blur(24px) !important;
            border: 1px solid rgba(99, 102, 241, 0.2) !important;
            border-radius: 32px !important;
            padding: 40px !important;
            margin: 16px auto !important;
            width: 100% !important;
            box-shadow: 0 30px 80px rgba(0, 0, 0, 0.7), inset 0 1px 0 rgba(255, 255, 255, 0.1) !important;
        }
    """

# 3. ADVANCED FUTURISTIC UNIFIED STYLING
theme_css = f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;500;600;700&family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');

    html, body {{
        box-sizing: border-box;
        width: 100% !important;
        max-width: 100% !important;
        overflow-x: hidden !important;
        margin: 0 !important;
        padding: 0 !important;
        -webkit-text-size-adjust: 100%;
    }}
    *, *:before, *:after {{
        box-sizing: inherit;
    }}

    .stApp {{
        background: radial-gradient(circle at 50% 0%, #1e1b4b 0%, #090d16 60%, #020617 100%) !important;
        background-attachment: fixed !important;
        color: #f8fafc !important;
        font-family: 'Plus Jakarta Sans', sans-serif;
        width: 100% !important;
    }}

    {desktop_container_css}

    /* Mobile View Strict Responsive Adjustments */
    @media (max-width: 768px) {{
        .block-container {{
            padding-left: 10px !important;
            padding-right: 10px !important;
            padding-top: 1rem !important;
            padding-bottom: 8rem !important;
            margin: 0 !important;
        }}
        [data-testid="stMain"] > div {{
            background: transparent !important;
            backdrop-filter: none !important;
            border: none !important;
            border-radius: 0 !important;
            padding: 10px !important;
            margin: 0 !important;
            box-shadow: none !important;
            width: 100% !important;
        }}
        .gemini-title {{
            font-size: 1.6rem !important;
        }}
        .gemini-subtitle {{
            font-size: 0.75rem !important;
            margin-bottom: 16px !important;
        }}
        .stChatMessage {{
            padding: 14px !important;
            border-radius: 16px !important;
            margin-bottom: 12px !important;
        }}
        [data-testid="stChatInput"] {{
            bottom: 6px !important;
            left: 4px !important;
            right: 4px !important;
            width: calc(100% - 8px) !important;
        }}
    }}

    [data-testid="stSidebar"] {{
        background-color: #030712 !important;
        border-right: 1px solid rgba(99, 102, 241, 0.15) !important;
    }}
    
    [data-testid="stSidebar"] * {{
        color: #f8fafc !important;
    }}

    .gemini-title {{
        font-family: 'Outfit', sans-serif;
        font-size: 2.5rem;
        font-weight: 700;
        background: linear-gradient(135deg, #818cf8 0%, #c084fc 50%, #38bdf8 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 4px;
        letter-spacing: -0.8px;
    }}
    
    .gemini-subtitle {{
        color: #94a3b8;
        font-size: 0.85rem;
        margin-bottom: 28px;
        font-weight: 500;
        letter-spacing: 0.3px;
    }}

    .stChatMessage {{
        background: rgba(23, 32, 59, 0.7) !important;
        backdrop-filter: blur(12px) !important;
        border: 1px solid rgba(99, 102, 241, 0.2) !important;
        border-radius: 22px !important;
        padding: 22px !important;
        margin-bottom: 18px !important;
        box-shadow: 0 12px 30px rgba(0, 0, 0, 0.4) !important;
        word-break: break-word !important;
        overflow-wrap: break-word !important;
        max-width: 100% !important;
    }}

    .stChatMessage p, .stChatMessage span, .stChatMessage div, .stMarkdown {{
        color: #f8fafc !important;
        font-size: 0.96rem !important;
        line-height: 1.65 !important;
        word-break: break-word !important;
        overflow-wrap: break-word !important;
    }}

    .stButton button {{
        border-radius: 14px !important;
        font-family: 'Outfit', sans-serif !important;
        font-weight: 600 !important;
        font-size: 0.84rem !important;
        border: 1px solid rgba(99, 102, 241, 0.35) !important;
        background: linear-gradient(135deg, rgba(30, 27, 75, 0.8), rgba(49, 46, 129, 0.8)) !important;
        color: #f8fafc !important;
        width: 100% !important;
        padding: 10px 16px !important;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3) !important;
        transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1) !important;
    }}
    
    .stButton button:hover {{
        background: linear-gradient(135deg, rgba(49, 46, 129, 1), rgba(67, 56, 202, 1)) !important;
        border-color: #818cf8 !important;
        box-shadow: 0 6px 20px rgba(99, 102, 241, 0.4) !important;
    }}

    [data-testid="stChatInput"] {{
        padding: 0 4px 10px 4px !important;
    }}

    [data-testid="stChatInput"] textarea {{
        background: rgba(15, 23, 42, 0.9) !important;
        color: #f8fafc !important;
        border: 1px solid rgba(99, 102, 241, 0.35) !important;
        border-radius: 24px !important;
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        font-size: 0.96rem !important;
        padding: 16px 22px !important;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.6) !important;
    }}

    .sidebar-signature {{
        text-align: center;
        font-family: 'Outfit', sans-serif;
        font-size: 0.7rem;
        color: #818cf8;
        letter-spacing: 1.5px;
        padding: 14px 4px;
        margin-top: 24px;
        margin-bottom: 24px;
        border-top: 1px solid rgba(99, 102, 241, 0.2);
        border-bottom: 1px solid rgba(99, 102, 241, 0.2);
        text-transform: uppercase;
        background: rgba(99, 102, 241, 0.05);
    }}

    .ai-thinking-box {{
        display: flex;
        align-items: center;
        gap: 10px;
        padding: 14px 20px;
        background: rgba(30, 27, 75, 0.6);
        border: 1px solid rgba(99, 102, 241, 0.3);
        border-radius: 18px;
        width: fit-content;
        margin: 8px 0;
    }}

    .ai-thinking-dots {{
        display: flex;
        gap: 6px;
        align-items: center;
    }}

    .ai-dot {{
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background-color: #818cf8;
        animation: aiDotBounce 1.4s infinite ease-in-out both;
    }}

    .ai-dot:nth-child(1) {{ animation-delay: -0.32s; }}
    .ai-dot:nth-child(2) {{ animation-delay: -0.16s; background-color: #c084fc; }}
    .ai-dot:nth-child(3) {{ animation-delay: 0s; background-color: #38bdf8; }}

    @keyframes aiDotBounce {{
        0%, 80%, 100% {{ transform: scale(0); opacity: 0.4; }}
        40% {{ transform: scale(1.3); opacity: 1; }}
    }}

    .ai-thinking-text {{
        font-family: 'Outfit', sans-serif;
        font-size: 0.88rem;
        font-weight: 600;
        color: #818cf8;
    }}

    .ai-replying-badge {{
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 6px 14px;
        margin-bottom: 12px;
        background: rgba(99, 102, 241, 0.15);
        border: 1px solid rgba(99, 102, 241, 0.35);
        border-radius: 14px;
        font-family: 'Outfit', sans-serif;
        font-size: 0.76rem;
        color: #818cf8;
        font-weight: 600;
    }}
</style>
"""

st.markdown(theme_css, unsafe_allow_html=True)

# 4. Sidebar Navigation & Feature Control
with st.sidebar:
    st.markdown("### ✨ Metaverse_AI Nexus")
    
    if not is_logged_in:
        st.write("<span style='font-size: 0.81rem;'>Sign in with Google to unlock full workspace capabilities.</span>", unsafe_allow_html=True)
        st.button("🔑 Sign in with Google", on_click=st.login, use_container_width=True, type="primary")
    else:
        st.success(f"**{user_display_name}**")
        st.write(f"<span style='font-size: 0.76rem;'>{user_email}</span>", unsafe_allow_html=True)
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
            col1, col2 = st.columns([0.75, 0.25])
            with col1:
                btn_type = "primary" if sid == current_sid else "secondary"
                display_title = sdata["title"][:14] + ("..." if len(sdata["title"]) > 14 else "")
                if st.button(display_title, key=f"sel_{sid}", use_container_width=True, type=btn_type):
                    st.session_state[f"{storage_key}_current_sid"] = sid
                    st.rerun()
            with col2:
                if st.button("🗑️", key=f"del_{sid}", help="Delete chat", use_container_width=True):
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

# 5. Settings Modal Panel (Including new alignment feature selector)
if is_logged_in and st.session_state.get("show_settings_modal", False):
    with st.container():
        st.markdown("""
            <div style="border-radius: 16px; padding: 16px; margin-bottom: 14px;">
                <h3 style="font-family: 'Outfit', sans-serif; margin-top: 0; font-size: 1.1rem;">⚙️ Settings & Preferences</h3>
            </div>
        """, unsafe_allow_html=True)
        
        models_list = ["gemini-3.1-flash-lite", "gemini-2.0-flash", "gemini-2.5-flash", "gemini-2.5-pro"]
        model_index = models_list.index(selected_model) if selected_model in models_list else 0
        selected_model_input = st.selectbox("Model Engine", models_list, index=model_index, key="modal_model_select")

        languages = ["English", "Malayalam", "Hindi", "Spanish", "French", "German", "Japanese", "Chinese", "Arabic"]
        lang_index = languages.index(lang_choice) if lang_choice in languages else 0
        lang_choice_input = st.selectbox("Response Language", languages, index=lang_index, key="modal_lang_select")

        alignments = ["Centered Hologram Card", "Full-Width Cyber Stream", "Split Workspace Grid"]
        current_align_pref = st.session_state[prefs_storage_key].get("chat_alignment", "Centered Hologram Card")
        align_index = alignments.index(current_align_pref) if current_align_pref in alignments else 0
        alignment_choice_input = st.selectbox("Chat Container Alignment", alignments, index=align_index, key="modal_align_select")
        
        col_s1, col_s2 = st.columns(2)
        with col_s1:
            if st.button("Save Changes", use_container_width=True, type="primary"):
                st.session_state[prefs_storage_key]["selected_model"] = selected_model_input
                st.session_state[prefs_storage_key]["lang_choice"] = lang_choice_input
                st.session_state[prefs_storage_key]["chat_alignment"] = alignment_choice_input
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
            <div style="border-radius: 16px; padding: 16px; margin-bottom: 14px;">
                <h3 style="font-family: 'Outfit', sans-serif; margin-top: 0; font-size: 1.1rem;">🧠 Memory & Context</h3>
            </div>
        """, unsafe_allow_html=True)
        
        memory_list = st.session_state[memory_storage_key]
        for idx, mem in enumerate(memory_list):
            col_m1, col_m2 = st.columns([0.82, 0.18])
            with col_m1:
                st.code(mem, language="text")
            with col_m2:
                if st.button("🗑️", key=f"del_mem_{idx}", use_container_width=True):
                    memory_list.pop(idx)
                    st.rerun()

        if st.button("Close Memory Bank", use_container_width=True):
            st.session_state["show_brain_modal"] = False
            st.rerun()
        st.markdown("---")

# Refresh preferences
selected_model = st.session_state[prefs_storage_key].get("selected_model", "gemini-3.1-flash-lite")
lang_choice = st.session_state[prefs_storage_key].get("lang_choice", "English")
current_alignment = st.session_state[prefs_storage_key].get("chat_alignment", "Centered Hologram Card")

# 7. Main Canvas Layout
st.markdown(f'<div class="gemini-title">Metaverse_AI</div>', unsafe_allow_html=True)
st.markdown(f'<div class="gemini-subtitle">Engine: {selected_model} • Layout: {current_alignment} • Language: {lang_choice}</div>', unsafe_allow_html=True)

if not is_logged_in:
    st.markdown("""
        <div style="border-radius: 24px; padding: 32px; text-align: center; margin-top: 20px; background: rgba(23, 32, 59, 0.4); border: 1px solid rgba(99, 102, 241, 0.2);">
            <h2 style="font-family: 'Outfit', sans-serif; font-size: 1.35rem; margin-bottom: 12px;">Welcome to Metaverse_AI</h2>
            <p style="font-size: 0.95rem; line-height: 1.6; margin-bottom: 24px; color: #94a3b8;">
                Please sign in from the sidebar to activate your immersive workspace and begin your AI journey.
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
        current_session_data["title"] = prompt[:18]

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
