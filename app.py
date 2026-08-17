import os
import uuid
import streamlit as st
from google import genai
from google.genai import types

# Optional import for OpenAI DALL-E
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

# 1. Page Configuration & Mobile Viewport Support
st.set_page_config(
    page_title="Metaverse AI - Gemini Edition",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="auto"
)

# 2. Neon Gemini UI Styling & Mobile Responsive CSS Injection
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
    
    /* --- MOBILE RESPONSIVE MEDIA QUERIES --- */
    @media screen and (max-width: 768px) {
        .main .block-container {
            padding: 1rem 0.75rem !important;
            max-width: 100% !important;
        }
        h1 {
            font-size: 1.6rem !important;
        }
        .stTextInput input, .stTextArea textarea, .stSelectbox {
            font-size: 16px !important; /* Prevents auto-zoom on iOS */
        }
        div[data-testid="stHorizontalBlock"] {
            flex-direction: column !important;
        }
        div[data-testid="column"] {
            width: 100% !important;
            flex: 1 1 100% !important;
            min-width: 100% !important;
        }
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
    pass 

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
    GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
except Exception:
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "YOUR_ACTUAL_GEMINI_API_KEY")

try:
    OPENAI_API_KEY = st.secrets.get("OPENAI_API_KEY", os.getenv("OPENAI_API_KEY", ""))
except Exception:
    OPENAI_API_KEY = ""

if not GEMINI_API_KEY or GEMINI_API_KEY == "YOUR_ACTUAL_GEMINI_API_KEY":
    st.error("⚠️ Please configure your GEMINI_API_KEY in Streamlit Secrets.")
    st.stop()
else:
    @st.cache_resource
    def get_gemini_client(api_key):
        return genai.Client(api_key=api_key)

    client = get_gemini_client(GEMINI_API_KEY)

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
        "🍌 Multi-AI Art Studio", 
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

    # --- MODE 2: MULTI-AI ART STUDIO (Nano Banana & ChatGPT DALL-E) ---
    elif app_mode == "🍌 Multi-AI Art Studio":
        st.title("🍌 Multi-AI Art Studio")
        st.caption("Generate stunning visuals using either Google Nano Banana or ChatGPT DALL-E 3.")

        art_engine = st.selectbox("Choose Image Engine", ["🍌 Nano Banana (Gemini)", "🤖 ChatGPT (DALL-E 3)"])

        if art_engine == "🍌 Nano Banana (Gemini)":
            tab_type = st.radio("Operation", ["🎨 Text-to-Image", "🔄 Image-to-Image Edit"], horizontal=True)

            if tab_type == "🎨 Text-to-Image":
                img_prompt = st.text_area("Describe your concept for Nano Banana:", placeholder="e.g., A futuristic cyberpunk street in Tokyo, neon lights...")
                if st.button("Generate with Nano Banana", use_container_width=True):
                    if img_prompt:
                        with st.spinner("Synthesizing pixels with Nano Banana..."):
                            try:
                                result = client.models.generate_content(
                                    model='gemini-2.5-flash-image',
                                    contents=img_prompt
                                )
                                rendered_image = False
                                if hasattr(result, 'candidates') and result.candidates:
                                    for part in result.candidates[0].content.parts:
                                        if hasattr(part, 'inline_data') and part.inline_data:
                                            st.image(part.inline_data.data, caption=img_prompt, use_container_width=True)
                                            rendered_image = True
                                if not rendered_image and hasattr(result, 'text'):
                                    st.markdown(result.text)
                            except Exception as e:
                                st.error(f"Generation error (Quota or Limit): {e}")
                    else:
                        st.warning("Please enter a prompt.")
            else:
                uploaded_file = st.file_uploader("Upload reference image", type=["jpg", "jpeg", "png", "webp"])
                edit_prompt = st.text_input("Describe style transformation:")
                if uploaded_file and st.button("Transform Image", use_container_width=True):
                    with st.spinner("Processing reference with Nano Banana..."):
                        try:
                            resp = client.models.generate_content(
                                model="gemini-2.5-flash-image",
                                contents=[edit_prompt, types.Part.from_bytes(data=uploaded_file.getvalue(), mime_type=uploaded_file.type)]
                            )
                            rendered_image = False
                            if hasattr(resp, 'candidates') and resp.candidates:
                                for part in resp.candidates[0].content.parts:
                                    if hasattr(part, 'inline_data') and part.inline_data:
                                        st.image(part.inline_data.data, caption=edit_prompt, use_container_width=True)
                                        rendered_image = True
                            if not rendered_image and hasattr(resp, 'text'):
                                st.markdown(resp.text)
                        except Exception as e:
                            st.error(f"Editing error: {e}")

        else: # ChatGPT DALL-E 3 Mode
            st.markdown("### 🤖 ChatGPT DALL-E 3 Studio")
            dall_e_prompt = st.text_area("Describe your artwork for ChatGPT DALL-E 3:", placeholder="e.g., An oil painting of a cosmic cat floating in a galaxy...")
            dall_e_quality = st.selectbox("Quality", ["standard", "hd"])
            dall_e_size = st.selectbox("Image Size", ["1024x1024", "1024x1792", "1792x1024"])

            if st.button("🎨 Generate with ChatGPT DALL-E 3", use_container_width=True):
                if not OPENAI_API_KEY:
                    st.error("⚠️ Please configure your `OPENAI_API_KEY` in Streamlit Secrets to use DALL-E 3.")
                elif not OPENAI_AVAILABLE:
                    st.error("⚠️ The `openai` library is missing from `requirements.txt`.")
                elif dall_e_prompt:
                    with st.spinner("Painting artwork with ChatGPT DALL-E 3..."):
                        try:
                            openai_client = OpenAI(api_key=OPENAI_API_KEY)
                            response = openai_client.images.generate(
                                model="dall-e-3",
                                prompt=dall_e_prompt,
                                size=dall_e_size,
                                quality=dall_e_quality,
                                n=1,
                            )
                            image_url = response.data[0].url
                            st.image(image_url, caption=dall_e_prompt, use_container_width=True)
                        except Exception as e:
                            st.error(f"ChatGPT DALL-E Error: {e}")
                else:
                    st.warning("Please enter a prompt description.")

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
