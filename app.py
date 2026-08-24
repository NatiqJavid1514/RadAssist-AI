import streamlit as st
from google import genai
from PIL import Image
import os

st.set_page_config(page_title="RadAssist AI - Medical Screening Assistant", layout="centered")

st.title("🩺 RadAssist AI: Preliminary X-Ray Screener")
st.caption("AI-powered triage support for rural and under-resourced healthcare clinics.")

st.info("⚠️ **Responsible AI Disclaimer:** This tool provides preliminary observations for educational and triage assistance only. It is not an autonomous diagnostic device and does not replace evaluation by a licensed radiologist.")

# API Key input
api_key = st.text_input("Enter your Gemini API Key:", type="password")

# Provide sample image options or custom upload
st.subheader("Select or Upload an X-Ray Image")
input_option = st.radio("Choose image source:", [
    "Sample: Pneumonia Chest X-Ray", 
    "Sample: Normal Chest X-Ray", 
    "Upload My Own Image"
])

image = None

# Handle image selection based on exact filenames in your repo
if input_option == "Sample: Pneumonia Chest X-Ray":
    # Try both common spellings just in case
    sample_path = "pneumonia.jpeg" if os.path.exists("pneumonia.jpeg") else "pnemonia.jpeg"
    if os.path.exists(sample_path):
        image = Image.open(sample_path)
        st.image(image, caption="Sample Input: Pneumonia Scan", use_container_width=True)
    else:
        st.error("Pneumonia sample file not found in root directory.")

elif input_option == "Sample: Normal Chest X-Ray":
    # Checks for either file extension for your normal chest scan
    possible_names = [f for f in os.listdir('.') if f.startswith('Normal_posteroanterior')]
    if possible_names:
        sample_path = possible_names[0]
        image = Image.open(sample_path)
        st.image(image, caption="Sample Input: Normal Chest Scan", use_container_width=True)
    else:
        st.error("Normal chest sample file not found.")

else:
    uploaded_file = st.file_uploader("Upload an X-Ray Scan (PNG/JPG)", type=["png", "jpg", "jpeg"])
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded X-Ray Scan", use_container_width=True)

# Analysis Trigger
if image is not None:
    if st.button("Generate Preliminary Triage Report", type="primary"):
        if not api_key:
            st.error("Please enter a valid Gemini API Key to proceed.")
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
                    # Updated to gemini-3.6-flash model
                    response = client.models.generate_content(
                        model="gemini-3.6-flash",
                        contents=[image, prompt]
                    )
                
                st.markdown("---")
                st.markdown(response.text)
                
            except Exception as e:
                st.error(f"Error executing analysis: {e}")
