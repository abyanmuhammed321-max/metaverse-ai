import uuid
import streamlit as st
from google import genai
from google.genai import errors
from google.genai import types

# 1. Page Configuration
st.set_page_config(
    page_title="METAVERSE_AI",
    page_icon="⚡",
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

# 2. Comprehensive Persistent Storage (Chats, Selections, UI States)
if storage_key not in st.session_state:
    first_sid = str(uuid.uuid4())
    st.session_state[storage_key] = {
        first_sid: {
            "title": "🌌 Metaverse Node 1",
            "messages": [],
            "selected_snippets": []
        }
    }

if f"{storage_key}_current_sid" not in st.session_state:
    st.session_state[f"{storage_key}_current_sid"] = list(st.session_state[storage_key].keys())[0]

current_sid = st.session_state[f"{storage_key}_current_sid"]
if current_sid not in st.session_state[storage_key]:
    st.session_state[f"{storage_key}_current_sid"] = list(st.session_state[storage_key].keys())[0]
    current_sid = st.session_state[f"{storage_key}_current_sid"]

current_session_data = st.session_state[storage_key][current_sid]

# 3. High-Tech Cyber-Neon Background Animation & Ultimate Futuristic UI
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;500;700;900&family=Rajdhani:wght@400;500;600;700&display=swap');

    .stApp {
        background-color: #030305 !important;
        color: #00ffcc !important;
        font-family: 'Rajdhani', sans-serif;
        background-image: 
            radial-gradient(circle at 15% 20%, rgba(0, 255, 204, 0.04) 0%, transparent 40%),
            radial-gradient(circle at 85% 80%, rgba(138, 43, 226, 0.05) 0%, transparent 40%);
        overflow-x: hidden;
    }

    /* --- BACKGROUND ANIMATED HOLOGRAPHIC GRID & SCANLINES --- */
    .stApp::before {
        content: " ";
        display: block;
        position: fixed;
        top: 0; left: 0; bottom: 0; right: 0;
        background: linear-gradient(rgba(18, 16, 16, 0) 50%, rgba(0, 0, 0, 0.25) 50%), 
                    linear-gradient(90deg, rgba(255, 0, 0, 0.03), rgba(0, 255, 0, 0.01), rgba(0, 0, 255, 0.03));
        z-index: 99999;
        background-size: 100% 3px, 6px 100%;
        pointer-events: none;
    }

    /* --- DYNAMIC FLOATING METAVERSE NEON PARTICLES ANIMATION --- */
    @keyframes bgParticles {
        0% { transform: translateY(0px) rotate(0deg); opacity: 0.15; }
        50% { transform: translateY(-15px) rotate(180deg); opacity: 0.35; filter: drop-shadow(0 0 12px #00ffcc); }
        100% { transform: translateY(0px) rotate(360deg); opacity: 0.15; }
    }

    .stApp::after {
        content: "";
        position: fixed;
        width: 100vw;
        height: 100vh;
        top: 0;
        left: 0;
        background-image: radial-gradient(#00ffcc 1px, transparent 1px);
        background-size: 40px 40px;
        opacity: 0.08;
        animation: bgParticles 12s infinite ease-in-out;
        pointer-events: none;
        z-index: 0;
    }

    [data-testid="stSidebar"] {
        background-color: #07090f !important;
        border-right: 1px solid rgba(0, 255, 204, 0.2);
        box-shadow: inset -5px 0 25px rgba(0, 255, 204, 0.04);
        z-index: 10;
    }
    
    [data-testid="stSidebar"] * {
        color: #d1dcf5 !important;
    }

    /* METAVERSE_AI Holographic Glowing Title with Pulsing Neon Gradient */
    @keyframes titleGlow {
        0%, 100% { filter: drop-shadow(0 0 15px rgba(0, 255, 204, 0.4)); }
        50% { filter: drop-shadow(0 0 30px rgba(138, 43, 226, 0.8)); }
    }

    .metaverse-title {
        text-align: center;
        font-family: 'Orbitron', sans-serif;
        font-size: 3rem;
        font-weight: 900;
        background: linear-gradient(135deg, #00ffcc 0%, #7928ca 50%, #ff007f 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        letter-spacing: 3px;
        margin-bottom: 0px;
        padding-top: 10px;
        animation: titleGlow 4s infinite ease-in-out;
    }
    
    .metaverse-subtitle {
        text-align: center;
        font-family: 'Orbitron', sans-serif;
        color: #8fa3cc;
        font-size: 0.9rem;
        letter-spacing: 2px;
        margin-bottom: 25px;
        text-transform: uppercase;
    }

    /* High-Tech Glassmorphism Message Bubbles */
    .stChatMessage {
        background: rgba(10, 14, 23, 0.8) !important;
        border: 1px solid rgba(0, 255, 204, 0.3) !important;
        border-radius: 12px !important;
        padding: 16px !important;
        margin-bottom: 14px !important;
        box-shadow: 0 0 20px rgba(0, 255, 204, 0.06), inset 0 0 10px rgba(0, 255, 204, 0.02);
        backdrop-filter: blur(10px);
        position: relative;
        z-index: 2;
    }

    /* Holographic Cyber Buttons */
    .stButton button {
        border-radius: 8px !important;
        font-family: 'Orbitron', sans-serif !important;
        font-weight: 700 !important;
        font-size: 0.8rem !important;
        letter-spacing: 1px !important;
        border: 1px solid rgba(0, 255, 204, 0.4) !important;
        background: rgba(0, 255, 204, 0.06) !important;
        color: #00ffcc !important;
        transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1) !important;
    }
    
    .stButton button:hover {
        border-color: #ff007f !important;
        background: rgba(255, 0, 127, 0.2) !important;
        color: #ffffff !important;
        box-shadow: 0 0 20px rgba(255, 0, 127, 0.6) !important;
        transform: translateY(-1px);
    }

    /* High-Tech Pulsating Neural Stream Loader */
    .metaverse-loader {
        display: flex;
        align-items: center;
        gap: 8px;
        padding: 12px 18px;
        background: rgba(121, 40, 202, 0.12);
        border: 1px solid rgba(0, 255, 204, 0.5);
        border-radius: 12px;
        width: fit-content;
        margin: 10px 0;
        box-shadow: 0 0 20px rgba(0, 255, 204, 0.2);
    }

    .m-dot {
        width: 8px;
        height: 8px;
        background-color: #00ffcc;
        border-radius: 50%;
        animation: mPulse 1.2s infinite ease-in-out both;
    }

    .m-dot:nth-child(1) { animation-delay: -0.32s; }
    .m-dot:nth-child(2) { animation-delay: -0.16s; }
    .m-dot:nth-child(3) { animation-delay: 0s; }

    @keyframes mPulse {
        0%, 80%, 100% { transform: scale(0); opacity: 0.2; }
        40% { transform: scale(1.3); opacity: 1; box-shadow: 0 0 12px #00ffcc; }
    }
</style>
""", unsafe_allow_html=True)

# 4. Sidebar Professional Navigation & Archive Panel
with st.sidebar:
    st.markdown("### 🌌 METAVERSE IDENTITY")
    
    if not is_logged_in:
        st.write("<span style='font-size: 0.8rem; color: #8fa3cc;'>Authenticate with Google to activate permanent cloud synchronization.</span>", unsafe_allow_html=True)
        st.button("🌐 Connect Google ID", on_click=st.login, use_container_width=True, type="primary")
    else:
        user_name = getattr(st.user, "name", "Meta Operative")
        st.success(f"**{user_name}**")
        st.write(f"<span style='font-size: 0.72rem; color: #8fa3cc;'>{user_email}</span>", unsafe_allow_html=True)
        st.button("Disconnect Node", on_click=st.logout, use_container_width=True)
            
    st.markdown("---")
    
    if st.button("➕ New Metaverse Node", use_container_width=True, type="primary"):
        new_sid = str(uuid.uuid4())
        st.session_state[storage_key][new_sid] = {
            "title": f"Node {len(st.session_state[storage_key]) + 1}",
            "messages": [],
            "selected_snippets": []
        }
        st.session_state[f"{storage_key}_current_sid"] = new_sid
        st.rerun()
        
    st.markdown("### 🗄️ SAVED NODES & CHATS")
    
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
                    st.session_state[storage_key][fresh_sid] = {"title": "Node 1", "messages": [], "selected_snippets": []}
                    st.session_state[f"{storage_key}_current_sid"] = fresh_sid
                else:
                    st.session_state[f"{storage_key}_current_sid"] = list(st.session_state[storage_key].keys())[0]
                st.rerun()

    st.markdown("---")
    st.markdown("### 📌 SAVED SELECTIONS & CLIPS")
    
    saved_snippets = current_session_data.get("selected_snippets", [])
    if not saved_snippets:
        st.info("No selections or chat points saved in this node yet.")
    else:
        for idx, clip in enumerate(saved_snippets):
            st.markdown(f"<div style='background: rgba(0,255,204,0.04); border-left: 2px solid #00ffcc; padding: 6px 10px; font-size: 0.78rem; margin-bottom: 6px; border-radius: 4px; color: #e2fefc;'>{clip[:70]}...</div>", unsafe_allow_html=True)
        if st.button("🧹 Clear Saved Clips", use_container_width=True):
            current_session_data["selected_snippets"] = []
            st.rerun()

    st.markdown("---")
    st.markdown("### ⚙️ SYSTEM SETTINGS")
    
    selected_model = st.selectbox(
        "Quantum Core",
        ["gemini-3.7-flash", "gemini-3.6-flash", "gemini-3.1-flash-lite"],
        index=0
    )

    languages = ["English", "Malayalam", "Spanish", "French", "German", "Hindi", "Japanese", "Chinese", "Portuguese", "Arabic"]
    lang_choice = st.selectbox(
        "Language Matrix",
        languages,
        index=0
    )

if not api_key:
    st.error("⚠️ GEMINI_API_KEY configuration missing in `.streamlit/secrets.toml`.")
    st.stop()

# 5. Main Canvas Interface Layout
st.markdown(f'<p class="metaverse-title">METAVERSE_AI</p>', unsafe_allow_html=True)
st.markdown(f'<p class="metaverse-subtitle">Next-Gen Holographic Intelligence • Language: {lang_choice}</p>', unsafe_allow_html=True)

if not is_logged_in:
    st.warning("🔒 **Authorization Required:** Please click **'Connect Google ID'** in the sidebar to initialize secure persistent cloud storage across reloads.")
    st.stop()

current_messages = current_session_data["messages"]

# Render Existing Saved Chat Messages & Selections
for msg_idx, message in enumerate(current_messages):
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        
        # Interactive Option: Save specific AI response points/answers directly
        if message["role"] == "model":
            save_btn_key = f"save_clip_{current_sid}_{msg_idx}"
            if st.button("📌 Save this Output Point", key=save_btn_key):
                if message["content"] not in current_session_data["selected_snippets"]:
                    current_session_data["selected_snippets"].append(message["content"])
                    st.success("Successfully saved to Selections Vault!")
                    st.rerun()

# 6. Realtime Prompt Processing & Automated State Archiving
if prompt := st.chat_input("Transmit prompt to METAVERSE_AI..."):
    if len(current_messages) == 0:
        current_session_data["title"] = prompt[:22]

    current_messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        loader_placeholder = st.empty()
        loader_placeholder.markdown("""
            <div class="metaverse-loader">
                <div class="m-dot"></div>
                <div class="m-dot"></div>
                <div class="m-dot"></div>
                <span style="font-size: 0.8rem; font-family: 'Orbitron', sans-serif; color: #00ffcc; letter-spacing: 1px;">SYNTHESIZING MATRIX...</span>
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
            
            system_instruction = f"You are METAVERSE_AI, an advanced high-tech holographic AI assistant built on cutting-edge Google architecture. Respond natively in {lang_choice}."
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
