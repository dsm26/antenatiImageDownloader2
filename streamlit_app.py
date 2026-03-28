import streamlit as st
import math
import requests
import re
import json
from io import BytesIO
from PIL import Image
import google.generativeai as genai

# --- CONFIGURATION ---
CHOSEN_MODEL = 'gemini-2.5-flash' 
CACHE_TTL = 900 
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Referer": "https://antenati.cultura.gov.it/",
}

st.set_page_config(page_title="Antenati Downloader & AI Translator", page_icon="🧬", layout="wide")

if "history" not in st.session_state:
    st.session_state.history = []

# --- ROBUST METADATA EXTRACTION ---
@st.cache_data(show_spinner=False, ttl=CACHE_TTL)
def get_antenati_metadata(input_str):
    image_id = input_str.strip().split('/')[-1] if "/" in input_str else input_str.strip()
    
    # Strategy 1: IIIF Manifest
    try:
        manifest_url = f"https://antenati.cultura.gov.it/iiif/2/{image_id}/manifest"
        resp = requests.get(manifest_url, headers=HEADERS, timeout=5)
        if resp.status_code == 200:
            label = resp.json().get("label", "")
            if label: return f"{label}"
    except:
        pass

    # Strategy 2: Page Scraping (Requires Full URL)
    if "antenati.cultura.gov.it" in input_str:
        try:
            resp = requests.get(input_str, headers=HEADERS, timeout=5)
            if resp.status_code == 200:
                title_match = re.search(r'<title>(.*?)</title>', resp.text)
                if title_match:
                    clean_title = title_match.group(1).replace(" - Antenati", "").strip()
                    if clean_title and "Antenati" not in clean_title:
                        return f"{clean_title}"
        except:
            pass

    # Strategy 3: ID Breakdown
    folder_match = re.search(r'an_ua\d+', input_str)
    if folder_match:
        return f"Italian Record (Unit: {folder_match.group(0)}, ID: {image_id})"

    return f"Italian Civil Record (ID: {image_id})"

# --- DOWNLOAD & STITCHING ---
@st.cache_data(show_spinner=False, ttl=CACHE_TTL)
def get_stitched_image(image_id):
    base_url = f"https://iiif-antenati.cultura.gov.it/iiif/2/{image_id}"
    info_resp = requests.get(f"{base_url}/info.json", headers=HEADERS)
    info_resp.raise_for_status()
    info = info_resp.json()
    
    w, h = info["width"], info["height"]
    tw, th = info["tiles"][0]["width"], info.get("tiles")[0].get("height", info["tiles"][0]["width"])
    
    final_img = Image.new("RGB", (w, h))
    cols, rows = math.ceil(w / tw), math.ceil(h / th)
    total_tiles = rows * cols
    
    progress_placeholder = st.empty()
    tile_count = 0
    for r in range(rows):
        for c in range(cols):
            tile_count += 1
            x, y = c * tw, r * th
            tile_w, tile_h = min(tw, w - x), min(th, h - y)
            tile_url = f"{base_url}/{x},{y},{tile_w},{tile_h}/full/0/default.jpg"
            progress_placeholder.progress(tile_count / total_tiles, text=f"📥 Downloading tile {tile_count} of {total_tiles}...")
            res = requests.get(tile_url, headers=HEADERS)
            tile_data = Image.open(BytesIO(res.content))
            final_img.paste(tile_data, (x, y))
    
    progress_placeholder.empty()
    buf = BytesIO()
    final_img.save(buf, format="JPEG", quality=95)
    return buf.getvalue()

# --- AI ANALYSIS ---
@st.cache_data(show_spinner=False, ttl=CACHE_TTL)
def get_ai_analysis(img_bytes, metadata_context, _model_instance):
    prompt = f"""
    ARCHIVAL CONTEXT: {metadata_context}
    
    TASK: Analyze this 19th-century Italian civil record.
    1. Identify Record Type, Primary Subject Name, Date of Event, Father's Name, Mother's Name (with maiden name), and Town.
    2. Provide a full transcription of names and any marginalia.
    3. Provide an English Summary of the key findings.
    
    IMPORTANT: After your summary, provide a single line starting with "RAW_DATA: " followed by a JSON block exactly like this:
    RAW_DATA: {{"type": "...", "subject": "...", "date": "...", "father": "...", "mother": "...", "town": "...", "notes": "..."}}
    """
    response = _model_instance.generate_content([prompt, {"mime_type": "image/jpeg", "data": img_bytes}])
    return response.text

# --- CSV HELPER ---
def format_csv_row(ai_text, image_id):
    try:
        match = re.search(r'RAW_DATA:\s*(\{.*?\})', ai_text, re.DOTALL)
        if match:
            data = json.loads(match.group(1))
            row = [image_id, data.get("type",""), data.get("subject",""), data.get("date",""), data.get("father",""), data.get("mother",""), data.get("town",""), data.get("notes","").replace("\n", " ")]
            return ",".join([f'"{str(x)}"' for x in row])
    except:
        return None

# --- SIDEBAR ---
with st.sidebar:
    st.header("⚙️ App Management")
    st.write(f"**Model:** {CHOSEN_MODEL}")
    st.write(f"**Cache TTL:** 15m")
    if st.button("🗑️ Clear Cache & History"):
        st.cache_data.clear()
        st.session_state.history = []
        st.rerun()

    if st.session_state.history:
        st.markdown("---")
        st.header("🕒 Recent History")
        for h_id in reversed(st.session_state.history[-5:]):
            if st.button(f"📄 {h_id}", key=f"hist_{h_id}", use_container_width=True):
                st.query_params["image_id"] = h_id
                st.rerun()

    # --- NEW CSV HELP SECTION ---
    st.markdown("---")
    with st.expander("📊 CSV Log Guide"):
        st.markdown("""
        **Column Meanings:**
        * **ID:** The unique Antenati Image ID.
        * **Type:** Birth, Marriage, Death, etc.
        * **Subject:** The primary person in the record.
        * **Date:** When the event was recorded.
        * **Father/Mother:** Parents (includes maiden names).
        * **Town:** Location of the record.
        * **Notes:** Marginalia (marriages, deaths) or age/occupation details.
        """)

# --- MAIN UI ---
st.title("🏛️ Antenati Downloader & AI Translator")

st.markdown(f"""
💡 **How to use:** Paste a **Full URL** (recommended for best metadata) or an **Image ID**. <br>
**Example URL:** https://antenati.cultura.gov.it/ark:/12657/an_ua264421/LzPr8VJ <br>
**Example ID:** LzPr8VJ
""", unsafe_allow_html=True)

if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel(CHOSEN_MODEL)
    
    params = st.query_params
    default_id = params.get("image_id", "")
    raw_input = st.text_input("Paste Antenati URL or Image ID:", value=default_id)
    input_id = raw_input.strip().split('/')[-1] if "/" in raw_input else raw_input.strip()

    if input_id:
        if input_id not in st.session_state.history:
            st.session_state.history.append(input_id)

        try:
            record_meta = get_antenati_metadata(raw_input if "http" in raw_input else input_id)
            img_data = get_stitched_image(input_id)
            
            st.download_button("📥 Download JPG", img_data, f"{input_id}.jpg", "image/jpeg")
            
            status_area = st.empty()
            status_area.info(f"⏳ AI is analyzing record: {input_id}. Results will appear **below the image** once completed...")

            st.image(img_data, use_container_width=True)
            st.info(f"📍 **Archival Context:** {record_meta}")

            analysis_text = get_ai_analysis(img_data, record_meta, model)
            display_text = analysis_text.split("RAW_DATA:")[0].strip()
            
            st.markdown('<div id="findings"></div>', unsafe_allow_html=True)
            st.markdown("---")
            st.subheader("📝 AI Findings")
            st.write(display_text)
            
            csv_row = format_csv_row(analysis_text, input_id)
            if csv_row:
                st.markdown("---")
                st.subheader("📊 Research Log Entry (CSV)")
                st.markdown("""
                **Recommended Spreadsheet Headers:** `ID`, `Record Type`, `Subject`, `Date`, `Father`, `Mother`, `Town`, `Notes`
                """)
                st.code(csv_row, language="csv")
                st.caption("☝️ Use the copy button in the top right of the code block above to copy the row for your log.")
            
            status_area.success(f"✅ Analysis complete. [View Findings](#findings)")

        except Exception as e:
            st.error(f"Error: {e}")
else:
    st.error("🔑 API Key missing in Secrets.")
