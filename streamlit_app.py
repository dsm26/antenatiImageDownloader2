import streamlit as st
from google import genai
from PIL import Image
import io

# --- INITIALIZATION ---
if "history" not in st.session_state:
    st.session_state.history = []

# --- SIDEBAR UI (All settings moved here) ---
with st.sidebar:
    st.title("Settings & Info")
    api_key = st.text_input("Gemini API Key", type="password")

    # Fixed Model List: No 1.5, includes Accuracy, Stability, and Lite options
    model_options = {
        "Gemini 2.5 Flash (Best Accuracy)": "gemini-2.5-flash",
        "Gemini 3.1 Flash-Lite (Highest Limits)": "gemini-3.1-flash-lite-preview",
        "Gemini 2.5 Flash-Lite (Very Fast)": "gemini-2.5-flash-lite",
        "Gemini 2.0 Flash (Stable)": "gemini-2.0-flash"
    }

    selected_display_name = st.selectbox("Gemini Model", list(model_options.keys()), index=0)
    selected_model_id = model_options[selected_display_name]

    st.markdown("---")
    st.markdown("""
    **CSV Log Guide (10 Fields):**
    1. Image ID
    2. Record Type
    3. Subject Name
    4. Date
    5. Father's Name
    6. Mother's Name
    7. Town/Locality
    8. Job/Occupation
    9. Notes
    10. Source URL
    """)

# --- MAIN UI ---
st.title("Antenati Downloader & AI Translator")
st.markdown("Enter an **Image ID** or a full **Antenati URL** to begin.")

input_val = st.text_input("Antenati URL or Image ID", placeholder="https://antenati.cultura.gov.it/detail-view/?id=...")

# --- LOGIC FUNCTIONS ---

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
        return "Missing API Key in Sidebar"
    try:
        client = genai.Client(api_key=api_key)
        img = Image.open(io.BytesIO(image_bytes))
        prompt = "Analyze this record. Summary first, then RAW_DATA: {json with 8 keys: type, subject, date, father, mother, town, job, notes}"
        
        response = client.models.generate_content(model=selected_model_id, contents=[prompt, img])
        return response.text if response.text else "Empty response from AI."
    except Exception as e:
        if "429" in str(e):
            return f"⚠️ Limit Reached. Switch to a 'Lite' model in the sidebar."
        return f"AI Error: {str(e)}"

# --- EXECUTION ---
if input_val:
    # (Rest of your stitching and display logic goes here)
    pass

st.divider()
st.caption("Note: AI translations are probabilistic. Always verify with the original image.")
