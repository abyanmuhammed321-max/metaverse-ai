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
    .stApp {
        background: radial-gradient(circle at center, #0a0b10, #121420, #06070b);
        color: #e2e8f0;
    }
    h1 {
        color: #00f2fe !important;
        text-shadow: 0 0 12px rgba(0, 242, 254, 0.6);
        font-family: 'Inter', sans-serif;
    }
    section[data-testid="stSidebar"] {
        background-color: #0d0f17;
        border-right: 1px solid rgba(0, 242, 254, 0.2);
    }
    .stButton button {
        background: linear-gradient(135deg, #00f2fe 0%, #4facfe 100%);
        color: #0a0b10;
        font-weight: bold;
        border: none;
        border-radius: 8px;
        box-shadow: 0 0 10px rgba(0, 242, 254, 0.3);
    }
    </style>
""", unsafe_allow_html=True)

# 3. Google Sign-In Gate (with fallback safety if secrets aren't linked yet)
is_logged_in = True
user_name = "Matrix Creator"

try:
    is_logged_in = st.user.is_logged_in
    user_name = getattr(st.user, "name", "User")
except Exception:
    pass # Bypasses safely if [auth] secrets are not added yet

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
            st.error("Google OAuth is not configured in your Streamlit secrets block.")
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
            "chat_obj": client.chats.create(model="gemini-2.5-flash")
        }
        st.session_state.current_session_id = init_id

    # --- SIDEBAR ---
    st.sidebar.title("✨ Metaverse AI")
    st.sidebar.markdown(f"👤 **User:** {user_name}")
    
    try:
        if st.sidebar.button("🚪 Log out", use_container_width=True):
            st.logout()
    except Exception:
        pass

    st.sidebar.markdown("---")
    
    if st.sidebar.button("➕ New Chat", use_container_width=True):
        new_id = str(uuid.uuid4())
        st.session_state.sessions[new_id] = {
            "title": "New Chat",
            "messages": [],
            "chat_obj": client.chats.create(model="gemini-2.5-flash")
        }
        st.session_state.current_session_id = new_id
        st.rerun()

    st.sidebar.markdown("### 💬 Recent Chats")

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

    if sessions_to_delete:
        for s_id in sessions_to_delete:
            del st.session_state.sessions[s_id]
        if len(st.session_state.sessions) == 0:
            fallback_id = str(uuid.uuid4())
            st.session_state.sessions[fallback_id] = {
                "title": "New Chat",
                "messages": [],
                "chat_obj": client.chats.create(model="gemini-2.5-flash")
            }
            st.session_state.current_session_id = fallback_id
        else:
            st.session_state.current_session_id = list(st.session_state.sessions.keys())[0]
        st.rerun()

    st.sidebar.markdown("---")
    app_mode = st.sidebar.radio("Core Engine Mode", [
        "💬 Gemini Neural Chat", 
        "🍌 Nano Banana Art Studio", 
        "👁️ Vision Analyzer"
    ])

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
                        current_session["chat_obj"] = client.chats.create(model="gemini-2.5-flash")
                        response = current_session["chat_obj"].send_message(prompt)
                        reply = response.text

                    st.markdown(reply)
                    current_session["messages"].append({"role": "assistant", "content": reply})
            st.rerun()

    # --- MODE 2: NANO BANANA ART STUDIO ---
    elif app_mode == "🍌 Nano Banana Art Studio":
        st.title("🍌 Nano Banana: AI Art & Image Studio")
        st.caption("Powered by Gemini 2.5 Flash Image & Nano Banana Generation Core.")

        tab_type = st.radio("Select Operation", ["🎨 Text-to-Image Generation", "🔄 Image-to-Image / Conversational Edit"], horizontal=True)

        if tab_type == "🎨 Text-to-Image Generation":
            img_prompt = st.text_area("Describe your visual concept:", placeholder="e.g., A stylish 3D caricature of a cyberpunk tiger, expressive features, neon lighting...")
            aspect_ratio = st.selectbox("Aspect Ratio", ["1:1", "16:9", "4:3", "9:16"])
            
            if st.button("Generate Nano Banana Art", use_container_width=True):
                if img_prompt:
                    with st.spinner("Synthesizing pixels with Nano Banana engine..."):
                        try:
                            result = client.models.generate_images(
                                model='imagen-3.0-generate-002',
                                prompt=img_prompt,
                                config=types.GenerateImagesConfig(
                                    number_of_images=1,
                                    output_mime_type="image/jpeg",
                                    aspect_ratio=aspect_ratio,
                                )
                            )
                            for generated in result.generated_images:
                                st.image(generated.image.image_bytes, caption=img_prompt, use_container_width=True)
                        except Exception as e:
                            st.error(f"Generation error: {e}")
                else:
                    st.warning("Please enter a prompt description.")

        else: 
            uploaded_file = st.file_uploader("Upload reference image(s) [Up to 5]", type=["jpg", "jpeg", "png", "webp"], accept_multiple_files=True)
            edit_prompt = st.text_input("Describe how to transform or edit the image:", placeholder="e.g., Turn this into a hand-drawn cartoon anime style...")

            if uploaded_file:
                st.write(f"Loaded {len(uploaded_file)} reference specimen(s).")
                if st.button("Transform with Nano Banana", use_container_width=True):
                    with st.spinner("Processing multi-image context & style transfer..."):
                        try:
                            content_payload = [edit_prompt]
                            for f in uploaded_file:
                                content_payload.append(types.Part.from_bytes(data=f.getvalue(), mime_type=f.type))
                            
                            resp = client.models.generate_content(
                                model="gemini-2.5-flash",
                                contents=content_payload
                            )
                            st.markdown("### Nano Banana Studio Result:")
                            st.markdown(resp.text)
                        except Exception as e:
                            st.error(f"Editing error: {e}")

    # --- MODE 3: VISION ANALYZER ---
    elif app_mode == "👁️ Vision Analyzer":
        st.title("👁️ Vision Matrix")
        uploaded_image = st.file_uploader("Upload visual specimen", type=["jpg", "jpeg", "png"])
        v_prompt = st.text_input("Visual Query:", "Analyze this image and list key details.")
        if uploaded_image:
            st.image(uploaded_image, caption="Loaded Specimen", width=400)
            if st.button("Analyze Specimen", use_container_width=True):
                with st.spinner("Scanning visual patterns..."):
                    try:
                        resp = client.models.generate_content(
                            model="gemini-2.5-flash",
                            contents=[v_prompt, types.Part.from_bytes(data=uploaded_image.getvalue(), mime_type=uploaded_image.type)]
                        )
                        st.markdown("### Analysis Report:")
                        st.markdown(resp.text)
                    except Exception as e:
                        st.error(f"Vision error: {e}")
