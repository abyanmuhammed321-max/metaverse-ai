import uuid
import streamlit as st
from google import genai
from google.genai import errors
from google.genai import types

# 1. Page Configuration
st.set_page_config(
    page_title="METAVERSE_AI",
    page_icon="🌌",
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

# 3. Clean, Solid High-Contrast Professional Dark Theme (No Blur, Perfectly Crisp Text)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;500;700;900&family=Inter:wght@400;500;600&display=swap');

    .stApp {
        background-color: #0b0f19 !important;
        color: #f1f5f9 !important;
        font-family: 'Inter', sans-serif;
    }

    [data-testid="stSidebar"] {
        background-color: #0f172a !important;
        border-right: 1px solid #1e293b;
    }
    
    [data-testid="stSidebar"] * {
        color: #f1f5f9 !important;
    }

    /* METAVERSE_AI Solid Title */
    .metaverse-title {
        text-align: center;
        font-family: 'Orbitron', sans-serif;
        font-size: 2.8rem;
        font-weight: 900;
        background: linear-gradient(135deg, #38bdf8 0%, #a855f7 50%, #ec4899 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        letter-spacing: 2px;
        margin-bottom: 0px;
        padding-top: 10px;
    }
    
    .metaverse-subtitle {
        text-align: center;
        font-family: 'Orbitron', sans-serif;
        color: #94a3b8;
        font-size: 0.9rem;
        letter-spacing: 1.5px;
        margin-bottom: 25px;
        text-transform: uppercase;
    }

    /* 100% Solid & Crisp Chat Bubbles (Zero Overlays / Zero Blur) */
    .stChatMessage {
        background-color: #111827 !important;
        border: 1px solid #374151 !important;
        border-radius: 12px !important;
        padding: 16px !important;
        margin-bottom: 14px !important;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3);
    }

    /* Guarantee absolute clarity for all text inside messages */
    .stChatMessage p, .stChatMessage span, .stChatMessage div, .stMarkdown {
        color: #f8fafc !important;
        font-size: 1.02rem !important;
        line-height: 1.6 !important;
    }

    /* Modern Professional Buttons */
    .stButton button {
        border-radius: 8px !important;
        font-family: 'Orbitron', sans-serif !important;
        font-weight: 600 !important;
        font-size: 0.8rem !important;
        letter-spacing: 0.5px !important;
        border: 1px solid #4b5563 !important;
        background-color: #1f2937 !important;
        color: #38bdf8 !important;
        transition: all 0.2s ease !important;
    }
    
    .stButton button:hover {
        border-color: #38bdf8 !important;
        background-color: #374151 !important;
        color: #ffffff !important;
    }

    /* High-Tech Loader */
    .metaverse-loader {
        display: flex;
        align-items: center;
        gap: 8px;
        padding: 10px 16px;
        background-color: #1f2937;
        border: 1px solid #4b5563;
        border-radius: 8px;
        width: fit-content;
        margin: 10px 0;
    }

    .m-dot {
        width: 8px;
        height: 8px;
        background-color: #38bdf8;
        border-radius: 50%;
        animation: mPulse 1.2s infinite ease-in-out both;
    }

    .m-dot:nth-child(1) { animation-delay: -0.32s; }
    .m-dot:nth-child(2) { animation-delay: -0.16s; }
    .m-dot:nth-child(3) { animation-delay: 0s; }

    @keyframes mPulse {
        0%, 80%, 100% { transform: scale(0); opacity: 0.3; }
        40% { transform: scale(1.2); opacity: 1; }
    }
</style>
""", unsafe_allow_html=True)

# 4. Sidebar Professional Navigation & Archive Panel
with st.sidebar:
    st.markdown("### 🌌 METAVERSE IDENTITY")
    
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
            st.markdown(f"<div style='background-color: #1f2937; border-left: 3px solid #38bdf8; padding: 6px 10px; font-size: 0.78rem; margin-bottom: 6px; border-radius: 4px; color: #f1f5f9;'>{clip[:70]}...</div>", unsafe_allow_html=True)
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
st.markdown(f'<p class="metaverse-subtitle">Next-Gen Solid High-Contrast Intelligence • Language: {lang_choice}</p>', unsafe_allow_html=True)

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
                <span style="font-size: 0.8rem; font-family: 'Orbitron', sans-serif; color: #38bdf8; letter-spacing: 1px;">SYNTHESIZING MATRIX...</span>
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
            
            system_instruction = f"You are METAVERSE_AI, an advanced crystal-clear AI assistant built on cutting-edge Google architecture. Respond natively in {lang_choice}."
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
