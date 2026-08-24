import streamlit as st
from google import genai
from PIL import Image
import os

# Page configuration
st.set_page_config(
    page_title="RadAssist AI | Clinical Triage",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for polished UI styling
st.markdown("""
<style>
    /* Dark theme medical palette */
    .main {
        background-color: #0E1117;
    }
    
    /* Header card styling */
    .header-card {
        background: linear-gradient(135deg, #1E293B 0%, #0F172A 100%);
        padding: 24px;
        border-radius: 12px;
        border: 1px solid #334155;
        margin-bottom: 20px;
    }
    .header-title {
        color: #38BDF8;
        font-size: 2.2rem;
        font-weight: 700;
        margin: 0;
    }
    .header-sub {
        color: #94A3B8;
        font-size: 1.05rem;
        margin-top: 6px;
    }

    /* Disclaimer box styling */
    .disclaimer-box {
        background-color: #1E1B4B;
        border-left: 5px solid #6366F1;
        padding: 14px 18px;
        border-radius: 8px;
        color: #E0E7FF;
        font-size: 0.9rem;
        margin-bottom: 25px;
    }

    /* Output card styling */
    .report-card {
        background-color: #1E293B;
        padding: 24px;
        border-radius: 12px;
        border: 1px solid #334155;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
    }
</style>
""", unsafe_allow_html=True)

# App Header
st.markdown("""
<div class="header-card">
    <div class="header-title">🩺 RadAssist AI</div>
    <div class="header-sub">Clinical Decision Support & Preliminary X-Ray Triage for Remote Health Settings</div>
</div>
""", unsafe_allow_html=True)

# Responsible AI Banner
st.markdown("""
<div class="disclaimer-box">
    <strong>⚠️ Responsible AI Disclaimer:</strong> This tool provides preliminary visual triage notes for educational and decision-support purposes only. It is not an autonomous diagnostic device and does not replace evaluation by a certified radiologist.
</div>
""", unsafe_allow_html=True)

# Sidebar Configuration
with st.sidebar:
    st.header("⚙️ Settings")
    api_key = st.text_input("Gemini API Key:", type="password", help="Enter your Gemini API key from AI Studio")
    
    st.markdown("---")
    st.subheader("📊 System Specs")
    st.write("**Model:** `gemini-3.6-flash`")
    st.write("**Vision Processing:** Active")
    st.write("**Interface:** Streamlit v1.x")

# Main Content Grid (2 Columns)
col_input, col_output = st.columns([1, 1], gap="large")

with col_input:
    st.subheader("1. Input Medical Image")
    
    input_option = st.radio(
        "Select Scan Source:", 
        ["Sample: Pneumonia Chest X-Ray", "Sample: Normal Chest X-Ray", "Upload Custom Image"],
        horizontal=False
    )

    image = None

    if input_option == "Sample: Pneumonia Chest X-Ray":
        sample_path = "pneumonia.jpeg" if os.path.exists("pneumonia.jpeg") else "pnemonia.jpeg"
        if os.path.exists(sample_path):
            image = Image.open(sample_path)
            st.image(image, caption="Loaded: Abnormal Chest Scan (Pneumonia)", use_container_width=True)
        else:
            st.error("Pneumonia sample file not found in root directory.")

    elif input_option == "Sample: Normal Chest X-Ray":
        possible_names = [f for f in os.listdir('.') if f.startswith('Normal_posteroanterior')]
        if possible_names:
            sample_path = possible_names[0]
            image = Image.open(sample_path)
            st.image(image, caption="Loaded: Unremarkable Chest Scan (Normal)", use_container_width=True)
        else:
            st.error("Normal chest sample file not found.")

    else:
        uploaded_file = st.file_uploader("Upload Image File", type=["png", "jpg", "jpeg"])
        if uploaded_file is not None:
            image = Image.open(uploaded_file)
            st.image(image, caption="Uploaded Medical Scan", use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)
    analyze_button = st.button("🚀 Analyze Scan & Generate Report", type="primary", use_container_width=True)

with col_output:
    st.subheader("2. Triage Output & Findings")
    
    if analyze_button:
        if not image:
            st.warning("Please select or upload an image first.")
        elif not api_key:
            st.error("Please enter your Gemini API Key in the sidebar.")
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
                
                with st.spinner("⚡ Running vision model inference..."):
                    response = client.models.generate_content(
                        model="gemini-3.6-flash",
                        contents=[image, prompt]
                    )
                
                # Render results in styled card
                st.markdown(f'<div class="report-card">{response.text}</div>', unsafe_allow_html=True)
                
            except Exception as e:
                st.error(f"Error executing analysis: {e}")
    else:
        st.info("👈 Select an X-ray image on the left and click 'Analyze Scan' to view clinical findings.")
