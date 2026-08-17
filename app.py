import uuid
import asyncio
import streamlit as st
from google import genai
from google.genai import errors
from google.genai import types

# 1. Page Configuration
st.set_page_config(
    page_title="Gemini Clone with Live Mode",
    page_icon="✨",
    layout="centered",
    initial_sidebar_state="expanded"
)

# Load Gemini API Key from secrets
api_key = st.secrets.get("GEMINI_API_KEY")

# 2. Handle Authentication Flow
if not st.user.is_logged_in:
    st.markdown("""
    <style>
        .stApp { background-color: #131314; color: #e3e3e3; font-family: 'Inter', sans-serif; }
        header {visibility: hidden;}
        footer {visibility: hidden;}
        .login-box { text-align: center; margin-top: 20vh; }
        .gemini-login-header {
            background: linear-gradient(90deg, #4285F4, #9B72CB, #D96570);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-size: 3rem;
            font-weight: 700;
        }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="login-box">', unsafe_allow_html=True)
    st.markdown('<p class="gemini-login-header">Gemini AI</p>', unsafe_allow_html=True)
    st.markdown('<p style="color: #8e918f; font-size: 1.1rem; margin-bottom: 30px;">Sign in with your Google account to start chatting.</p>', unsafe_allow_html=True)
    
    if st.button("🔵 Sign in with Google", use_container_width=True):
        st.login()
        
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# 3. Inject UI Styles for Main App
st.markdown("""
<style>
    .stApp { background-color: #131314; color: #e3e3e3; font-family: 'Inter', sans-serif; }
    header {visibility: hidden;}
    footer {visibility: hidden;}
    .stChatMessage { background-color: transparent !important; border-radius: 12px; padding: 10px; margin-bottom: 10px; }
    [data-testid="stChatMessage"]:nth-child(odd) { background-color: #1e1f20 !important; border: 1px solid #333537; }
    .stChatInput input { color: #e3e3e3 !important; }
    [data-testid="stSidebar"] { background-color: #1e1f20; border-right: 1px solid #333537; }
    .gemini-header {
        text-align: center;
        background: linear-gradient(90deg, #4285F4, #9B72CB, #D96570);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 0px;
    }
    .gemini-subheader { text-align: center; color: #8e918f; font-size: 1.2rem; margin-bottom: 30px; }
    .live-pulse {
        width: 15px; height: 15px; background-color: #D96570; border-radius: 50%;
        display: inline-block; box-shadow: 0 0 0 rgba(217, 101, 112, 0.4);
        animation: pulse 1.5s infinite; margin-right: 8px;
    }
    @keyframes pulse {
        0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(217, 101, 112, 0.7); }
        70% { transform: scale(1); box-shadow: 0 0 0 10px rgba(217, 101, 112, 0); }
        100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(217, 101, 112, 0); }
    }
</style>
""", unsafe_allow_html=True)

# Initialize Session Storage States
if "sessions" not in st.session_state:
    first_sid = str(uuid.uuid4())
    st.session_state.sessions = {first_sid: {"title": "New Chat", "messages": []}}
    st.session_state.current_session_id = first_sid

if "app_mode" not in st.session_state:
    st.session_state.app_mode = "Standard Chat"

if st.session_state.current_session_id not in st.session_state.sessions:
    st.session_state.current_session_id = list(st.session_state.sessions.keys())[0]

# 4. Sidebar Configuration
with st.sidebar:
    st.markdown("### 👤 User Profile")
    if hasattr(st.user, "picture") and st.user.picture:
        st.image(st.user.picture, width=50)
    st.write(f"**{getattr(st.user, 'name', 'User')}**")
    st.write(f"<span style='font-size: 0.8rem; color: #8e918f;'>{getattr(st.user, 'email', '')}</span>", unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Mode Selector (Chat vs Live Section)
    st.markdown("### 🧭 Navigation")
    mode_selection = st.radio(
        "Select Mode",
        ["Standard Chat", "Gemini Live Section"],
        index=0 if st.session_state.app_mode == "Standard Chat" else 1
    )
    if mode_selection != st.session_state.app_mode:
        st.session_state.app_mode = mode_selection
        st.rerun()

    st.markdown("---")
    
    if st.session_state.app_mode == "Standard Chat":
        if st.button("➕ New Chat", use_container_width=True, type="primary"):
            new_sid = str(uuid.uuid4())
            st.session_state.sessions[new_sid] = {"title": "New Chat", "messages": []}
            st.session_state.current_session_id = new_sid
            st.rerun()
            
        st.markdown("### 💬 Chat History")
        for sid, sdata in list(st.session_state.sessions.items()):
            col1, col2 = st.columns([0.75, 0.25])
            with col1:
                btn_type = "primary" if sid == st.session_state.current_session_id else "secondary"
                display_title = sdata["title"][:18] + ("..." if len(sdata["title"]) > 18 else "")
                if st.button(display_title, key=f"sel_{sid}", use_container_width=True, type=btn_type):
                    st.session_state.current_session_id = sid
                    st.rerun()
            with col2:
                if st.button("🗑️", key=f"del_{sid}", help="Delete chat"):
                    del st.session_state.sessions[sid]
                    if not st.session_state.sessions:
                        fresh_sid = str(uuid.uuid4())
                        st.session_state.sessions[fresh_sid] = {"title": "New Chat", "messages": []}
                        st.session_state.current_session_id = fresh_sid
                    else:
                        st.session_state.current_session_id = list(st.session_state.sessions.keys())[0]
                    st.rerun()

    st.markdown("---")
    st.markdown("### ⚙️ Settings")
    selected_model = st.selectbox(
        "Choose Model",
        ["gemini-3.6-flash", "gemini-3.1-pro-preview", "gemini-3.1-flash-live-preview"],
        index=0
    )
    
    st.markdown("---")
    if st.button("🚪 Sign Out", use_container_width=True):
        st.logout()

if not api_key:
    st.error("⚠️ GEMINI_API_KEY is missing! Please configure it in your secrets.")
    st.stop()

# 5. Route views based on Mode
user_first_name = getattr(st.user, 'name', 'human').split()[0]

if st.session_state.app_mode == "Standard Chat":
    # --- STANDARD CHAT VIEW ---
    st.markdown(f'<p class="gemini-header">Hello, {user_first_name}</p>', unsafe_allow_html=True)
    st.markdown('<p class="gemini-subheader">How can I help you today?</p>', unsafe_allow_html=True)

    current_sid = st.session_state.current_session_id
    current_messages = st.session_state.sessions[current_sid]["messages"]

    for message in current_messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Enter a prompt here..."):
        if len(current_messages) == 0:
            st.session_state.sessions[current_sid]["title"] = prompt[:25]

        current_messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""
            
            try:
                client = genai.Client(api_key=api_key)
                chat_history_formatted = [
                    {"role": m["role"], "parts": [{"text": m["content"]}]} 
                    for m in current_messages
                ]
                
                response_stream = client.models.generate_content_stream(
                    model=selected_model,
                    contents=chat_history_formatted
                )
                
                for chunk in response_stream:
                    if chunk.text:
                        full_response += chunk.text
                        message_placeholder.markdown(full_response + "▌")
                
                message_placeholder.markdown(full_response)
                
            except errors.APIError as e:
                full_response = f"❌ **API Error:** {e}"
                message_placeholder.markdown(full_response)
            except Exception as e:
                full_response = f"❌ **Error:** {str(e)}"
                message_placeholder.markdown(full_response)

            current_messages.append({"role": "model", "content": full_response})

else:
    # --- LIVE SECTION VIEW (Gemini Live API) ---
    st.markdown('<p class="gemini-header"><span class="live-pulse"></span>Gemini Live Studio</p>', unsafe_allow_html=True)
    st.markdown('<p class="gemini-subheader">Real-time bidirectional multimodal audio-visual intelligence stream.</p>', unsafe_allow_html=True)

    if "live_messages" not in st.session_state:
        st.session_state.live_messages = []

    for msg in st.session_state.live_messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if live_prompt := st.chat_input("Send a real-time command to Live Stream..."):
        st.session_state.live_messages.append({"role": "user", "content": live_prompt})
        with st.chat_message("user"):
            st.markdown(live_prompt)

        with st.chat_message("assistant"):
            live_placeholder = st.empty()
            live_response = [""]  # Mutable list container to prevent scope errors
            
            async def run_live_session():
                client = genai.Client(api_key=api_key)
                live_model = "gemini-3.1-flash-live-preview"
                config = types.LiveConnectConfig(response_modalities=["TEXT"])
                
                async with client.aio.live.connect(model=live_model, config=config) as session:
                    await session.send(input=live_prompt, end_of_turn=True)
                    async for response in session.receive():
                        if response.server_content and response.server_content.model_turn:
                            for part in response.server_content.model_turn.parts:
                                if part.text:
                                    live_response[0] += part.text
                                    live_placeholder.markdown(live_response[0] + "▌")

            try:
                asyncio.run(run_live_session())
                live_placeholder.markdown(live_response[0])
            except Exception as ex:
                live_response[0] = f"❌ **Live Session Error:** {str(ex)}"
                live_placeholder.markdown(live_response[0])

            st.session_state.live_messages.append({"role": "model", "content": live_response[0]})
