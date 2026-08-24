import streamlit as st
from google import genai
from PIL import Image

st.set_page_config(page_title="RadAssist AI - Medical Screening Assistant", layout="centered")

st.title("🩺 RadAssist AI: Preliminary X-Ray Screener")
st.caption("AI-powered triage support for rural and under-resourced healthcare clinics.")

st.info("⚠️ **Responsible AI Disclaimer:** This tool provides preliminary observations for educational and triage assistance only. It is not an autonomous diagnostic device and does not replace evaluation by a licensed radiologist.")

# API Key Input
api_key = st.text_input("Enter your Gemini API Key:", type="password")

# File Upload
uploaded_file = st.file_uploader("Upload an X-Ray Scan (PNG/JPG)", type=["png", "jpg", "jpeg"])

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded X-Ray Scan", use_container_width=True)
    
    if st.button("Generate Preliminary Triage Report", type="primary"):
        if not api_key:
            st.error("Please enter your Gemini API Key to proceed.")
        else:
            try:
                client = genai.Client(api_key=api_key)
                
                prompt = (
                    "Act as an educational medical AI assistant aiding a general practitioner in a rural clinic.\n"
                    "Analyze the provided X-ray image and generate a structured triage note with the following headers:\n\n"
                    "### 1. Image Overview\n"
                    "Identify the anatomical region and projection (e.g., Chest PA, Limb/Bone X-Ray).\n\n"
                    "### 2. Preliminary Visual Observations\n"
                    "Describe visible key structures, symmetry, density, and general clarity.\n\n"
                    "### 3. Potential Anomalies / Areas of Interest\n"
                    "Highlight any noticeable visual abnormalities, potential fractures, opacities, or clear signs of concern. If none are visible, state that the scan appears gross-unremarkable.\n\n"
                    "### 4. Triage & Follow-up Recommendation\n"
                    "Provide a suggested priority level (Low/Medium/High) for radiologist review and list recommended next clinical steps.\n\n"
                    "Maintain professional, cautious medical phrasing and include an explicit disclaimer at the end."
                )
                
                with st.spinner("Analyzing image features..."):
                    response = client.models.generate_content(
                        model="gemini-2.5-flash",
                        contents=[image, prompt]
                    )
                
                st.markdown("---")
                st.markdown(response.text)
                
            except Exception as e:
                st.error(f"Error executing analysis: {e}")