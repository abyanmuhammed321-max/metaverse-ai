import uuid
import streamlit as st
from google import genai
from google.genai import errors
from google.genai import types

# 1. Page Configuration with Adaptive Layout
st.set_page_config(
    page_title="Metaverse_AI",
    page_icon="⚡",
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
memory_storage_key = f"metaverse_ai_memory_{user_email.replace('@', '_at_').replace('.', '_')}"

# Initialize preferences with the brand new Cyberpunk Neon Nebula theme
if prefs_storage_key not in st.session_state:
    st.session_state[prefs_storage_key] = {
        "selected_model": "gemini-3.1-flash-lite",
        "lang_choice": "English",
        "chat_alignment": "Cyber Neon Grid"
    }

# Initialize Memory Bank
if memory_storage_key not in st.session_state:
    st.session_state[memory_storage_key] = [
        "Creator and Master Developer: Abyan Muhammed",
        "Creator Display Rule: Only mention 'Made by Abyan Muhammed' when the user explicitly greets ('hello', 'hi', 'hey') or asks who built/made the AI.",
        "User signed in as Google Identity: " + user_display_name,
        "Core Objective: Cyberpunk Neon Nebula styling with glowing cyan/magenta gradients, holographic panels, and futuristic alignment layouts."
    ]

if storage_key not in st.session_state:
    first_sid = str(uuid.uuid4())
    st.session_state[storage_key] = {
        first_sid: {
            "title": "Neural stream",
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

# Retrieve current alignment preference
current_alignment = st.session_state[prefs_storage_key].get("chat_alignment", "Cyber Neon Grid")

# Futuristic Alignment Engine Selection
if current_alignment == "Cyber Neon Grid":
    desktop_container_css = """
        .block-container {
            max-width: 1350px !important;
            padding-left: 3rem !important;
            padding-right: 3rem !important;
            padding-top: 2rem !important;
            padding-bottom: 7.5rem !important;
            margin: 0 auto !important;
        }
        [data-testid="stMain"] > div {
            background: linear-gradient(135deg, rgba(8, 12, 28, 0.9) 0%, rgba(20, 8, 32, 0.9) 100%) !important;
            backdrop-filter: blur(40px) !important;
            border: 1px solid rgba(0, 243, 255, 0.3) !important;
            border-top: 3px solid #00f3ff !important;
            border-radius: 24px !important;
            padding: 44px !important;
            margin: 16px auto !important;
            width: 100% !important;
            box-shadow: 0 0 50px rgba(0, 243, 255, 0.12), inset 0 1px 0 rgba(255, 255, 255, 0.1) !important;
        }
    """
elif current_alignment == "Holographic Matrix":
    desktop_container_css = """
        .block-container {
            max-width: 1400px !important;
            padding-left: 3rem !important;
            padding-right: 3rem !important;
            padding-top: 2rem !important;
            padding-bottom: 7.5rem !important;
            margin: 0 auto !important;
        }
        [data-testid="stMain"] > div {
            background: radial-gradient(circle at 50% 0%, rgba(5, 30, 25, 0.85) 0%, rgba(5, 10, 20, 0.95) 100%) !important;
            backdrop-filter: blur(35px) !important;
            border: 1px solid rgba(16, 185, 129, 0.35) !important;
            border-top: 3px solid #10b981 !important;
            border-radius: 24px !important;
            padding: 44px !important;
            margin: 16px auto !important;
            width: 100% !important;
            box-shadow: 0 0 50px rgba(16, 185, 129, 0.15) !important;
        }
    """
else: # Deep Space Nebula
    desktop_container_css = """
        .block-container {
            max-width: 1300px !important;
            padding-left: 3rem !important;
            padding-right: 3rem !important;
            padding-top: 2rem !important;
            padding-bottom: 7.5rem !important;
            margin: 0 auto !important;
        }
        [data-testid="stMain"] > div {
            background: linear-gradient(150deg, rgba(30, 10, 40, 0.9) 0%, rgba(10, 5, 20, 0.95) 100%) !important;
            backdrop-filter: blur(30px) !important;
            border: 1px solid rgba(236, 72, 153, 0.35) !important;
            border-top: 3px solid #ec4899 !important;
            border-radius: 28px !important;
            padding: 44px !important;
            margin: 16px auto !important;
            width: 100% !important;
            box-shadow: 0 0 60px rgba(236, 72, 153, 0.15) !important;
        }
    """

# 3. CYBERPUNK NEON NEBULA STYLING ENGINE
theme_css = f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@500;700;900&family=Inter:wght@300;400;500;600&display=swap');

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
        background: radial-gradient(circle at 50% 0%, #0c102b 0%, #050714 60%, #010208 100%) !important;
        background-attachment: fixed !important;
        color: #e2e8f0 !important;
        font-family: 'Inter', sans-serif;
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
            font-size: 1.5rem !important;
        }}
        .gemini-subtitle {{
            font-size: 0.7rem !important;
            margin-bottom: 16px !important;
        }}
        .stChatMessage {{
            padding: 14px !important;
            border-radius: 14px !important;
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
        background-color: #03050c !important;
        border-right: 1px solid rgba(0, 243, 255, 0.15) !important;
    }}
    
    [data-testid="stSidebar"] * {{
        color: #e2e8f0 !important;
    }}

    .gemini-title {{
        font-family: 'Orbitron', sans-serif;
        font-size: 2.4rem;
        font-weight: 900;
        background: linear-gradient(135deg, #ffffff 0%, #00f3ff 50%, #ec4899 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 4px;
        letter-spacing: 1.5px;
        text-shadow: 0 0 30px rgba(0, 243, 255, 0.3);
    }}
    
    .gemini-subtitle {{
        color: #94a3b8;
        font-size: 0.78rem;
        margin-bottom: 28px;
        font-weight: 600;
        letter-spacing: 1.5px;
        text-transform: uppercase;
        font-family: 'Orbitron', sans-serif;
    }}

    .stChatMessage {{
        background: rgba(13, 18, 38, 0.85) !important;
        backdrop-filter: blur(16px) !important;
        border: 1px solid rgba(0, 243, 255, 0.2) !important;
        border-radius: 18px !important;
        padding: 20px !important;
        margin-bottom: 16px !important;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5), inset 0 1px 0 rgba(255, 255, 255, 0.05) !important;
        word-break: break-word !important;
        overflow-wrap: break-word !important;
        max-width: 100% !important;
    }}

    .stChatMessage p, .stChatMessage span, .stChatMessage div, .stMarkdown {{
        color: #e2e8f0 !important;
        font-size: 0.95rem !important;
        line-height: 1.65 !important;
        word-break: break-word !important;
        overflow-wrap: break-word !important;
    }}

    .stButton button {{
        border-radius: 12px !important;
        font-family: 'Orbitron', sans-serif !important;
        font-weight: 700 !important;
        font-size: 0.75rem !important;
        letter-spacing: 1px !important;
        border: 1px solid rgba(0, 243, 255, 0.4) !important;
        background: linear-gradient(135deg, rgba(15, 23, 42, 0.9), rgba(0, 50, 80, 0.8)) !important;
        color: #00f3ff !important;
        width: 100% !important;
        padding: 10px 16px !important;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.4) !important;
        transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1) !important;
        text-transform: uppercase !important;
    }}
    
    .stButton button:hover {{
        background: linear-gradient(135deg, rgba(0, 243, 255, 0.2), rgba(236, 72, 153, 0.2)) !important;
        border-color: #00f3ff !important;
        box-shadow: 0 0 20px rgba(0, 243, 255, 0.5) !important;
        color: #ffffff !important;
        transform: translateY(-1px);
    }}

    [data-testid="stChatInput"] {{
        padding: 0 4px 10px 4px !important;
    }}

    [data-testid="stChatInput"] textarea {{
        background: rgba(6, 9, 20, 0.95) !important;
        color: #e2e8f0 !important;
        border: 1px solid rgba(0, 243, 255, 0.4) !important;
        border-radius: 18px !important;
        font-family: 'Inter', sans-serif !important;
        font-size: 0.95rem !important;
        padding: 16px 20px !important;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.7), inset 0 0 15px rgba(0, 243, 255, 0.05) !important;
    }}

    .sidebar-signature {{
        text-align: center;
        font-family: 'Orbitron', sans-serif;
        font-size: 0.65rem;
        color: #00f3ff;
        letter-spacing: 2px;
        padding: 14px 4px;
        margin-top: 24px;
        margin-bottom: 24px;
        border-top: 1px solid rgba(0, 243, 255, 0.25);
        border-bottom: 1px solid rgba(0, 243, 255, 0.25);
        text-transform: uppercase;
        background: rgba(0, 243, 255, 0.04);
        text-shadow: 0 0 10px rgba(0, 243, 255, 0.4);
    }}

    .ai-thinking-box {{
        display: flex;
        align-items: center;
        gap: 10px;
        padding: 14px 20px;
        background: rgba(0, 243, 255, 0.08);
        border: 1px solid rgba(0, 243, 255, 0.4);
        border-radius: 14px;
        width: fit-content;
        margin: 8px 0;
        box-shadow: 0 0 20px rgba(0, 243, 255, 0.1);
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
        background-color: #00f3ff;
        box-shadow: 0 0 8px #00f3ff;
        animation: aiDotBounce 1.4s infinite ease-in-out both;
    }}

    .ai-dot:nth-child(1) {{ animation-delay: -0.32s; }}
    .ai-dot:nth-child(2) {{ animation-delay: -0.16s; background-color: #ec4899; box-shadow: 0 0 8px #ec4899; }}
    .ai-dot:nth-child(3) {{ animation-delay: 0s; background-color: #10b981; box-shadow: 0 0 8px #10b981; }}

    @keyframes aiDotBounce {{
        0%, 80%, 100% {{ transform: scale(0); opacity: 0.4; }}
        40% {{ transform: scale(1.3); opacity: 1; }}
    }}

    .ai-thinking-text {{
        font-family: 'Orbitron', sans-serif;
        font-size: 0.75rem;
        font-weight: 700;
        letter-spacing: 1px;
        color: #00f3ff;
        text-transform: uppercase;
    }}

    .ai-replying-badge {{
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 6px 14px;
        margin-bottom: 12px;
        background: rgba(0, 243, 255, 0.1);
        border: 1px solid rgba(0, 243, 255, 0.35);
        border-radius: 10px;
        font-family: 'Orbitron', sans-serif;
        font-size: 0.68rem;
        color: #00f3ff;
        font-weight: 700;
        letter-spacing: 1px;
        text-transform: uppercase;
        box-shadow: 0 0 15px rgba(0, 243, 255, 0.15);
    }}
</style>
"""

st.markdown(theme_css, unsafe_allow_html=True)

# 4. Sidebar Navigation & Feature Control
with st.sidebar:
    st.markdown("### ⚡ Cyber Neural Core")
    
    if not is_logged_in:
        st.write("<span style='font-size: 0.8rem;'>Sign in with Google to synchronize neural sync.</span>", unsafe_allow_html=True)
        st.button("🔑 Sign in with Google", on_click=st.login, use_container_width=True, type="primary")
    else:
        st.success(f"**{user_display_name}**")
        st.write(f"<span style='font-size: 0.72rem; color: #00f3ff;'>{user_email}</span>", unsafe_allow_html=True)
        st.button("Disconnect Link", on_click=st.logout, use_container_width=True)
            
        st.markdown("---")
        
        show_settings = st.checkbox("⚙️ Cyber Config", value=st.session_state["show_settings_modal"])
        if show_settings != st.session_state["show_settings_modal"]:
            st.session_state["show_settings_modal"] = show_settings
            st.rerun()

        show_brain = st.checkbox("🧠 Neural Bank", value=st.session_state["show_brain_modal"])
        if show_brain != st.session_state["show_brain_modal"]:
            st.session_state["show_brain_modal"] = show_brain
            st.rerun()

        st.markdown("---")
        
        if st.button("➕ New Neural Stream", use_container_width=True, type="primary"):
            new_sid = str(uuid.uuid4())
            st.session_state[storage_key][new_sid] = {
                "title": "Neural stream",
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
                if st.button("🗑️", key=f"del_{sid}", help="Terminate stream", use_container_width=True):
                    del st.session_state[storage_key][sid]
                    if not st.session_state[storage_key]:
                        fresh_sid = str(uuid.uuid4())
                        st.session_state[storage_key][fresh_sid] = {"title": "Neural stream", "messages": []}
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

# 5. Settings Modal Panel
if is_logged_in and st.session_state.get("show_settings_modal", False):
    with st.container():
        st.markdown("""
            <div style="border-radius: 16px; padding: 16px; margin-bottom: 14px;">
                <h3 style="font-family: 'Orbitron', sans-serif; margin-top: 0; font-size: 1rem; color: #00f3ff;">⚙️ Cyber Config & Layout Grids</h3>
            </div>
        """, unsafe_allow_html=True)
        
        models_list = ["gemini-3.1-flash-lite", "gemini-2.0-flash", "gemini-2.5-flash", "gemini-2.5-pro"]
        model_index = models_list.index(selected_model) if selected_model in models_list else 0
        selected_model_input = st.selectbox("Model Engine", models_list, index=model_index, key="modal_model_select")

        languages = ["English", "Malayalam", "Hindi", "Spanish", "French", "German", "Japanese", "Chinese", "Arabic"]
        lang_index = languages.index(lang_choice) if lang_choice in languages else 0
        lang_choice_input = st.selectbox("Response Language", languages, index=lang_index, key="modal_lang_select")

        alignments = ["Cyber Neon Grid", "Holographic Matrix", "Deep Space Nebula"]
        current_align_pref = st.session_state[prefs_storage_key].get("chat_alignment", "Cyber Neon Grid")
        align_index = alignments.index(current_align_pref) if current_align_pref in alignments else 0
        alignment_choice_input = st.selectbox("Holographic Layout Alignment", alignments, index=align_index, key="modal_align_select")
        
        col_s1, col_s2 = st.columns(2)
        with col_s1:
            if st.button("Apply Config", use_container_width=True, type="primary"):
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
                <h3 style="font-family: 'Orbitron', sans-serif; margin-top: 0; font-size: 1rem; color: #00f3ff;">🧠 Neural Memory Bank</h3>
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

        if st.button("Close Neural Bank", use_container_width=True):
            st.session_state["show_brain_modal"] = False
            st.rerun()
        st.markdown("---")

# Refresh preferences
selected_model = st.session_state[prefs_storage_key].get("selected_model", "gemini-3.1-flash-lite")
lang_choice = st.session_state[prefs_storage_key].get("lang_choice", "English")
current_alignment = st.session_state[prefs_storage_key].get("chat_alignment", "Cyber Neon Grid")

# 7. Main Canvas Layout
st.markdown(f'<div class="gemini-title">Metaverse_AI</div>', unsafe_allow_html=True)
st.markdown(f'<div class="gemini-subtitle">Engine: {selected_model} • Style: {current_alignment} • Language: {lang_choice}</div>', unsafe_allow_html=True)

if not is_logged_in:
    st.markdown("""
        <div style="border-radius: 20px; padding: 32px; text-align: center; margin-top: 20px; background: rgba(13, 18, 38, 0.5); border: 1px solid rgba(0, 243, 255, 0.3);">
            <h2 style="font-family: 'Orbitron', sans-serif; font-size: 1.2rem; margin-bottom: 12px; color: #00f3ff;">Neural Link Required</h2>
            <p style="font-size: 0.9rem; line-height: 1.6; margin-bottom: 24px; color: #94a3b8;">
                Please authenticate using Google credentials from the sidebar to initialize your workspace connection.
            </p>
        </div>
    """, unsafe_allow_html=True)
    st.stop()

current_messages = current_session_data["messages"]

for message in current_messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 8. Realtime Message Handling & Animated Reply Engine
prompt = st.chat_input("Enter command or prompt...")

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
                <span class="ai-thinking-text">Processing Neural Stream...</span>
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
                        f"""<div class="ai-replying-badge">⚡ Neural Transmission Active</div>\n\n{full_response}▌""",
                        unsafe_allow_html=True
                    )
            
            message_placeholder.markdown(
                f"""<div class="ai-replying-badge">⚡ Neural Transmission Complete</div>\n\n{full_response}""",
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
