import streamlit as st
import os
import uuid
from io import BytesIO
from google import genai
from google.genai import types
from PIL import Image

# Page configuration
st.set_page_config(
    page_title="Metaverse AI - Gemini Edition",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="auto"
)

# UI Styling
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
    @media screen and (max-width: 768px) {
        .main .block-container {
            padding: 1rem 0.75rem !important;
            max-width: 100% !important;
        }
        h1 {
            font-size: 1.6rem !important;
        }
    }
    </style>
""", unsafe_allow_html=True)

# API Key Configuration
api_key = ""
try:
    api_key = st.secrets["GEMINI_API_KEY"]
except Exception:
    api_key = os.getenv("GEMINI_API_KEY", "")

if not api_key:
    with st.sidebar:
        st.subheader("🔑 Authentication Required")
        api_key = st.text_input("Enter your Gemini API Key", type="password")
        if api_key:
            os.environ["GEMINI_API_KEY"] = api_key

try:
    client = genai.Client(api_key=api_key) if api_key else genai.Client()
except Exception as e:
    st.error(f"Failed to initialize Gemini Client: {e}")
    client = None

# Initialize session state for multi-chat support
if "sessions" not in st.session_state:
    st.session_state.sessions = {
        "Default Chat": {
            "title": "Default Chat",
            "messages": []
        }
    }

if "active_session" not in st.session_state or st.session_state.active_session not in st.session_state.sessions:
    st.session_state.active_session = list(st.session_state.sessions.keys())[0]

# Sidebar Navigation & Features
with st.sidebar:
    st.title("✨ Metaverse AI")
    st.markdown("---")
    
    if st.button("➕ New Chat", use_container_width=True):
        new_title = f"Chat {len(st.session_state.sessions) + 1}"
        st.session_state.sessions[new_title] = {"title": new_title, "messages": []}
        st.session_state.active_session = new_title
        st.rerun()
        
    st.subheader("💬 Conversations")
    session_keys = list(st.session_state.sessions.keys())
    if st.session_state.active_session not in session_keys:
        st.session_state.active_session = session_keys[0]
        
    safe_index = session_keys.index(st.session_state.active_session)
    selected_chat = st.radio(
        "Select Chat",
        session_keys,
        index=safe_index,
        label_visibility="collapsed"
    )
    
    if selected_chat != st.session_state.active_session:
        st.session_state.active_session = selected_chat
        st.rerun()

    st.markdown("---")
    app_mode = st.sidebar.radio("Core Engine Mode", [
        "💬 Gemini Neural Chat", 
        "🍌 Nano Banana Art Studio", 
        "👁️ Vision Analyzer"
    ])

# Main application routing based on selected mode
if not api_key:
    st.error("⚠️ Please provide your `GEMINI_API_KEY` in Streamlit Secrets or via the sidebar.")
    st.stop()

# --- MODE 1: GEMINI NEURAL CHAT ---
if app_mode == "💬 Gemini Neural Chat":
    current_session = st.session_state.sessions[st.session_state.active_session]
    st.title(f"✨ Metaverse AI: Gemini Core")
    st.caption(f"Active Session: {current_session['title']}")

    for msg in current_session["messages"]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if prompt := st.chat_input("Ask your neon AI anything..."):
        current_session["messages"].append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        if current_session["title"] == "Default Chat" or current_session["title"].startswith("Chat "):
            current_session["title"] = prompt[:22] + ("..." if len(prompt) > 22 else "")

        with st.chat_message("assistant"):
            with st.spinner("Thinking through neural pathways..."):
                try:
                    formatted_contents = []
                    for m in current_session["messages"]:
                        role = "user" if m["role"] == "user" else "model"
                        formatted_contents.append({
                            "role": role,
                            "parts": [{"text": m["content"]}]
                        })

                    response = client.models.generate_content(
                        model="gemini-2.5-flash",
                        contents=formatted_contents
                    )
                    reply = response.text if hasattr(response, 'text') and response.text else "No response generated."
                    st.markdown(reply)
                    current_session["messages"].append({"role": "assistant", "content": reply})
                except Exception as e:
                    st.error(f"⚠️ API Error: {e}")
        st.rerun()

# --- MODE 2: NANO BANANA ART STUDIO ---
elif app_mode == "🍌 Nano Banana Art Studio":
    st.title("🍌 Nano Banana Art Studio")
    st.caption("Generate stunning visuals and edit assets using Gemini's native media engine.")

    tab_type = st.radio("Operation", ["🎨 Text-to-Image", "🔄 Image-to-Image Edit"], horizontal=True)

    if tab_type == "🎨 Text-to-Image":
        img_prompt = st.text_area("Describe your concept for Nano Banana:", placeholder="e.g., A futuristic cyberpunk street in Tokyo, neon lights...")
        if st.button("Generate with Nano Banana", use_container_width=True):
            if img_prompt:
                with st.spinner("Synthesizing pixels with Nano Banana..."):
                    try:
                        result = client.models.generate_content(
                            model='gemini-3.1-flash-image',
                            contents=img_prompt,
                            config=types.GenerateContentConfig(
                                response_modalities=["TEXT", "IMAGE"]
                            )
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
                        st.error(f"Generation error: {e}")
            else:
                st.warning("Please enter a prompt.")
    else:
        uploaded_file = st.file_uploader("Upload reference image", type=["jpg", "jpeg", "png", "webp"])
        edit_prompt = st.text_input("Describe style transformation:")
        if uploaded_file and st.button("Transform Image", use_container_width=True):
            with st.spinner("Processing reference with Nano Banana..."):
                try:
                    resp = client.models.generate_content(
                        model="gemini-3.1-flash-image",
                        contents=[edit_prompt, types.Part.from_bytes(data=uploaded_file.getvalue(), mime_type=uploaded_file.type)],
                        config=types.GenerateContentConfig(
                            response_modalities=["TEXT", "IMAGE"]
                        )
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

# --- MODE 3: VISION ANALYZER ---
elif app_mode == "👁️ Vision Analyzer":
    st.title("👁️ Vision Matrix")
    st.caption("Upload visual specimens for deep multi-modal analysis.")
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
