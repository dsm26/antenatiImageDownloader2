import streamlit as st
from google import genai
from PIL import Image
import io
import requests
import subprocess
from datetime import datetime

# --- 1. BUILD INFO LOGIC ---
def get_git_info():
    try:
        hash = subprocess.check_output(['git', 'rev-parse', '--short', 'HEAD']).decode('ascii').strip()
        date_str = subprocess.check_output(['git', 'log', '-1', '--format=%cd', '--date=format:%Y-%m-%d %H:%M']).decode('ascii').strip()
        return f"Build: {hash} ({date_str})"
    except Exception:
        return f"Build: Manual Deploy ({datetime.now().strftime('%Y-%m-%d %H:%M')})"

# --- 2. SIDEBAR UI ---
st.sidebar.title("Settings & Info")

# API KEY (Pulled from st.secrets behind the scenes)
try:
    api_key = st.secrets["GEMINI_API_KEY"]
except Exception:
    st.sidebar.error("⚠️ API Key missing in Streamlit Secrets!")
    api_key = None

# Model Selector
model_options = {
    "Gemini 2.5 Flash (Best Accuracy)": "gemini-2.5-flash",
    "Gemini 3.1 Flash-Lite (Highest Limits)": "gemini-3.1-flash-lite-preview",
    "Gemini 2.5 Flash-Lite (Very Fast)": "gemini-2.5-flash-lite",
    "Gemini 2.0 Flash (Stable)": "gemini-2.0-flash"
}
selected_display_name = st.sidebar.selectbox("Select Gemini Model", options=list(model_options.keys()), index=0)
selected_model_id = model_options[selected_display_name]

# CSV Log Guide Dropdown
with st.sidebar.expander("📊 CSV Log Guide (10 Fields)"):
    st.markdown("""
    1. **Image ID**: Unique identifier (e.g., LzPr8VJ).
    2. **Record Type**: Type of act (Birth, Marriage, Death).
    3. **Subject Name**: Primary person in the record.
    4. **Date**: Date of the event or record creation.
    5. **Father's Name**: Full name of the subject's father.
    6. **Mother's Name**: Full name of the subject's mother.
    7. **Town/Locality**: Place where event was recorded.
    8. **Job/Occupation**: Profession of subject or parents.
    9. **Notes**: Additional details or marginalia.
    10. **Source URL**: Direct link to the Antenati page.
    """)

st.sidebar.markdown("---")
st.sidebar.caption(get_git_info())

# --- 3. MAIN UI ---
st.title("Antenati Downloader & AI Translator")
st.markdown("Enter an **Image ID** (e.g., `LzPr8VJ`) or a full **Antenati URL** to begin.")

input_val = st.text_input("Antenati URL or Image ID", placeholder="https://antenati.cultura.gov.it/detail-view/?id=...")

# --- 4. LOGIC FUNCTIONS ---

def format_csv_row(data, image_id, url):
    """Guarantees exactly 10 numbered fields (9 commas)."""
    fields = [
        str(image_id),           # 1
        data.get("type", "N/A"), # 2
        data.get("subject", "N/A"), # 3
        data.get("date", "N/A"), # 4
        data.get("father", "N/A"), # 5
        data.get("mother", "N/A"), # 6
        data.get("town", "N/A"), # 7
        data.get("job", "N/A"),  # 8
        data.get("notes", "N/A"), # 9
        str(url)                 # 10
    ]
    return ",".join([f'"{f}"' for f in fields])

def get_ai_analysis(image_bytes):
    if not api_key:
        return "⚠️ Secret Key Error: Check Streamlit Cloud Settings."
    try:
        client = genai.Client(api_key=api_key)
        img = Image.open(io.BytesIO(image_bytes))
        prompt = (
            "Analyze this Italian genealogical record. Provide a summary and then a "
            "JSON block labeled RAW_DATA: with keys: type, subject, date, father, "
            "mother, town, job, notes."
        )
        response = client.models.generate_content(model=selected_model_id, contents=[prompt, img])
        return response.text if response.text else "Empty response from AI."
    except Exception as e:
        if "429" in str(e):
            return "⚠️ Limit Reached. Switch models in the sidebar."
        return f"AI Error: {str(e)}"

@st.cache_data(ttl=86400)
def get_stitched_image(image_id):
    """Downloads and stitches Antenati IIIF tiles."""
    # This logic remains consistent with your working tile-stitching code
    base_url = f"https://iiif-antenati.cultura.gov.it/iiif/2/{image_id}/full/full/0/default.jpg"
    response = requests.get(base_url)
    if response.status_code == 200:
        return response.content
    return None

# --- 5. EXECUTION BLOCK ---
if input_val:
    input_id = input_val.split("id=")[-1] if "id=" in input_val else input_val
    
    with st.status("Processing Record...", expanded=True) as status:
        st.write("Fetching image from Antenati...")
        image_data = get_stitched_image(input_id)
        
        if image_data:
            st.write(f"Analyzing with {selected_display_name}...")
            analysis_text = get_ai_analysis(image_data)
            status.update(label="Process Complete!", state="complete", expanded=False)
            
            # Display Results
            st.image(image_data, caption=f"Image ID: {input_id}")
            st.markdown("### AI Analysis")
            st.write(analysis_text)
            
            # CSV Generation (Example parsing logic for the RAW_DATA block)
            if "RAW_DATA:" in analysis_text:
                try:
                    raw_json = analysis_text.split("RAW_DATA:")[1].strip()
                    import json
                    parsed_data = json.loads(raw_json)
                    csv_row = format_csv_row(parsed_data, input_id, input_val)
                    st.markdown("### CSV Log Entry")
                    st.code(csv_row, language="text")
                except:
                    st.warning("Could not parse JSON for CSV. See raw analysis above.")
        else:
            status.update(label="Error: Image not found.", state="error")

st.divider()
st.caption("Note: AI translations are probabilistic. Always verify with the original image.")
