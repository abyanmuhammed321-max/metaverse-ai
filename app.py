import uuid
import streamlit as st
from google import genai
from google.genai import errors
from google.genai import types

# 1. Page Configuration
st.set_page_config(
    page_title="METAVERSE_AI",
    page_icon="🔮",
    layout="centered",
    initial_sidebar_state="expanded"
)

api_key = st.secrets.get("GEMINI_API_KEY")

try:
    is_logged_in = getattr(st.user, "is_logged_in", False)
    user_email = getattr(st.user, "email", "default_guest_user")
except Exception:
    is_logged_in = False
    user_email = "default_guest_user"

storage_key = f"metaverse_ai_sessions_{user_email.replace('@', '_at_').replace('.', '_')}"
prefs_storage_key = f"metaverse_ai_prefs_{user_email.replace('@', '_at_').replace('.', '_')}"

# Initialize default preferences with Gemini 3.1 Flash Lite
if prefs_storage_key not in st.session_state:
    st.session_state[prefs_storage_key] = {
        "selected_model": "gemini-3.1-flash-lite",
        "lang_choice": "English"
    }

# 2. Comprehensive Persistent Storage (Chats & State Sync)
if storage_key not in st.session_state:
    first_sid = str(uuid.uuid4())
    st.session_state[storage_key] = {
        first_sid: {
            "title": "🔮 Metaverse Node 1",
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

# Initialize Settings Dialog State
if "show_settings_modal" not in st.session_state:
    st.session_state["show_settings_modal"] = False

# 3. Cyberpunk Neon UI/UX Matrix Style (Clean standard text box)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;600;800;900&family=Inter:wght@400;500;600&display=swap');

    .stApp {
        background-color: #03050c !important;
        color: #f1f5f9 !important;
        font-family: 'Inter', sans-serif;
    }

    /* --- ADVANCED CYBERPUNK NEON GLOW GRID & AMBIENT ORBS --- */
    @keyframes neonGlowPulse {
        0%, 100% { opacity: 0.18; transform: scale(1); }
        50% { opacity: 0.4; transform: scale(1.06); }
    }

    .cyber-grid-bg {
        position: fixed;
        top: 0;
        left: 0;
        width: 100vw;
        height: 100vh;
        background-image: 
            linear-gradient(rgba(0, 243, 255, 0.035) 1px, transparent 1px),
            linear-gradient(90deg, rgba(188, 19, 254, 0.035) 1px, transparent 1px);
        background-size: 35px 35px;
        z-index: 0;
        pointer-events: none;
    }

    .neon-orb-top {
        position: fixed;
        top: 5vh;
        left: 10vw;
        width: 35vw;
        height: 35vw;
        background: radial-gradient(circle, rgba(0, 243, 255, 0.15) 0%, transparent 70%);
        border-radius: 50%;
        animation: neonGlowPulse 7s infinite ease-in-out;
        z-index: 0;
        pointer-events: none;
    }

    .neon-orb-bottom {
        position: fixed;
        bottom: 5vh;
        right: 10vw;
        width: 35vw;
        height: 35vw;
        background: radial-gradient(circle, rgba(255, 0, 127, 0.15) 0%, transparent 70%);
        border-radius: 50%;
        animation: neonGlowPulse 9s infinite ease-in-out;
        z-index: 0;
        pointer-events: none;
    }

    /* --- SMOOTH POPUP ANIMATION FOR MODALS --- */
    @keyframes modalPopupFadeIn {
        0% { opacity: 0; transform: scale(0.85) translateY(20px); }
        100% { opacity: 1; transform: scale(1) translateY(0); }
    }

    div[data-testid="stModal"] > div {
        animation: modalPopupFadeIn 0.3s cubic-bezier(0.16, 1, 0.3, 1) forwards !important;
        background-color: #080c19 !important;
        border: 1px solid #00f3ff !important;
        box-shadow: 0 0 40px rgba(0, 243, 255, 0.35) !important;
        border-radius: 16px !important;
    }

    /* --- SIDEBAR NEON UX STYLING --- */
    [data-testid="stSidebar"] {
        background-color: #060913 !important;
        border-right: 1px solid rgba(0, 243, 255, 0.15);
        z-index: 10;
    }
    
    [data-testid="stSidebar"] * {
        color: #f1f5f9 !important;
    }

    /* --- METAVERSE HEADER GLOW TITLE --- */
    .metaverse-title {
        text-align: center;
        font-family: 'Orbitron', sans-serif;
        font-size: 2.9rem;
        font-weight: 900;
        background: linear-gradient(135deg, #00f3ff 0%, #bc13fe 50%, #ff007f 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-shadow: 0 0 30px rgba(0, 243, 255, 0.45);
        letter-spacing: 2.5px;
        margin-bottom: 0px;
        padding-top: 10px;
        position: relative;
        z-index: 2;
    }
    
    .metaverse-subtitle {
        text-align: center;
        font-family: 'Orbitron', sans-serif;
        color: #00f3ff;
        font-size: 0.88rem;
        letter-spacing: 2px;
        margin-bottom: 25px;
        text-transform: uppercase;
        position: relative;
        z-index: 2;
        text-shadow: 0 0 10px rgba(0, 243, 255, 0.3);
    }

    /* --- NEON-BORDERED HOLOGRAPHIC CHAT BUBBLES --- */
    .stChatMessage {
        background-color: rgba(10, 15, 30, 0.85) !important;
        border: 1px solid rgba(0, 243, 255, 0.25) !important;
        border-radius: 14px !important;
        padding: 18px !important;
        margin-bottom: 16px !important;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.7), inset 0 0 12px rgba(0, 243, 255, 0.04);
        position: relative;
        backdrop-filter: blur(10px);
        z-index: 2;
    }

    .stChatMessage p, .stChatMessage span, .stChatMessage div, .stMarkdown {
        color: #f8fafc !important;
        font-size: 1.02rem !important;
        line-height: 1.65 !important;
    }

    /* --- CYBERPUNK NEON BUTTONS --- */
    .stButton button {
        border-radius: 8px !important;
        font-family: 'Orbitron', sans-serif !important;
        font-weight: 600 !important;
        font-size: 0.78rem !important;
        letter-spacing: 0.8px !important;
        border: 1px solid rgba(0, 243, 255, 0.4) !important;
        background: linear-gradient(135deg, rgba(13, 22, 43, 0.9), rgba(26, 11, 46, 0.9)) !important;
        color: #00f3ff !important;
        box-shadow: 0 0 12px rgba(0, 243, 255, 0.15);
        transition: all 0.25s ease !important;
        z-index: 2;
    }
    
    .stButton button:hover {
        border-color: #00f3ff !important;
        background: linear-gradient(135deg, rgba(0, 243, 255, 0.2), rgba(188, 19, 254, 0.2)) !important;
        color: #ffffff !important;
        box-shadow: 0 0 20px rgba(0, 243, 255, 0.5), inset 0 0 8px rgba(0, 243, 255, 0.3);
        transform: translateY(-1px);
    }

    /* --- CLEAN STANDARD CHAT INPUT FIELD (NO NEON GLOW) --- */
    [data-testid="stChatInput"] textarea {
        background-color: #0d111a !important;
        color: #e2e8f0 !important;
        border: 1px solid #334155 !important;
        border-radius: 8px !important;
        font-family: 'Inter', sans-serif !important;
        box-shadow: none !important;
    }
    
    [data-testid="stChatInput"] textarea:focus {
        border-color: #64748b !important;
        box-shadow: none !important;
    }

    /* --- ADVANCED HOLOGRAPHIC AI LOADING BOX --- */
    .metaverse-loader-box {
        display: flex;
        flex-direction: column;
        gap: 12px;
        padding: 18px 22px;
        background: linear-gradient(135deg, rgba(8, 13, 26, 0.95), rgba(20, 10, 38, 0.95));
        border: 1px solid #00f3ff;
        border-radius: 14px;
        width: 100%;
        max-width: 320px;
        margin: 12px 0;
        position: relative;
        z-index: 2;
        box-shadow: 0 0 25px rgba(0, 243, 255, 0.3), inset 0 0 12px rgba(0, 243, 255, 0.12);
        animation: boxGlowPulse 2s infinite ease-in-out;
    }

    @keyframes boxGlowPulse {
        0%, 100% { border-color: rgba(0, 243, 255, 0.6); box-shadow: 0 0 20px rgba(0, 243, 255, 0.25); }
        50% { border-color: rgba(188, 19, 254, 0.9); box-shadow: 0 0 30px rgba(188, 19, 254, 0.5); }
    }

    .loader-header {
        display: flex;
        align-items: center;
        gap: 12px;
    }

    .m-core-ring {
        width: 20px;
        height: 20px;
        border: 2px solid rgba(0, 243, 255, 0.2);
        border-top: 2px solid #00f3ff;
        border-radius: 50%;
        animation: spinRing 0.75s linear infinite;
        box-shadow: 0 0 10px #00f3ff;
    }

    @keyframes spinRing {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }

    .loader-text {
        font-size: 0.84rem;
        font-family: 'Orbitron', sans-serif;
        color: #00f3ff;
        letter-spacing: 1.5px;
        font-weight: 700;
        text-shadow: 0 0 8px rgba(0, 243, 255, 0.4);
    }

    .loader-progress-track {
        width: 100%;
        height: 4px;
        background-color: #060913;
        border-radius: 4px;
        overflow: hidden;
        position: relative;
    }

    .loader-progress-fill {
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, #00f3ff, #bc13fe, #ff007f, transparent);
        animation: progressWave 1.5s infinite linear;
    }

    @keyframes progressWave {
        0% { left: -100%; }
        100% { left: 100%; }
    }
</style>

<!-- Neon Cyber Grid and Orb Layers -->
<div class="cyber-grid-bg"></div>
<div class="neon-orb-top"></div>
<div class="neon-orb-bottom"></div>
""", unsafe_allow_html=True)

# 4. Sidebar Professional Navigation & Persistent Chat Archive Panel
with st.sidebar:
    st.markdown("### 🔮 METAVERSE IDENTITY")
    
    if not is_logged_in:
        st.write("<span style='font-size: 0.8rem; color: #94a3b8;'>Authenticate with Google to activate permanent cloud synchronization.</span>", unsafe_allow_html=True)
        st.button("🌐 Connect Google ID", on_click=st.login, use_container_width=True, type="primary")
    else:
        user_name = getattr(st.user, "name", "Meta Operative")
        st.success(f"**{user_name}**")
        st.write(f"<span style='font-size: 0.72rem; color: #94a3b8;'>{user_email}</span>", unsafe_allow_html=True)
        st.button("Disconnect Node", on_click=st.logout, use_container_width=True)
            
    st.markdown("---")
    
    if st.button("➕ New Metaverse Node", use_container_width=True, type="primary"):
        new_sid = str(uuid.uuid4())
        st.session_state[storage_key][new_sid] = {
            "title": f"Node {len(st.session_state[storage_key]) + 1}",
            "messages": []
        }
        st.session_state[f"{storage_key}_current_sid"] = new_sid
        st.rerun()
        
    st.markdown("### 🗄️ SAVED CHATS & NODES")
    
    for sid, sdata in list(st.session_state[storage_key].items()):
        col1, col2 = st.columns([0.76, 0.24])
        with col1:
            btn_type = "primary" if sid == current_sid else "secondary"
            display_title = sdata["title"][:16] + ("..." if len(sdata["title"]) > 16 else "")
            if st.button(display_title, key=f"sel_{sid}", use_container_width=True, type=btn_type):
                st.session_state[f"{storage_key}_current_sid"] = sid
                st.rerun()
        with col2:
            if st.button("🗑️", key=f"del_{sid}", help="Purge Node"):
                del st.session_state[storage_key][sid]
                if not st.session_state[storage_key]:
                    fresh_sid = str(uuid.uuid4())
                    st.session_state[storage_key][fresh_sid] = {"title": "Node 1", "messages": []}
                    st.session_state[f"{storage_key}_current_sid"] = fresh_sid
                else:
                    st.session_state[f"{storage_key}_current_sid"] = list(st.session_state[storage_key].keys())[0]
                st.rerun()

if not api_key:
    st.error("⚠️ GEMINI_API_KEY configuration missing in `.streamlit/secrets.toml`.")
    st.stop()

# 5. Top Bar with Settings Icon Pop-up Trigger (Corner)
col_top1, col_top2 = st.columns([0.92, 0.08])
with col_top2:
    if st.button("⚙️", help="System Settings Matrix"):
        st.session_state["show_settings_modal"] = True

# 6. Animated Settings Modal Popup Dialog
@st.dialog("⚙️ SYSTEM SETTINGS MATRIX")
def settings_modal():
    st.markdown("<span style='color: #94a3b8; font-size: 0.85rem;'>Configure Quantum Model Cores and Linguistic matrices below. Preferences save automatically for future sessions.</span>", unsafe_allow_html=True)
    st.markdown("---")

    # Updated modern/latest Gemini models list including gemini-3.1-flash-lite
    models_list = ["gemini-3.1-flash-lite", "gemini-2.5-flash", "gemini-2.5-pro", "gemini-2.0-flash"]
    current_saved_model = st.session_state[prefs_storage_key].get("selected_model", "gemini-3.1-flash-lite")
    model_index = models_list.index(current_saved_model) if current_saved_model in models_list else 0

    selected_model_input = st.selectbox(
        "⚡ Quantum Model Core (Gemini 3.1 & Latest)",
        models_list,
        index=model_index,
        key="modal_model_select"
    )

    st.markdown("---")

    # Language Selection
    languages = ["English", "Malayalam", "Spanish", "French", "German", "Hindi", "Japanese", "Chinese", "Portuguese", "Arabic"]
    current_saved_lang = st.session_state[prefs_storage_key].get("lang_choice", "English")
    lang_index = languages.index(current_saved_lang) if current_saved_lang in languages else 0

    lang_choice_input = st.selectbox(
        "Language Matrix",
        languages,
        index=lang_index,
        key="modal_lang_select"
    )
    
    st.markdown("---")
    if st.button("💾 Save & Close Matrix", use_container_width=True, type="primary"):
        st.session_state[prefs_storage_key]["selected_model"] = selected_model_input
        st.session_state[prefs_storage_key]["lang_choice"] = lang_choice_input
        st.session_state["show_settings_modal"] = False
        st.rerun()

if st.session_state.get("show_settings_modal", False):
    settings_modal()

# Retrieve active persistent preferences
selected_model = st.session_state[prefs_storage_key].get("selected_model", "gemini-3.1-flash-lite")
lang_choice = st.session_state[prefs_storage_key].get("lang_choice", "English")

# 7. Main Canvas Interface Layout
st.markdown(f'<p class="metaverse-title">METAVERSE_AI</p>', unsafe_allow_html=True)
st.markdown(f'<p class="metaverse-subtitle">Model: {selected_model} • Language: {lang_choice}</p>', unsafe_allow_html=True)

if not is_logged_in:
    st.warning("🔒 **Authorization Required:** Please click **'Connect Google ID'** in the sidebar to initialize secure persistent cloud storage across reloads.")
    st.stop()

current_messages = current_session_data["messages"]

# Render Existing Saved Chat Messages
for msg_idx, message in enumerate(current_messages):
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 8. Realtime Prompt Processing & Automated State Archiving
if prompt := st.chat_input("Transmit prompt to METAVERSE_AI..."):
    if len(current_messages) == 0:
        current_session_data["title"] = prompt[:22]

    current_messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        loader_placeholder = st.empty()
        loader_placeholder.markdown("""
            <div class="metaverse-loader-box">
                <div class="loader-header">
                    <div class="m-core-ring"></div>
                    <span class="loader-text">SYNTHESIZING MATRIX...</span>
                </div>
                <div class="loader-progress-track">
                    <div class="loader-progress-fill"></div>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        message_placeholder = st.empty()
        full_response = ""
        
        try:
            client = genai.Client(api_key=api_key)
            
            chat_history_formatted = [
                {"role": m["role"], "parts": [{"text": m["content"]}]} 
                for m in current_messages
            ]
            
            system_instruction = f"You are METAVERSE_AI, an advanced high-visibility AI assistant built on cutting-edge Google architecture. Respond natively in {lang_choice}."
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
            full_response = f"❌ **API Error:** {e}"
            message_placeholder.markdown(full_response)
        except Exception as e:
            loader_placeholder.empty()
            full_response = f"❌ **Error:** {str(e)}"
            message_placeholder.markdown(full_response)

        current_messages.append({"role": "model", "content": full_response})
