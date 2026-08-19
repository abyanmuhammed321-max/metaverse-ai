import uuid
import streamlit as st
from google import genai
from google.genai import errors
from google.genai import types

# 1. Page Configuration & Adaptive Layout
st.set_page_config(
    page_title="Metaverse_AI",
    page_icon="🔮",
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
        "chat_alignment": "Neon Horizon"
    }

# Initialize Memory Bank
if memory_storage_key not in st.session_state:
    st.session_state[memory_storage_key] = [
        "Creator and Master Developer: Abyan Muhammed",
        "Creator Display Rule: Only mention 'Made by Abyan Muhammed' when the user explicitly greets ('hello', 'hi', 'hey') or asks who built/made the AI.",
        "User signed in as Google Identity: " + user_display_name,
        "Core Objective: Cybernetic Neon Horizon Layout with absolute visual prestige."
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

current_alignment = st.session_state[prefs_storage_key].get("chat_alignment", "Neon Horizon")

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
        background: rgba(13, 17, 28, 0.75) !important;
        backdrop-filter: blur(25px) !important;
        border: 1px solid rgba(168, 85, 247, 0.2) !important;
        border-top: 3px solid #a855f7 !important;
        border-radius: 28px !important;
        padding: 48px !important;
        margin: 16px auto !important;
        width: 100% !important;
        box-shadow: 0 25px 60px rgba(0, 0, 0, 0.7), 0 0 30px rgba(168, 85, 247, 0.1) !important;
    }
"""

# 3. CYBERNETIC NEON HORIZON STYLING & SIGN-IN LAYOUT
theme_css = f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&family=Space+Grotesk:wght@400;500;600;700&display=swap');

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
        background: radial-gradient(circle at 15% 15%, #1e1b4b 0%, #09090b 50%, #030305 100%) !important;
        background-attachment: fixed !important;
        color: #f4f4f5 !important;
        font-family: 'Outfit', sans-serif;
        width: 100% !important;
        overflow-x: hidden !important;
    }}

    {desktop_container_css}

    /* Strict Mobile Screen Optimization (< 768px) */
    @media (max-width: 768px) {{
        .block-container {{
            max-width: 100% !important;
            padding-left: 10px !important;
            padding-right: 10px !important;
            padding-top: 1rem !important;
            padding-bottom: 8rem !important;
            margin: 0 !important;
        }}
        [data-testid="stMain"] > div {{
            background: rgba(13, 17, 28, 0.85) !important;
            border: 1px solid rgba(168, 85, 247, 0.25) !important;
            border-top: 3px solid #a855f7 !important;
            border-radius: 20px !important;
            padding: 16px 12px !important;
            margin: 15px auto 0 auto !important;
            box-shadow: 0 15px 35px rgba(0, 0, 0, 0.7) !important;
            width: 100% !important;
        }}
        
        .neon-title-container {{
            text-align: center !important;
            width: 100% !important;
            display: block !important;
            padding-top: 4px !important;
            margin-bottom: 14px !important;
        }}
        .neon-title {{
            font-size: 1.6rem !important;
            letter-spacing: -0.5px !important;
            line-height: 1.2 !important;
            text-align: center !important;
            display: block !important;
            width: 100% !important;
            margin: 0 auto !important;
        }}
        .neon-subtitle {{
            font-size: 0.6rem !important;
            margin-bottom: 12px !important;
            letter-spacing: 0.8px !important;
            text-align: center !important;
            display: flex !important;
            flex-wrap: wrap !important;
            justify-content: center !important;
            gap: 2px 6px !important;
            width: 100% !important;
        }}
        .stChatMessage {{
            padding: 14px !important;
            border-radius: 16px !important;
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
            background: rgba(9, 9, 11, 0.9) !important;
            backdrop-filter: blur(20px) !important;
            z-index: 99999 !important;
            border-top: 1px solid rgba(168, 85, 247, 0.2) !important;
        }}
    }}

    [data-testid="stSidebar"] {{
        background-color: #060608 !important;
        border-right: 1px solid rgba(168, 85, 247, 0.15) !important;
    }}
    
    [data-testid="stSidebar"] * {{
        color: #f4f4f5 !important;
    }}

    .neon-title {{
        font-family: 'Space Grotesk', sans-serif;
        font-size: 2.8rem;
        font-weight: 800;
        background: linear-gradient(135deg, #ffffff 30%, #c084fc 70%, #ec4899 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 4px;
        letter-spacing: -1.5px;
    }}
    
    .neon-subtitle {{
        color: #a1a1aa;
        font-size: 0.82rem;
        margin-bottom: 24px;
        font-weight: 600;
        letter-spacing: 1.2px;
        text-transform: uppercase;
        font-family: 'Space Grotesk', sans-serif;
    }}

    /* Neon Horizon Centered Login Box */
    .neon-auth-container {{
        background: rgba(18, 20, 32, 0.85);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(168, 85, 247, 0.3);
        border-radius: 24px;
        padding: 48px 40px;
        margin: 30px auto;
        max-width: 540px;
        box-shadow: 0 20px 50px rgba(0, 0, 0, 0.6), 0 0 40px rgba(168, 85, 247, 0.15);
        text-align: center;
        position: relative;
        overflow: hidden;
    }}
    
    .neon-auth-container::before {{
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: linear-gradient(90deg, #ec4899, #8b5cf6, #3b82f6);
    }}

    .neon-auth-badge {{
        font-size: 2.5rem;
        margin-bottom: 16px;
        display: inline-block;
        padding: 16px;
        background: rgba(168, 85, 247, 0.1);
        border-radius: 20px;
        border: 1px solid rgba(168, 85, 247, 0.3);
    }}

    .neon-auth-title {{
        font-family: 'Space Grotesk', sans-serif;
        font-size: 1.6rem;
        font-weight: 700;
        color: #ffffff;
        margin-bottom: 10px;
        letter-spacing: -0.5px;
    }}

    .neon-auth-desc {{
        font-size: 0.95rem;
        line-height: 1.6;
        color: #a1a1aa;
        margin-bottom: 32px;
    }}

    .stChatMessage {{
        background: rgba(18, 22, 36, 0.8) !important;
        backdrop-filter: blur(15px) !important;
        border: 1px solid rgba(168, 85, 247, 0.2) !important;
        border-radius: 20px !important;
        padding: 22px !important;
        margin-bottom: 20px !important;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.4) !important;
        word-break: break-word !important;
        overflow-wrap: break-word !important;
        max-width: 100% !important;
    }}

    .stChatMessage p, .stChatMessage span, .stChatMessage div, .stMarkdown {{
        color: #f4f4f5 !important;
        font-size: 0.98rem !important;
        line-height: 1.7 !important;
        word-break: break-word !important;
        overflow-wrap: break-word !important;
    }}

    .stButton button {{
        border-radius: 14px !important;
        font-family: 'Space Grotesk', sans-serif !important;
        font-weight: 700 !important;
        font-size: 0.92rem !important;
        letter-spacing: 0.5px !important;
        border: 1px solid rgba(168, 85, 247, 0.5) !important;
        background: linear-gradient(135deg, #a855f7 0%, #ec4899 100%) !important;
        color: #ffffff !important;
        width: 100% !important;
        padding: 14px 24px !important;
        box-shadow: 0 6px 25px rgba(168, 85, 247, 0.35) !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    }}
    
    .stButton button:hover {{
        background: linear-gradient(135deg, #c084fc 0%, #f43f5e 100%) !important;
        border-color: #f472b6 !important;
        box-shadow: 0 10px 30px rgba(236, 72, 153, 0.5) !important;
        transform: translateY(-2px);
    }}

    [data-testid="stChatInput"] textarea {{
        background: rgba(18, 22, 36, 0.9) !important;
        color: #f4f4f5 !important;
        border: 1px solid rgba(168, 85, 247, 0.3) !important;
        border-radius: 16px !important;
        font-family: 'Outfit', sans-serif !important;
        font-size: 0.98rem !important;
        padding: 16px 20px !important;
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.5) !important;
    }}

    .sidebar-signature {{
        text-align: center;
        font-family: 'Space Grotesk', sans-serif;
        font-size: 0.7rem;
        color: #c084fc;
        letter-spacing: 1.5px;
        padding: 16px 4px;
        margin-top: 24px;
        margin-bottom: 24px;
        border-top: 1px solid rgba(168, 85, 247, 0.2);
        border-bottom: 1px solid rgba(168, 85, 247, 0.2);
        text-transform: uppercase;
        background: rgba(168, 85, 247, 0.05);
    }}

    .ai-thinking-box {{
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 14px 18px;
        background: rgba(18, 22, 36, 0.9);
        border: 1px solid rgba(168, 85, 247, 0.4);
        border-radius: 14px;
        width: fit-content;
        max-width: 100%;
        margin: 10px 0;
        box-shadow: 0 8px 25px rgba(168, 85, 247, 0.15);
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
        background-color: #a855f7;
        animation: aiDotBounce 1.4s infinite ease-in-out both;
    }}

    .ai-dot:nth-child(1) {{ animation-delay: -0.32s; }}
    .ai-dot:nth-child(2) {{ animation-delay: -0.16s; background-color: #ec4899; }}
    .ai-dot:nth-child(3) {{ animation-delay: 0s; background-color: #3b82f6; }}

    @keyframes aiDotBounce {{
        0%, 80%, 100% {{ transform: scale(0); opacity: 0.4; }}
        40% {{ transform: scale(1.3); opacity: 1; }}
    }}

    .ai-thinking-text {{
        font-family: 'Space Grotesk', sans-serif;
        font-size: 0.78rem;
        font-weight: 700;
        letter-spacing: 0.6px;
        color: #c084fc;
        text-transform: uppercase;
    }}

    .ai-replying-badge {{
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 6px 14px;
        margin-bottom: 12px;
        background: rgba(168, 85, 247, 0.12);
        border: 1px solid rgba(168, 85, 247, 0.3);
        border-radius: 10px;
        font-family: 'Space Grotesk', sans-serif;
        font-size: 0.72rem;
        color: #c084fc;
        font-weight: 700;
        letter-spacing: 0.6px;
        text-transform: uppercase;
    }}
</style>
"""

st.markdown(theme_css, unsafe_allow_html=True)

# 4. Sidebar Navigation & Controls
with st.sidebar:
    st.markdown("### 🌌 Quantum Core")
    
    if not is_logged_in:
        st.write("<span style='font-size: 0.82rem; color: #a1a1aa;'>Sign in to activate your quantum node.</span>", unsafe_allow_html=True)
        st.button("🔮 Sign in with Google", on_click=st.login, use_container_width=True, type="primary")
    else:
        st.success(f"**{user_display_name}**")
        st.write(f"<span style='font-size: 0.76rem; color: #c084fc;'>{user_email}</span>", unsafe_allow_html=True)
        st.button("Sign Out", on_click=st.logout, use_container_width=True)
            
        st.markdown("---")
        
        show_settings = st.checkbox("⚙️ Settings", value=st.session_state["show_settings_modal"])
        if show_settings != st.session_state["show_settings_modal"]:
            st.session_state["show_settings_modal"] = show_settings
            st.rerun()

        show_brain = st.checkbox("🧠 Memory Vault", value=st.session_state["show_brain_modal"])
        if show_brain != st.session_state["show_brain_modal"]:
            st.session_state["show_brain_modal"] = show_brain
            st.rerun()

        st.markdown("---")
        
        if st.button("➕ New Quantum Stream", use_container_width=True, type="primary"):
            new_sid = str(uuid.uuid4())
            st.session_state[storage_key][new_sid] = {
                "title": "Quantum Stream",
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

selected_model = st.session_state[prefs_storage_key].get("selected_model", "gemini-3.5-flash-lite")
lang_choice = st.session_state[prefs_storage_key].get("lang_choice", "English")

# 5. Settings Modal Panel
if is_logged_in and st.session_state.get("show_settings_modal", False):
    with st.container():
        st.markdown("""
            <div style="border-radius: 12px; padding: 12px; margin-bottom: 12px;">
                <h3 style="font-family: 'Space Grotesk', sans-serif; margin-top: 0; font-size: 1.1rem; color: #c084fc;">⚙️ Quantum Configuration</h3>
            </div>
        """, unsafe_allow_html=True)
        
        models_list = ["gemini-3.5-flash-lite", "gemini-3.1-flash-lite", "gemini-2.5-flash", "gemini-2.5-pro"]
        model_index = models_list.index(selected_model) if selected_model in models_list else 0
        selected_model_input = st.selectbox("AI Model Core", models_list, index=model_index, key="modal_model_select")

        languages = ["English", "Malayalam", "Hindi", "Spanish", "French", "German", "Japanese", "Chinese", "Arabic"]
        lang_index = languages.index(lang_choice) if lang_choice in languages else 0
        lang_choice_input = st.selectbox("Response Language", languages, index=lang_index, key="modal_lang_select")
        
        col_s1, col_s2 = st.columns(2)
        with col_s1:
            if st.button("Apply Changes", use_container_width=True, type="primary"):
                st.session_state[prefs_storage_key]["selected_model"] = selected_model_input
                st.session_state[prefs_storage_key]["lang_choice"] = lang_choice_input
                st.session_state["show_settings_modal"] = False
                st.rerun()
        with col_s2:
            if st.button("Close Modal", use_container_width=True):
                st.session_state["show_settings_modal"] = False
                st.rerun()
        st.markdown("---")

# 6. Memory Bank Modal Panel
if is_logged_in and st.session_state.get("show_brain_modal", False):
    with st.container():
        st.markdown("""
            <div style="border-radius: 12px; padding: 12px; margin-bottom: 12px;">
                <h3 style="font-family: 'Space Grotesk', sans-serif; margin-top: 0; font-size: 1.1rem; color: #c084fc;">🧠 Quantum Memory Vault</h3>
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

        if st.button("Close Vault", use_container_width=True):
            st.session_state["show_brain_modal"] = False
            st.rerun()
        st.markdown("---")

# Refresh preferences
selected_model = st.session_state[prefs_storage_key].get("selected_model", "gemini-3.5-flash-lite")
lang_choice = st.session_state[prefs_storage_key].get("lang_choice", "English")

# 7. Main Canvas Header & Neon Horizon Centered Sign-In Layout
st.markdown(f"""
    <div class="neon-title-container">
        <div class="neon-title">Metaverse_AI</div>
        <div class="neon-subtitle">
            <span>Core: {selected_model}</span>
            <span>•</span>
            <span>Horizon: Neon Cyber</span>
            <span>•</span>
            <span>Lang: {lang_choice}</span>
        </div>
    </div>
""", unsafe_allow_html=True)

if not is_logged_in:
    # Spectacular Centered Glassmorphic Sign-In Horizon
    st.markdown("""
        <div class="neon-auth-container">
            <div class="neon-auth-badge">🌌</div>
            <div class="neon-auth-title">Welcome to the Quantum Frontier</div>
            <div class="neon-auth-desc">
                Authenticate with your Google identity to unlock high-velocity generative AI streams, neural memory modules, and multi-model intelligence.
            </div>
    """, unsafe_allow_html=True)
    
    col_btn1, col_btn2, col_btn3 = st.columns([1, 2.5, 1])
    with col_btn2:
        st.button("🔮 Sign in with Google", on_click=st.login, use_container_width=True, type="primary")
        
    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

current_messages = current_session_data["messages"]

for message in current_messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 8. Realtime Chat & Response Engine
prompt = st.chat_input("Ask or command the quantum engine...")

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
                <span class="ai-thinking-text">Synthesizing Response...</span>
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
                f"MEMORY VAULT:\n{brain_memories_str}"
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
                        f"""<div class="ai-replying-badge">🔮 Quantum Stream Active</div>\n\n{full_response}▌""",
                        unsafe_allow_html=True
                    )
            
            message_placeholder.markdown(
                f"""<div class="ai-replying-badge">🔮 Quantum Stream Complete</div>\n\n{full_response}""",
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
