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

# Initialize preferences with Gemini 3.5 Flash Lite as default
if prefs_storage_key not in st.session_state:
    st.session_state[prefs_storage_key] = {
        "selected_model": "gemini-3.5-flash-lite",
        "lang_choice": "English",
        "chat_alignment": "Neon Obsidian Vault"
    }

# Initialize Memory Bank
if memory_storage_key not in st.session_state:
    st.session_state[memory_storage_key] = [
        "Creator and Master Developer: Abyan Muhammed",
        "Creator Display Rule: Only mention 'Made by Abyan Muhammed' when the user explicitly greets ('hello', 'hi', 'hey') or asks who built/made the AI.",
        "User signed in as Google Identity: " + user_display_name,
        "Core Objective: Next-gen Neon Cyber-Luxe styling with absolute mobile text clarity."
    ]

if storage_key not in st.session_state:
    first_sid = str(uuid.uuid4())
    st.session_state[storage_key] = {
        first_sid: {
            "title": "Luxe Stream",
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

current_alignment = st.session_state[prefs_storage_key].get("chat_alignment", "Neon Obsidian Vault")

# Luxury Alignment Configurations (Desktop CSS)
if current_alignment == "Neon Obsidian Vault":
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
            background: linear-gradient(145deg, rgba(12, 14, 20, 0.95) 0%, rgba(22, 18, 30, 0.95) 100%) !important;
            backdrop-filter: blur(45px) !important;
            border: 1px solid rgba(212, 175, 55, 0.3) !important;
            border-top: 3px solid #00f3ff !important;
            border-radius: 30px !important;
            padding: 48px !important;
            margin: 16px auto !important;
            width: 100% !important;
            box-shadow: 0 0 70px rgba(0, 243, 255, 0.1), 0 30px 90px rgba(0, 0, 0, 0.9) !important;
        }
    """
elif current_alignment == "Cyber Imperial Suite":
    desktop_container_css = """
        .block-container {
            max-width: 1360px !important;
            padding-left: 3rem !important;
            padding-right: 3rem !important;
            padding-top: 2rem !important;
            padding-bottom: 7.5rem !important;
            margin: 0 auto !important;
        }
        [data-testid="stMain"] > div {
            background: radial-gradient(circle at 50% 0%, rgba(25, 12, 35, 0.92) 0%, rgba(8, 10, 22, 0.96) 100%) !important;
            backdrop-filter: blur(40px) !important;
            border: 1px solid rgba(236, 72, 153, 0.35) !important;
            border-top: 3px solid #d4af37 !important;
            border-radius: 30px !important;
            padding: 48px !important;
            margin: 16px auto !important;
            width: 100% !important;
            box-shadow: 0 0 70px rgba(236, 72, 153, 0.15) !important;
        }
    """
else:
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
            background: linear-gradient(135deg, rgba(8, 20, 18, 0.95) 0%, rgba(10, 12, 22, 0.95) 100%) !important;
            backdrop-filter: blur(40px) !important;
            border: 1px solid rgba(16, 185, 129, 0.35) !important;
            border-top: 3px solid #10b981 !important;
            border-radius: 30px !important;
            padding: 48px !important;
            margin: 16px auto !important;
            width: 100% !important;
            box-shadow: 0 0 70px rgba(16, 185, 129, 0.12) !important;
        }
    """

# 3. ULTIMATE RESPONSIVE STYLING & MOBILE ALIGNMENT FIXES
theme_css = f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@600;700;900&family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');

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
        background: radial-gradient(circle at 50% 0%, #12141c 0%, #06080e 60%, #020306 100%) !important;
        background-attachment: fixed !important;
        color: #f1f5f9 !important;
        font-family: 'Plus Jakarta Sans', sans-serif;
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
            padding-top: 0.5rem !important;
            padding-bottom: 8rem !important;
            margin: 0 !important;
        }}
        [data-testid="stMain"] > div {{
            background: rgba(12, 14, 20, 0.98) !important;
            backdrop-filter: blur(20px) !important;
            border: 1px solid rgba(0, 243, 255, 0.25) !important;
            border-top: 3px solid #00f3ff !important;
            border-radius: 14px !important;
            padding: 12px 10px !important;
            margin: 2px auto !important;
            box-shadow: 0 5px 20px rgba(0, 0, 0, 0.7) !important;
            width: 100% !important;
        }}
        
        /* Perfectly aligned & fluid scaling for mobile headers */
        .gemini-title-container {{
            text-align: center !important;
            width: 100% !important;
            padding: 0 4px !important;
            margin-bottom: 6px !important;
        }}
        .gemini-title {{
            font-size: clamp(1.5rem, 6vw, 2.2rem) !important;
            letter-spacing: 0.8px !important;
            line-height: 1.2 !important;
            text-align: center !important;
            display: inline-block !important;
            width: 100% !important;
        }}
        .gemini-subtitle {{
            font-size: clamp(0.58rem, 2.5vw, 0.72rem) !important;
            margin-bottom: 16px !important;
            letter-spacing: 0.5px !important;
            text-align: center !important;
            padding: 0 4px !important;
            display: flex !important;
            flex-wrap: wrap !important;
            justify-content: center !important;
            gap: 4px 8px !important;
            width: 100% !important;
        }}
        .stChatMessage {{
            padding: 12px !important;
            border-radius: 12px !important;
            margin-bottom: 10px !important;
            width: 100% !important;
            word-break: break-word !important;
        }}
        .stChatMessage p, .stChatMessage span, .stChatMessage div, .stMarkdown {{
            font-size: 0.92rem !important;
            line-height: 1.55 !important;
        }}
        [data-testid="stChatInput"] {{
            position: fixed !important;
            bottom: 0px !important;
            left: 0px !important;
            right: 0px !important;
            width: 100% !important;
            padding: 6px 8px 12px 8px !important;
            background: rgba(6, 8, 14, 0.98) !important;
            backdrop-filter: blur(15px) !important;
            z-index: 99999 !important;
            border-top: 1px solid rgba(0, 243, 255, 0.3) !important;
        }}
        [data-testid="stChatInput"] textarea {{
            font-size: 16px !important;
            padding: 10px 14px !important;
            border-radius: 12px !important;
        }}
        .mobile-signin-card {{
            padding: 24px 14px !important;
            margin-top: 10px !important;
            width: 100% !important;
        }}
    }}

    [data-testid="stSidebar"] {{
        background-color: #040508 !important;
        border-right: 1px solid rgba(212, 175, 55, 0.2) !important;
    }}
    
    [data-testid="stSidebar"] * {{
        color: #f1f5f9 !important;
    }}

    .gemini-title {{
        font-family: 'Cinzel', serif;
        font-size: 2.6rem;
        font-weight: 900;
        background: linear-gradient(135deg, #ffffff 0%, #00f3ff 45%, #d4af37 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 4px;
        letter-spacing: 1.5px;
        filter: drop-shadow(0 0 25px rgba(0, 243, 255, 0.25));
    }}
    
    .gemini-subtitle {{
        color: #94a3b8;
        font-size: 0.82rem;
        margin-bottom: 28px;
        font-weight: 600;
        letter-spacing: 1.5px;
        text-transform: uppercase;
        font-family: 'Cinzel', serif;
    }}

    .stChatMessage {{
        background: rgba(18, 20, 28, 0.9) !important;
        backdrop-filter: blur(18px) !important;
        border: 1px solid rgba(0, 243, 255, 0.25) !important;
        border-radius: 20px !important;
        padding: 22px !important;
        margin-bottom: 18px !important;
        box-shadow: 0 15px 35px rgba(0, 0, 0, 0.6), inset 0 1px 0 rgba(255, 255, 255, 0.08) !important;
        word-break: break-word !important;
        overflow-wrap: break-word !important;
        max-width: 100% !important;
    }}

    .stChatMessage p, .stChatMessage span, .stChatMessage div, .stMarkdown {{
        color: #f1f5f9 !important;
        font-size: 0.96rem !important;
        line-height: 1.65 !important;
        word-break: break-word !important;
        overflow-wrap: break-word !important;
    }}

    .stButton button {{
        border-radius: 12px !important;
        font-family: 'Cinzel', serif !important;
        font-weight: 700 !important;
        font-size: 0.78rem !important;
        letter-spacing: 1px !important;
        border: 1px solid rgba(0, 243, 255, 0.4) !important;
        background: linear-gradient(135deg, rgba(20, 25, 40, 0.95), rgba(10, 40, 50, 0.9)) !important;
        color: #00f3ff !important;
        width: 100% !important;
        padding: 10px 16px !important;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.5) !important;
        transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1) !important;
        text-transform: uppercase !important;
    }}
    
    .stButton button:hover {{
        background: linear-gradient(135deg, rgba(0, 243, 255, 0.2), rgba(212, 175, 55, 0.2)) !important;
        border-color: #00f3ff !important;
        box-shadow: 0 0 25px rgba(0, 243, 255, 0.5) !important;
        color: #ffffff !important;
        transform: translateY(-1px);
    }}

    [data-testid="stChatInput"] textarea {{
        background: rgba(8, 10, 16, 0.95) !important;
        color: #f1f5f9 !important;
        border: 1px solid rgba(0, 243, 255, 0.4) !important;
        border-radius: 20px !important;
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        font-size: 0.96rem !important;
        padding: 16px 22px !important;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.8), inset 0 0 15px rgba(0, 243, 255, 0.05) !important;
    }}

    .sidebar-signature {{
        text-align: center;
        font-family: 'Cinzel', serif;
        font-size: 0.68rem;
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
        padding: 12px 16px;
        background: rgba(0, 243, 255, 0.08);
        border: 1px solid rgba(0, 243, 255, 0.4);
        border-radius: 14px;
        width: fit-content;
        max-width: 100%;
        margin: 8px 0;
        box-shadow: 0 0 20px rgba(0, 243, 255, 0.15);
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
        background-color: #00f3ff;
        box-shadow: 0 0 8px #00f3ff;
        animation: aiDotBounce 1.4s infinite ease-in-out both;
    }}

    .ai-dot:nth-child(1) {{ animation-delay: -0.32s; }}
    .ai-dot:nth-child(2) {{ animation-delay: -0.16s; background-color: #d4af37; box-shadow: 0 0 8px #d4af37; }}
    .ai-dot:nth-child(3) {{ animation-delay: 0s; background-color: #ec4899; box-shadow: 0 0 8px #ec4899; }}

    @keyframes aiDotBounce {{
        0%, 80%, 100% {{ transform: scale(0); opacity: 0.4; }}
        40% {{ transform: scale(1.3); opacity: 1; }}
    }}

    .ai-thinking-text {{
        font-family: 'Cinzel', serif;
        font-size: 0.72rem;
        font-weight: 700;
        letter-spacing: 0.8px;
        color: #00f3ff;
        text-transform: uppercase;
    }}

    .ai-replying-badge {{
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 5px 12px;
        margin-bottom: 10px;
        background: rgba(0, 243, 255, 0.12);
        border: 1px solid rgba(0, 243, 255, 0.35);
        border-radius: 10px;
        font-family: 'Cinzel', serif;
        font-size: 0.65rem;
        color: #00f3ff;
        font-weight: 700;
        letter-spacing: 0.8px;
        text-transform: uppercase;
        box-shadow: 0 0 15px rgba(0, 243, 255, 0.2);
    }}
</style>
"""

st.markdown(theme_css, unsafe_allow_html=True)

# 4. Sidebar Navigation & Controls
with st.sidebar:
    st.markdown("### 👑 Cyber-Luxe Core")
    
    if not is_logged_in:
        st.write("<span style='font-size: 0.8rem;'>Authenticate to unlock vault access.</span>", unsafe_allow_html=True)
        st.button("🔑 Sign in with Google", on_click=st.login, use_container_width=True, type="primary")
    else:
        st.success(f"**{user_display_name}**")
        st.write(f"<span style='font-size: 0.74rem; color: #00f3ff;'>{user_email}</span>", unsafe_allow_html=True)
        st.button("Lock Vault", on_click=st.logout, use_container_width=True)
            
        st.markdown("---")
        
        show_settings = st.checkbox("⚙️ Luxe Config", value=st.session_state["show_settings_modal"])
        if show_settings != st.session_state["show_settings_modal"]:
            st.session_state["show_settings_modal"] = show_settings
            st.rerun()

        show_brain = st.checkbox("🧠 Memory Vault", value=st.session_state["show_brain_modal"])
        if show_brain != st.session_state["show_brain_modal"]:
            st.session_state["show_brain_modal"] = show_brain
            st.rerun()

        st.markdown("---")
        
        if st.button("➕ New Luxe Stream", use_container_width=True, type="primary"):
            new_sid = str(uuid.uuid4())
            st.session_state[storage_key][new_sid] = {
                "title": "Luxe Stream",
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
                        st.session_state[storage_key][fresh_sid] = {"title": "Luxe Stream", "messages": []}
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
            <div style="border-radius: 14px; padding: 12px; margin-bottom: 12px;">
                <h3 style="font-family: 'Cinzel', serif; margin-top: 0; font-size: 1rem; color: #00f3ff;">⚙️ Cyber-Luxe Config & Layouts</h3>
            </div>
        """, unsafe_allow_html=True)
        
        models_list = ["gemini-3.5-flash-lite", "gemini-3.1-flash-lite", "gemini-2.5-flash", "gemini-2.5-pro"]
        model_index = models_list.index(selected_model) if selected_model in models_list else 0
        selected_model_input = st.selectbox("Model Engine", models_list, index=model_index, key="modal_model_select")

        languages = ["English", "Malayalam", "Hindi", "Spanish", "French", "German", "Japanese", "Chinese", "Arabic"]
        lang_index = languages.index(lang_choice) if lang_choice in languages else 0
        lang_choice_input = st.selectbox("Response Language", languages, index=lang_index, key="modal_lang_select")

        alignments = ["Neon Obsidian Vault", "Cyber Imperial Suite", "Emerald Cyber Matrix"]
        current_align_pref = st.session_state[prefs_storage_key].get("chat_alignment", "Neon Obsidian Vault")
        align_index = alignments.index(current_align_pref) if current_align_pref in alignments else 0
        alignment_choice_input = st.selectbox("Vault Alignment Theme", alignments, index=align_index, key="modal_align_select")
        
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
            <div style="border-radius: 14px; padding: 12px; margin-bottom: 12px;">
                <h3 style="font-family: 'Cinzel', serif; margin-top: 0; font-size: 1rem; color: #00f3ff;">🧠 Neural Memory Vault</h3>
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
current_alignment = st.session_state[prefs_storage_key].get("chat_alignment", "Neon Obsidian Vault")

# 7. Main Canvas Header & Responsive Sign-In Gateway
st.markdown(f"""
    <div class="gemini-title-container">
        <div class="gemini-title">Metaverse_AI</div>
        <div class="gemini-subtitle">
            <span>Engine: {selected_model}</span>
            <span>•</span>
            <span>Style: {current_alignment}</span>
            <span>•</span>
            <span>Lang: {lang_choice}</span>
        </div>
    </div>
""", unsafe_allow_html=True)

if not is_logged_in:
    st.markdown("""
        <div class="mobile-signin-card" style="
            background: linear-gradient(135deg, rgba(16, 20, 32, 0.98) 0%, rgba(25, 15, 35, 0.98) 100%);
            border: 1px solid rgba(0, 243, 255, 0.35);
            border-top: 3px solid #00f3ff;
            border-radius: 20px;
            padding: 24px 14px;
            text-align: center;
            margin: 10px auto;
            max-width: 100%;
            box-shadow: 0 0 40px rgba(0, 243, 255, 0.15), 0 15px 40px rgba(0, 0, 0, 0.8);
        ">
            <div style="font-size: 2rem; margin-bottom: 8px;">⚡</div>
            <h2 style="font-family: 'Cinzel', serif; font-size: 1.15rem; margin-bottom: 6px; color: #ffffff; letter-spacing: 0.5px;">
                Welcome to Metaverse_AI Elite
            </h2>
            <p style="font-size: 0.8rem; line-height: 1.45; margin-bottom: 18px; color: #94a3b8; max-width: 380px; margin-left: auto; margin-right: auto;">
                Step into an ultra-luxurious cyber intelligence nexus powered by Gemini 3.5 Flash Lite. Authenticate via Google to initialize your secure session.
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    col_empty1, col_btn, col_empty2 = st.columns([0.1, 2.8, 0.1])
    with col_btn:
        st.write("")
        st.button("🔑 Authenticate with Google", on_click=st.login, use_container_width=True, type="primary")
    st.stop()

current_messages = current_session_data["messages"]

for message in current_messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 8. Realtime Chat & Animated Response Engine
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
                <span class="ai-thinking-text">Processing Luxe Stream...</span>
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
                        f"""<div class="ai-replying-badge">👑 Luxe Transmission Active</div>\n\n{full_response}▌""",
                        unsafe_allow_html=True
                    )
            
            message_placeholder.markdown(
                f"""<div class="ai-replying-badge">👑 Luxe Transmission Complete</div>\n\n{full_response}""",
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
