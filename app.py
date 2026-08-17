import os
import streamlit as st
from google import genai
from google.genai import types

# 1. Page Configuration
st.set_page_config(
    page_title="Metaverse AI - Ultimate Intelligence",
    page_icon="🌌",
    layout="wide"
)

# 2. Cyber Neon UI Theme (CSS)
st.markdown("""
    <style>
    /* Deep Space Cyber Background */
    .stApp {
        background: radial-gradient(circle at center, #070514, #120d2a, #030208);
        color: #e2e8f0;
    }
    
    /* Neon Header Glow */
    h1 {
        color: #00ffff !important;
        text-shadow: 0 0 10px rgba(0, 255, 255, 0.7), 0 0 20px rgba(0, 255, 255, 0.4);
        font-family: 'Courier New', monospace;
        letter-spacing: 2px;
    }
    
    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #05040a;
        border-right: 1px solid #00ffff;
        box-shadow: 5px 0 15px rgba(0, 255, 255, 0.15);
    }
    
    /* User Chat Bubble */
    .stChatMessage[data-testid="stChatMessage-user"] {
        background: rgba(0, 255, 255, 0.05);
        border: 1px solid #00ffff;
        border-radius: 12px;
        box-shadow: 0 0 10px rgba(0, 255, 255, 0.2);
    }
    
    /* Assistant Chat Bubble */
    .stChatMessage[data-testid="stChatMessage-assistant"] {
        background: rgba(255, 0, 127, 0.05);
        border: 1px solid #ff007f;
        border-radius: 12px;
        box-shadow: 0 0 10px rgba(255, 0, 127, 0.2);
    }
    
    /* Chat Input Field */
    .stChatInput input {
        background-color: #0b091a !important;
        color: #00ffff !important;
        border: 1px solid #00ffff !important;
        border-radius: 8px !important;
    }
    .stChatInput input:focus {
        box-shadow: 0 0 20px rgba(0, 255, 255, 0.6) !important;
    }
    
    /* Action Buttons */
    .stButton button {
        background: linear-gradient(45deg, #00ffff, #7928ca);
        color: #05040a;
        font-weight: bold;
        border: none;
        border-radius: 8px;
        box-shadow: 0 0 12px rgba(0, 255, 255, 0.5);
        transition: 0.3s ease;
    }
    .stButton button:hover {
        box-shadow: 0 0 22px rgba(255, 0, 127, 0.8);
        color: #ffffff;
    }
    </style>
""", unsafe_allow_html=True)

# 3. Sidebar Navigation
st.sidebar.title("🌌 Metaverse Controls")
app_mode = st.sidebar.radio("Select AI Module", [
    "🧠 Gemini Neural Core (Chat)", 
    "🎨 Holographic Image Synthesizer", 
    "👁️ Vision Analysis Matrix"
])
st.sidebar.markdown("---")
st.sidebar.markdown("✨ **Status:** Fully Synchronized")
st.sidebar.markdown("🚀 **Intelligence:** Gemini Flash Core")

# 4. API Key Configuration
API_KEY = os.getenv("GEMINI_API_KEY", "")

if API_KEY == "YOUR_ACTUAL_API_KEY":
    st.error("⚠️ Please insert your valid Google AI Studio API key into app.py to activate Metaverse AI.")
else:
    @st.cache_resource
    def get_genai_client(api_key):
        return genai.Client(api_key=api_key)

    client = get_genai_client(API_KEY)

    # --- MODULE 1: NEURAL CORE CHAT ---
    if app_mode == "🧠 Gemini Neural Core (Chat)":
        st.title("🧠 Metaverse: Neural Core")
        st.caption("Powered by deep contextual intelligence, multi-turn reasoning, and complex coding capability.")

        if "messages" not in st.session_state:
            st.session_state.messages = []

        if "chat_session" not in st.session_state:
            st.session_state.chat_session = client.chats.create(model="gemini-3.5-flash")

        # Display history
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        # Input handler
        if user_prompt := st.chat_input("Query the Neural Core..."):
            st.session_state.messages.append({"role": "user", "content": user_prompt})
            with st.chat_message("user"):
                st.markdown(user_prompt)

            with st.chat_message("assistant"):
                with st.spinner("Computing through neural pathways..."):
                    try:
                        response = st.session_state.chat_session.send_message(user_prompt)
                        bot_reply = response.text
                    except Exception:
                        st.session_state.chat_session = client.chats.create(model="gemini-3.5-flash")
                        response = st.session_state.chat_session.send_message(user_prompt)
                        bot_reply = response.text

                    st.markdown(bot_reply)
                    st.session_state.messages.append({"role": "assistant", "content": bot_reply})

    # --- MODULE 2: HOLOGRAPHIC IMAGE SYNTHESIZER ---
    elif app_mode == "🎨 Holographic Image Synthesizer":
        st.title("🎨 Metaverse: Image Synthesizer")
        st.caption("Generate high-definition digital imagery and neon artwork via advanced text prompts.")

        image_prompt = st.text_area("Hologram Prompt:", placeholder="e.g., A cybernetic samurai standing on a neon-lit Tokyo rooftop during a rainstorm, cinematic...")
        
        col1, col2 = st.columns([1, 4])
        with col1:
            gen_btn = st.button("Synthesize Hologram")

        if gen_btn and image_prompt:
            with st.spinner("Rendering pixels from the matrix..."):
                try:
                    result = client.models.generate_images(
                        model='imagen-3.0-generate-002',
                        prompt=image_prompt,
                        config=types.GenerateImagesConfig(
                            number_of_images=1,
                            output_mime_type="image/jpeg",
                            aspect_ratio="1:1",
                        )
                    )
                    for img in result.generated_images:
                        st.image(img.image.image_bytes, caption=f"Prompt: {image_prompt}", use_container_width=True)
                except Exception as e:
                    st.error(f"Image generation error: {e}")

    # --- MODULE 3: VISION ANALYSIS MATRIX ---
    elif app_mode == "👁️ Vision Analysis Matrix":
        st.title("👁️ Metaverse: Vision Matrix")
        st.caption("Upload images to let Gemini analyze, decode, and extract data from visual patterns.")

        uploaded_file = st.file_uploader("Upload an Image file", type=["jpg", "jpeg", "png"])
        vision_prompt = st.text_input("What would you like Gemini to analyze about this image?", "Describe this image in detail.")

        if uploaded_file is not None:
            st.image(uploaded_file, caption="Uploaded Specimen", width=400)
            if st.button("Analyze Specimen"):
                with st.spinner("Analyzing visual spectrum..."):
                    try:
                        # Read uploaded image bytes
                        image_bytes = uploaded_file.getvalue()
                        
                        response = client.models.generate_content(
                            model="gemini-3.5-flash",
                            contents=[
                                vision_prompt,
                                types.Part.from_bytes(
                                    data=image_bytes,
                                    mime_type=uploaded_file.type,
                                ),
                            ],
                        )
                        st.markdown("### Analysis Result:")
                        st.markdown(response.text)
                    except Exception as e:
                        st.error(f"Vision analysis error: {e}")
