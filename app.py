import uuid
import streamlit as st
from google import genai
from google.genai import errors
from google.genai import types

# 1. Page Configuration
st.set_page_config(
    page_title="_METAVERSE_AI",
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

storage_key = f"neon_meta_sessions_{user_email.replace('@', '_at_').replace('.', '_')}"

# 2. Comprehensive Persistent Storage (Chats, Selections, UI States)
if storage_key not in st.session_state:
    first_sid = str(uuid.uuid4())
    st.session_state[storage_key] = {
        first_sid: {
            "title": "⚡ Quantum Session 1",
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

# 3. High-Professional Cyberpunk Neon UI Theme Stylesheet
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;500;700;900&family=Plus+Jakarta+Sans:wght@300;400;500;600&display=swap');

    .stApp {
        background-color: #050508 !important;
        color: #00f0ff !important;
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    
    [data-testid="stSidebar"] {
        background-color: #090a0f !important;
        border-right: 1px solid rgba(0, 240, 255, 0.2);
        box-shadow: inset -5px 0 20px rgba(0, 240, 255, 0.03);
    }
    
    [data-testid="stSidebar"] * {
        color: #e0e6ed !important;
    }

    /* Neon Holographic Glow Titles */
    .neon-title {
        text-align: center;
        font-family: 'Orbitron', sans-serif;
        font-size: 2.8rem;
        font-weight: 900;
        background: linear-gradient(135deg, #00f0ff 0%, #7000ff 50%, #ff007f 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-shadow: 0 0 30px rgba(0, 240, 255, 0.4);
        letter-spacing: 2px;
        margin-bottom: 0px;
        padding-top: 10px;
    }
    
    .neon-subtitle {
        text-align: center;
        font-family: 'Orbitron', sans-serif;
        color: #a0aec0;
        font-size: 0.95rem;
        letter-spacing: 1px;
        margin-bottom: 30px;
        text-transform: uppercase;
    }

    /* Cyberpunk Glassmorphism Chat Message Bubbles */
    .stChatMessage {
        background: rgba(15, 18, 30, 0.7) !important;
        border: 1px solid rgba(0, 240, 255, 0.25) !important;
        border-radius: 14px !important;
        padding: 16px !important;
        margin-bottom: 14px !important;
        box-shadow: 0 0 20px rgba(0, 240, 255, 0.05), inset 0 0 10px rgba(0, 240, 255, 0.02);
    }

    /* Holographic Cyber Buttons */
    .stButton button {
        border-radius: 10px !important;
        font-family: 'Orbitron', sans-serif !important;
        font-weight: 600 !important;
        font-size: 0.82rem !important;
        letter-spacing: 0.5px !important;
        border: 1px solid rgba(0, 240, 255, 0.4) !important;
        background: rgba(0, 240, 255, 0.05) !important;
        color: #00f0ff !important;
        transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1) !important;
    }
    
    .stButton button:hover {
        border-color: #ff007f !important;
        background: rgba(255, 0, 127, 0.15) !important;
        color: #fff !important;
        box-shadow: 0 0 15px rgba(255, 0, 127, 0.5) !important;
    }

    /* Quantum Cyber Pulsating Loader */
    .quantum-loader {
        display: flex;
        align-items: center;
        gap: 8px;
        padding: 12px 16px;
        background: rgba(112, 0, 255, 0.1);
        border: 1px solid rgba(112, 0, 255, 0.4);
        border-radius: 12px;
        width: fit-content;
        margin: 10px 0;
        box-shadow: 0 0 15px rgba(112, 0, 255, 0.2);
    }

    .q-dot {
        width: 8px;
        height: 8px;
        background-color: #00f0ff;
        border-radius: 50%;
        animation: qPulse 1.2s infinite ease-in-out both;
    }

    .q-dot:nth-child(1) { animation-delay: -0.32s; }
    .q-dot:nth-child(2) { animation-delay: -0.16s; }
    .q-dot:nth-child(3) { animation-delay: 0s; }

    @keyframes qPulse {
        0%, 80%, 100% { transform: scale(0); opacity: 0.2; }
        40% { transform: scale(1.2); opacity: 1; box-shadow: 0 0 10px #00f0ff; }
    }
</style>
""", unsafe_allow_html=True)

# 4. Sidebar Professional Navigation & Archive Panel
with st.sidebar:
    st.markdown("### ⚡ QUANTUM IDENTITY")
    
    if not is_logged_in:
        st.write("<span style='font-size: 0.8rem; color: #a0aec0;'>Authorize with Google to activate permanent state sync across devices.</span>", unsafe_allow_html=True)
        st.button("🌐 Connect Google ID", on_click=st.login, use_container_width=True, type="primary")
    else:
        user_name = getattr(st.user, "name", "Cyber Operative")
        st.success(f"**{user_name}**")
        st.write(f"<span style='font-size: 0.72rem; color: #a0aec0;'>{user_email}</span>", unsafe_allow_html=True)
        st.button("Disconnect Node", on_click=st.logout, use_container_width=True)
            
    st.markdown("---")
    
    if st.button("➕ New Quantum Session", use_container_width=True, type="primary"):
        new_sid = str(uuid.uuid4())
        st.session_state[storage_key][new_sid] = {
            "title": f"Session {len(st.session_state[storage_key]) + 1}",
            "messages": [],
            "selected_snippets": []
        }
        st.session_state[f"{storage_key}_current_sid"] = new_sid
        st.rerun()
        
    st.markdown("### 🗄️ ARCHIVED SESSIONS")
    
    for sid, sdata in list(st.session_state[storage_key].items()):
        col1, col2 = st.columns([0.76, 0.24])
        with col1:
            btn_type = "primary" if sid == current_sid else "secondary"
            display_title = sdata["title"][:16] + ("..." if len(sdata["title"]) > 16 else "")
            if st.button(display_title, key=f"sel_{sid}", use_container_width=True, type=btn_type):
                st.session_state[f"{storage_key}_current_sid"] = sid
                st.rerun()
        with col2:
            if st.button("🗑️", key=f"del_{sid}", help="Purge Session"):
                del st.session_state[storage_key][sid]
                if not st.session_state[storage_key]:
                    fresh_sid = str(uuid.uuid4())
                    st.session_state[storage_key][fresh_sid] = {"title": "Session 1", "messages": [], "selected_snippets": []}
                    st.session_state[f"{storage_key}_current_sid"] = fresh_sid
                else:
                    st.session_state[f"{storage_key}_current_sid"] = list(st.session_state[storage_key].keys())[0]
                st.rerun()

    st.markdown("---")
    st.markdown("### 📌 SAVED CLIPS & SELECTIONS")
    
    saved_snippets = current_session_data.get("selected_snippets", [])
    if not saved_snippets:
        st.info("No text selections saved in this session yet.")
    else:
        for idx, clip in enumerate(saved_snippets):
            st.markdown(f"<div style='background: rgba(0,240,255,0.04); border-left: 2px solid #00f0ff; padding: 6px 10px; font-size: 0.78rem; margin-bottom: 6px; border-radius: 4px;'>{clip[:70]}...</div>", unsafe_allow_html=True)
        if st.button("🧹 Clear Saved Clips", use_container_width=True):
            current_session_data["selected_snippets"] = []
            st.rerun()

    st.markdown("---")
    st.markdown("### ⚙️ NEURAL SETTINGS")
    
    selected_model = st.selectbox(
        "Core Engine",
        ["gemini-3.7-flash", "gemini-3.6-flash", "gemini-3.1-flash-lite"],
        index=0
    )

    languages = ["English", "Malayalam", "Spanish", "French", "German", "Hindi", "Japanese", "Chinese", "Portuguese", "Arabic"]
    lang_choice = st.selectbox(
        "Output Matrix Language",
        languages,
        index=0
    )

if not api_key:
    st.error("⚠️ GEMINI_API_KEY configuration missing in `.streamlit/secrets.toml`.")
    st.stop()

# 5. Main Canvas Interface Layout
st.markdown(f'<p class="neon-title">NEON_META_AI</p>', unsafe_allow_html=True)
st.markdown(f'<p class="neon-subtitle">Quantum Neural Interface • Active Language: {lang_choice}</p>', unsafe_allow_html=True)

if not is_logged_in:
    st.warning("🔒 **Authorization Required:** Please click **'Connect Google ID'** in the sidebar to initialize secure persistent cloud storage.")
    st.stop()

current_messages = current_session_data["messages"]

# Render Existing Saved Chat Messages
for msg_idx, message in enumerate(current_messages):
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        
        # Interactive Option: Save specific AI response blocks or selections directly
        if message["role"] == "model":
            save_btn_key = f"save_clip_{current_sid}_{msg_idx}"
            if st.button("📌 Save this AI Output", key=save_btn_key):
                if message["content"] not in current_session_data["selected_snippets"]:
                    current_session_data["selected_snippets"].append(message["content"])
                    st.success("Successfully saved to Selections Vault!")
                    st.rerun()

# 6. Realtime Prompt Processing & Automated State Archiving
if prompt := st.chat_input("Transmit prompt to neural matrix..."):
    if len(current_messages) == 0:
        current_session_data["title"] = prompt[:22]

    current_messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        loader_placeholder = st.empty()
        loader_placeholder.markdown("""
            <div class="quantum-loader">
                <div class="q-dot"></div>
                <div class="q-dot"></div>
                <div class="q-dot"></div>
                <span style="font-size: 0.8rem; font-family: 'Orbitron', sans-serif; color: #00f0ff; letter-spacing: 0.5px;">SYNTHESIZING MATRIX...</span>
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
            
            system_instruction = f"You are NEON_META_AI, an elite high-professional quantum AI agent. Respond natively in {lang_choice}."
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
