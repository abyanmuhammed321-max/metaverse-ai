import os
import uuid
import streamlit as st
from google import genai
from google.genai import types

# 1. Page Configuration
st.set_page_config(
    page_title="Metaverse AI - Gemini Edition",
    page_icon="✨",
    layout="wide"
)

# 2. Neon Gemini UI Styling (CSS)
st.markdown("""
    <style>
    /* Deep Cyber Dark Background */
    .stApp {
        background: radial-gradient(circle at center, #0a0b10, #121420, #06070b);
        color: #e2e8f0;
    }
    
    /* Neon Header Glow */
    h1 {
        color: #00f2fe !important;
        text-shadow: 0 0 12px rgba(0, 242, 254, 0.6);
        font-family: 'Inter', sans-serif;
    }
    
    /* Sidebar Gemini Aesthetic */
    section[data-testid="stSidebar"] {
        background-color: #0d0f17;
        border-right: 1px solid rgba(0, 242, 254, 0.2);
    }
    
    /* User Chat Bubble */
    .stChatMessage[data-testid="stChatMessage-user"] {
        background: rgba(14, 165, 233, 0.08);
        border: 1px solid #00f2fe;
        border-radius: 12px;
        box-shadow: 0 0 10px rgba(0, 242, 254, 0.15);
    }
    
    /* Assistant Chat Bubble */
    .stChatMessage[data-testid="stChatMessage-assistant"] {
        background: rgba(139, 92, 246, 0.08);
        border: 1px solid #a855f7;
        border-radius: 12px;
        box-shadow: 0 0 10px rgba(168, 85, 247, 0.15);
    }
    
    /* Chat Input Bar */
    .stChatInput input {
        background-color: #121420 !important;
        color: #ffffff !important;
        border: 1px solid #00f2fe !important;
        border-radius: 8px !important;
    }
    .stChatInput input:focus {
        box-shadow: 0 0 15px rgba(0, 242, 254, 0.4) !important;
    }
    
    /* Custom Neon Buttons */
    .stButton button {
        background: linear-gradient(135deg, #00f2fe 0%, #4facfe 100%);
        color: #0a0b10;
        font-weight: bold;
        border: none;
        border-radius: 8px;
        box-shadow: 0 0 10px rgba(0, 242, 254, 0.3);
        transition: 0.3s ease;
    }
    .stButton button:hover {
        box-shadow: 0 0 20px rgba(0, 242, 254, 0.8);
    }
    </style>
""", unsafe_allow_html=True)

# 3. Google Sign-In Gate (With fallback protection if secrets aren't set up yet)
is_logged_in = False
user_name = "Creator"

try:
    is_logged_in = st.user.is_logged_in
    user_name = getattr(st.user, "name", "User")
except Exception:
    # Authentication secrets are not configured yet; allow app to run safely
    is_logged_in = True 

if not is_logged_in:
    st.markdown("<br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.title("✨ Welcome to Metaverse AI")
        st.markdown("Sign in securely with your Google account to access your personal AI matrix.")
        try:
            if st.button("🔐 Log in with Google", use_container_width=True):
                st.login()
        except Exception:
            st.error("Google OAuth is not configured in your Streamlit secrets.")
    st.stop()

# 4. Secure API Key Configuration
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
except Exception:
    API_KEY = os.getenv("GEMINI_API_KEY", "YOUR_ACTUAL_API_KEY")

if not API_KEY or API_KEY == "YOUR_ACTUAL_API_KEY":
    st.error("⚠️ Please configure your GEMINI_API_KEY in Streamlit Secrets.")
    st.stop()
else:
    @st.cache_resource
    def get_client(api_key):
        return genai.Client(api_key=api_key)

    client = get_client(API_KEY)

    # 5. Multi-Chat Session Storage Initialization
    if "sessions" not in st.session_state:
        st.session_state.sessions = {}
    if "current_session_id" not in st.session_state:
        init_id = str(uuid.uuid4())
        st.session_state.sessions[init_id] = {
            "title": "New Chat",
            "messages": [],
            "chat_obj": client.chats.create(model="gemini-3.5-flash")
        }
        st.session_state.current_session_id = init_id

    # --- SIDEBAR NAVIGATION & USER INFO ---
    st.sidebar.title("✨ Metaverse AI")
    st.sidebar.markdown(f"👤 **User:** {user_name}")
    
    try:
        if st.sidebar.button("🚪 Log out", use_container_width=True):
            st.logout()
    except Exception:
        pass

    st.sidebar.markdown("---")
    
    # New Chat Button
    if st.sidebar.button("➕ New Chat", use_container_width=True):
        new_id = str(uuid.uuid4())
        st.session_state.sessions[new_id] = {
            "title": "New Chat",
            "messages": [],
            "chat_obj": client.chats.create(model="gemini-3.5-flash")
        }
        st.session_state.current_session_id = new_id
        st.rerun()

    st.sidebar.markdown("### 💬 Recent Chats")

    # Render previous chat history list & Delete options
    sessions_to_delete = []
    for s_id, s_data in list(st.session_state.sessions.items()):
        col_chat, col_del = st.sidebar.columns([4, 1])
        
        label = f"💬 {s_data['title']}"
        if s_id == st.session_state.current_session_id:
            label = f"👉 {s_data['title']}"
        
        with col_chat:
            if st.button(label, key=f"select_{s_id}", use_container_width=True):
                st.session_state.current_session_id = s_id
                st.rerun()
        
        with col_del:
            if st.button("🗑️", key=f"del_{s_id}", use_container_width=True):
                sessions_to_delete.append(s_id)

    # Handle chat deletions safely
    if sessions_to_delete:
        for s_id in sessions_to_delete:
            del st.session_state.sessions[s_id]
        
        if len(st.session_state.sessions) == 0:
            fallback_id = str(uuid.uuid4())
            st.session_state.sessions[fallback_id] = {
                "title": "New Chat",
                "messages": [],
                "chat_obj": client.chats.create(model="gemini-3.5-flash")
            }
            st.session_state.current_session_id = fallback_id
        else:
            st.session_state.current_session_id = list(st.session_state.sessions.keys())[0]
        st.rerun()

    st.sidebar.markdown("---")
    app_mode = st.sidebar.radio("Core Engine Mode", ["💬 Gemini Neural Chat", "🎨 Imagen Art Studio", "👁️ Vision Analyzer"])
    st.sidebar.markdown("🚀 **Engine:** Gemini 3.5 & Imagen 3")

    # Get active session data
    curr_id = st.session_state.current_session_id
    if curr_id not in st.session_state.sessions:
        curr_id = list(st.session_state.sessions.keys())[0]
        st.session_state.current_session_id = curr_id

    current_session = st.session_state.sessions[curr_id]

    # --- MODE 1: GEMINI NEURAL CHAT ---
    if app_mode == "💬 Gemini Neural Chat":
        st.title("✨ Metaverse AI: Gemini Core")
        st.caption(f"Active Session: {current_session['title']}")

        for msg in current_session["messages"]:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        if prompt := st.chat_input("Ask your neon AI anything..."):
            current_session["messages"].append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            if current_session["title"] == "New Chat":
                current_session["title"] = prompt[:22] + ("..." if len(prompt) > 22 else "")

            with st.chat_message("assistant"):
                with st.spinner("Thinking through neural pathways..."):
                    try:
                        response = current_session["chat_obj"].send_message(prompt)
                        reply = response.text
                    except Exception:
                        current_session["chat_obj"] = client.chats.create(model="gemini-3.5-flash")
                        response = current_session["chat_obj"].send_message(prompt)
                        reply = response.text

                    st.markdown(reply)
                    current_session["messages"].append({"role": "assistant", "content": reply})
            st.rerun()

    # --- MODE 2: IMAGEN ART STUDIO ---
    elif app_mode == "🎨 Imagen Art Studio":
        st.title("🎨 Metaverse AI: Imagen Studio")
        st.caption("Synthesize stunning high-definition visual imagery from descriptive text prompts.")

        img_prompt = st.text_area("Describe your image concept:", placeholder="e.g., A cyberpunk glowing neon tiger walking through a digital grid city...")
        if st.button("Generate Hologram Artwork", use_container_width=True):
            if img_prompt:
                with st.spinner("Rendering pixels with Imagen..."):
                    try:
                        result = client.models.generate_images(
                            model='imagen-3.0-generate-002',
                            prompt=img_prompt,
                            config=types.GenerateImagesConfig(
                                number_of_images=1,
                                output_mime_type="image/jpeg",
                                aspect_ratio="1:1",
                            )
                        )
                        for generated in result.generated_images:
                            st.image(generated.image.image_bytes, caption=img_prompt, use_container_width=True)
                    except Exception as e:
                        st.error(f"Image generation error: {e}")

    # --- MODE 3: VISION ANALYZER ---
    elif app_mode == "👁️ Vision Analyzer":
        st.title("👁️ Metaverse AI: Vision Matrix")
        st.caption("Upload images to analyze spatial data, objects, and text.")

        uploaded_image = st.file_uploader("Upload visual specimen", type=["jpg", "jpeg", "png"])
        v_prompt = st.text_input("Visual Query:", "Analyze this image and list key details.")

        if uploaded_image:
            st.image(uploaded_image, caption="Loaded Specimen", width=400)
            if st.button("Analyze Specimen", use_container_width=True):
                with st.spinner("Scanning visual patterns..."):
                    try:
                        resp = client.models.generate_content(
                            model="gemini-3.5-flash",
                            contents=[
                                v_prompt,
                                types.Part.from_bytes(data=uploaded_image.getvalue(), mime_type=uploaded_image.type)
                            ]
                        )
                        st.markdown("### Analysis Report:")
                        st.markdown(resp.text)
                    except Exception as e:
                        st.error(f"Vision error: {e}")
