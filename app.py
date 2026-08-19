import uuid
import streamlit as st
from google import genai
from google.genai import errors
from google.genai import types

# 1. Page Configuration & Adaptive Layout
st.set_page_config(
    page_title="Metaverse_AI",
    page_icon="👑",
    layout="wide",
    initial_sidebar_state="auto"
)

# Enforce strict mobile viewport containment and scaling
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
memory_storage_key = f"metaverse_ai_memory_{user_email.replace('@', '_at_').replace('.', '_')}"

# Initialize preferences
if prefs_storage_key not in st.session_state:
    st.session_state[prefs_storage_key] = {
        "selected_model": "gemini-3.5-flash-lite",
        "lang_choice": "English",
        "chat_alignment": "Executive Split View"
    }

# Initialize Memory Bank
if memory_storage_key not in st.session_state:
    st.session_state[memory_storage_key] = [
        "Creator and Master Developer: Abyan Muhammed",
        "Creator Display Rule: Only mention 'Made by Abyan Muhammed' when the user explicitly greets ('hello', 'hi', 'hey') or asks who built/made the AI.",
        "User signed in as Google Identity: " + user_display_name,
        "Core Objective: Modern Executive Split-Screen Login Layout with absolute mobile clarity."
    ]

if storage_key not in st.session_state:
    first_sid = str(uuid.uuid4())
    st.session_state[storage_key] = {
        first_sid: {
            "title": "Executive Stream",
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

current_alignment = st.session_state[prefs_storage_key].get("chat_alignment", "Executive Split View")

# Container CSS Configurations
desktop_container_css = """
    .block-container {
        max-width: 1320px !important;
        padding-left: 3rem !important;
        padding-right: 3rem !important;
        padding-top: 2rem !important;
        padding-bottom: 7.5rem !important;
        margin: 0 auto !important;
    }
    [data-testid="stMain"] > div {
        background: #0f172a !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-top: 3px solid #38bdf8 !important;
        border-radius: 24px !important;
        padding: 48px !important;
        margin: 16px auto !important;
        width: 100% !important;
        box-shadow: 0 20px 50px rgba(0, 0, 0, 0.5) !important;
    }
"""

# 3. EXECUTIVE SPLIT STYLING & SIGN-IN LAYOUT
theme_css = f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Inter:wght@400;500;600;700&display=swap');

    html, body, [data-testid="stAppViewContainer"], [data-testid="stMain"] {{
        box-sizing: border-box !important;
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
        background: #090d16 !important;
        background-attachment: fixed !important;
        color: #f8fafc !important;
        font-family: 'Plus Jakarta Sans', sans-serif;
        width: 100% !important;
        overflow-x: hidden !important;
    }}

    {desktop_container_css}

    /* Strict Mobile Screen Optimization (< 768px) */
    @media (max-width: 768px) {{
        .block-container {{
            max-width: 100% !important;
            padding-left: 8px !important;
            padding-right: 8px !important;
            padding-top: 1rem !important;
            padding-bottom: 8rem !important;
            margin: 0 !important;
        }}
        [data-testid="stMain"] > div {{
            background: #0f172a !important;
            border: 1px solid rgba(255, 255, 255, 0.08) !important;
            border-top: 3px solid #38bdf8 !important;
            border-radius: 16px !important;
            padding: 16px 12px !important;
            margin: 15px auto 0 auto !important;
            box-shadow: 0 10px 25px rgba(0, 0, 0, 0.5) !important;
            width: 100% !important;
        }}
        
        .exec-title-container {{
            text-align: center !important;
            width: 100% !important;
            display: block !important;
            padding-top: 4px !important;
            margin-bottom: 12px !important;
        }}
        .exec-title {{
            font-size: 1.5rem !important;
            letter-spacing: -0.3px !important;
            line-height: 1.2 !important;
            text-align: center !important;
            white-space: nowrap !important;
            display: block !important;
            width: 100% !important;
            margin: 0 auto !important;
        }}
        .exec-subtitle {{
            font-size: 0.58rem !important;
            margin-bottom: 12px !important;
            letter-spacing: 0.5px !important;
            text-align: center !important;
            display: flex !important;
            flex-wrap: wrap !important;
            justify-content: center !important;
            gap: 2px 6px !important;
            width: 100% !important;
        }}
        .stChatMessage {{
            padding: 12px !important;
            border-radius: 14px !important;
            margin-bottom: 10px !important;
            width: 100% !important;
            word-break: break-word !important;
        }}
        [data-testid="stChatInput"] {{
            position: fixed !important;
            bottom: 0px !important;
            left: 0px !important;
            right: 0px !important;
            width: 100% !important;
            padding: 6px 8px 12px 8px !important;
            background: #090d16 !important;
            backdrop-filter: blur(15px) !important;
            z-index: 99999 !important;
            border-top: 1px solid rgba(255, 255, 255, 0.08) !important;
        }}
    }}

    [data-testid="stSidebar"] {{
        background-color: #05080f !important;
        border-right: 1px solid rgba(255, 255, 255, 0.08) !important;
    }}
    
    [data-testid="stSidebar"] * {{
        color: #f8fafc !important;
    }}

    .exec-title {{
        font-family: 'Inter', sans-serif;
        font-size: 2.4rem;
        font-weight: 800;
        color: #ffffff;
        margin-bottom: 4px;
        letter-spacing: -1px;
    }}
    
    .exec-subtitle {{
        color: #64748b;
        font-size: 0.8rem;
        margin-bottom: 24px;
        font-weight: 600;
        letter-spacing: 0.8px;
        text-transform: uppercase;
        font-family: 'Inter', sans-serif;
    }}

    /* Executive Split Login Box */
    .exec-auth-container {{
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-left: 4px solid #38bdf8;
        border-radius: 20px;
        padding: 40px 36px;
        margin: 20px auto 30px auto;
        max-width: 600px;
        box-shadow: 0 15px 35px rgba(0, 0, 0, 0.4);
    }}

    .exec-auth-badge {{
        font-size: 2rem;
        margin-bottom: 14px;
    }}

    .exec-auth-title {{
        font-family: 'Inter', sans-serif;
        font-size: 1.3rem;
        font-weight: 700;
        color: #ffffff;
        margin-bottom: 8px;
        letter-spacing: -0.3px;
    }}

    .exec-auth-desc {{
        font-size: 0.9rem;
        line-height: 1.6;
        color: #94a3b8;
        margin-bottom: 24px;
    }}

    .stChatMessage {{
        background: #1e293b !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 16px !important;
        padding: 20px !important;
        margin-bottom: 18px !important;
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.3) !important;
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
        border-radius: 12px !important;
        font-family: 'Inter', sans-serif !important;
        font-weight: 600 !important;
        font-size: 0.88rem !important;
        letter-spacing: 0.3px !important;
        border: 1px solid rgba(56, 189, 248, 0.4) !important;
        background: #38bdf8 !important;
        color: #0f172a !important;
        width: 100% !important;
        padding: 12px 20px !important;
        box-shadow: 0 4px 15px rgba(56, 189, 248, 0.25) !important;
        transition: all 0.2s ease-in-out !important;
    }}
    
    .stButton button:hover {{
        background: #7dd3fc !important;
        border-color: #38bdf8 !important;
        box-shadow: 0 6px 20px rgba(56, 189, 248, 0.4) !important;
        transform: translateY(-1px);
    }}

    [data-testid="stChatInput"] textarea {{
        background: #1e293b !important;
        color: #f8fafc !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 14px !important;
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        font-size: 0.96rem !important;
        padding: 16px 20px !important;
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.4) !important;
    }}

    .sidebar-signature {{
        text-align: center;
        font-family: 'Inter', sans-serif;
        font-size: 0.68rem;
        color: #38bdf8;
        letter-spacing: 1.2px;
        padding: 14px 4px;
        margin-top: 24px;
        margin-bottom: 24px;
        border-top: 1px solid rgba(255, 255, 255, 0.08);
        border-bottom: 1px solid rgba(255, 255, 255, 0.08);
        text-transform: uppercase;
        background: rgba(56, 189, 248, 0.04);
    }}

    .ai-thinking-box {{
        display: flex;
        align-items: center;
        gap: 10px;
        padding: 12px 16px;
        background: #1e293b;
        border: 1px solid rgba(56, 189, 248, 0.3);
        border-radius: 12px;
        width: fit-content;
        max-width: 100%;
        margin: 8px 0;
    }}

    .ai-thinking-dots {{
        display: flex;
        gap: 6px;
        align-items: center;
    }}

    .ai-dot {{
        width: 7px;
        height: 7px;
        border-radius: 50%;
        background-color: #38bdf8;
        animation: aiDotBounce 1.4s infinite ease-in-out both;
    }}

    .ai-dot:nth-child(1) {{ animation-delay: -0.32s; }}
    .ai-dot:nth-child(2) {{ animation-delay: -0.16s; background-color: #818cf8; }}
    .ai-dot:nth-child(3) {{ animation-delay: 0s; background-color: #34d399; }}

    @keyframes aiDotBounce {{
        0%, 80%, 100% {{ transform: scale(0); opacity: 0.4; }}
        40% {{ transform: scale(1.3); opacity: 1; }}
    }}

    .ai-thinking-text {{
        font-family: 'Inter', sans-serif;
        font-size: 0.74rem;
        font-weight: 600;
        letter-spacing: 0.4px;
        color: #38bdf8;
        text-transform: uppercase;
    }}

    .ai-replying-badge {{
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 5px 12px;
        margin-bottom: 10px;
        background: rgba(56, 189, 248, 0.1);
        border: 1px solid rgba(56, 189, 248, 0.25);
        border-radius: 8px;
        font-family: 'Inter', sans-serif;
        font-size: 0.68rem;
        color: #38bdf8;
        font-weight: 600;
        letter-spacing: 0.4px;
        text-transform: uppercase;
    }}
</style>
"""

st.markdown(theme_css, unsafe_allow_html=True)

# 4. Sidebar Navigation & Controls
with st.sidebar:
    st.markdown("### ⚡ Executive Core")
    
    if not is_logged_in:
        st.write("<span style='font-size: 0.8rem; color: #94a3b8;'>Sign in to access workspace.</span>", unsafe_allow_html=True)
        st.button("🔑 Sign in with Google", on_click=st.login, use_container_width=True, type="primary")
    else:
        st.success(f"**{user_display_name}**")
        st.write(f"<span style='font-size: 0.74rem; color: #38bdf8;'>{user_email}</span>", unsafe_allow_html=True)
        st.button("Sign Out", on_click=st.logout, use_container_width=True)
            
        st.markdown("---")
        
        show_settings = st.checkbox("⚙️ Preferences", value=st.session_state["show_settings_modal"])
        if show_settings != st.session_state["show_settings_modal"]:
            st.session_state["show_settings_modal"] = show_settings
            st.rerun()

        show_brain = st.checkbox("🧠 Memory Bank", value=st.session_state["show_brain_modal"])
        if show_brain != st.session_state["show_brain_modal"]:
            st.session_state["show_brain_modal"] = show_brain
            st.rerun()

        st.markdown("---")
        
        if st.button("➕ New Stream", use_container_width=True, type="primary"):
            new_sid = str(uuid.uuid4())
            st.session_state[storage_key][new_sid] = {
                "title": "Executive Stream",
                "messages": []
            }
            st.session_state[f"{storage_key}_current_sid"] = new_sid
            st.rerun()
            
        st.markdown("### 💬 Active Streams")
        
        for sid, sdata in list(st.session_state[storage_key].items()):
            col1, col2 = st.columns([0.75, 0.25])
            with col1:
                btn_type = "primary" if sid == current_sid else "secondary"
                display_title = sdata["title"][:14] + ("..." if len(sdata["title"]) > 14 else "")
                if st.button(display_title, key=f"sel_{sid}", use_container_width=True, type=btn_type):
                    st.session_state[f"{storage_key}_current_sid"] = sid
                    st.rerun()
            with col2:
                if st.button("🗑️", key=f"del_{sid}", help="Delete stream", use_container_width=True):
                    del st.session_state[storage_key][sid]
                    if not st.session_state[storage_key]:
                        fresh_sid = str(uuid.uuid4())
                        st.session_state[storage_key][fresh_sid] = {"title": "Executive Stream", "messages": []}
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

# 5. Settings Modal Panel
if is_logged_in and st.session_state.get("show_settings_modal", False):
    with st.container():
        st.markdown("""
            <div style="border-radius: 12px; padding: 12px; margin-bottom: 12px;">
                <h3 style="font-family: 'Inter', sans-serif; margin-top: 0; font-size: 1rem; color: #38bdf8;">⚙️ Configuration</h3>
            </div>
        """, unsafe_allow_html=True)
        
        models_list = ["gemini-3.5-flash-lite", "gemini-3.1-flash-lite", "gemini-2.5-flash", "gemini-2.5-pro"]
        model_index = models_list.index(selected_model) if selected_model in models_list else 0
        selected_model_input = st.selectbox("Model Engine", models_list, index=model_index, key="modal_model_select")

        languages = ["English", "Malayalam", "Hindi", "Spanish", "French", "German", "Japanese", "Chinese", "Arabic"]
        lang_index = languages.index(lang_choice) if lang_choice in languages else 0
        lang_choice_input = st.selectbox("Response Language", languages, index=lang_index, key="modal_lang_select")
        
        col_s1, col_s2 = st.columns(2)
        with col_s1:
            if st.button("Apply", use_container_width=True, type="primary"):
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
            <div style="border-radius: 12px; padding: 12px; margin-bottom: 12px;">
                <h3 style="font-family: 'Inter', sans-serif; margin-top: 0; font-size: 1rem; color: #38bdf8;">🧠 Memory Bank</h3>
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

        if st.button("Close", use_container_width=True):
            st.session_state["show_brain_modal"] = False
            st.rerun()
        st.markdown("---")

# Refresh preferences
selected_model = st.session_state[prefs_storage_key].get("selected_model", "gemini-3.5-flash-lite")
lang_choice = st.session_state[prefs_storage_key].get("lang_choice", "English")

# 7. Main Canvas Header & Executive Sign-In Layout
st.markdown(f"""
    <div class="exec-title-container">
        <div class="exec-title">Metaverse_AI</div>
        <div class="exec-subtitle">
            <span>Engine: {selected_model}</span>
            <span>•</span>
            <span>Layout: Executive Split</span>
            <span>•</span>
            <span>Lang: {lang_choice}</span>
        </div>
    </div>
""", unsafe_allow_html=True)

if not is_logged_in:
    # Exclusive Split Layout for Sign In Page
    col_left, col_right = st.columns([1.1, 1.1], gap="large")
    
    with col_left:
        st.markdown("""
            <div style="padding-top: 20px;">
                <h1 style="font-family: 'Inter', sans-serif; font-size: 2.2rem; font-weight: 800; color: #ffffff; line-height: 1.2; margin-bottom: 16px;">
                    Intelligence, <br><span style="color: #38bdf8;">Redefined.</span>
                </h1>
                <p style="color: #94a3b8; font-size: 1rem; line-height: 1.6; margin-bottom: 24px;">
                    Access high-speed generative AI streams, dynamic model switching, and localized memory tools built inside an elite professional workspace.
                </p>
                <div style="display: flex; gap: 12px; align-items: center; color: #64748b; font-size: 0.85rem; font-weight: 600;">
                    <span>✓ Secure Authentication</span>
                    <span>•</span>
                    <span>✓ Multi-Engine Access</span>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
    with col_right:
        st.markdown("""
            <div class="exec-auth-container">
                <div class="exec-auth-badge">🔒</div>
                <div class="exec-auth-title">Welcome Back</div>
                <div class="exec-auth-desc">
                    Sign in with your Google corporate or personal account to enter your secure session dashboard.
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        col_btn1, col_btn2, col_btn3 = st.columns([0.1, 2.8, 0.1])
        with col_btn2:
            st.button("🔑 Continue with Google", on_click=st.login, use_container_width=True, type="primary")
            
    st.stop()

current_messages = current_session_data["messages"]

for message in current_messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 8. Realtime Chat & Response Engine
prompt = st.chat_input("Enter your command or query...")

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
                <span class="ai-thinking-text">Processing Request...</span>
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
                        f"""<div class="ai-replying-badge">⚡ Executive Stream Active</div>\n\n{full_response}▌""",
                        unsafe_allow_html=True
                    )
            
            message_placeholder.markdown(
                f"""<div class="ai-replying-badge">⚡ Executive Stream Complete</div>\n\n{full_response}""",
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
