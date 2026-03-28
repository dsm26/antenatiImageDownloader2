# antenatiImageDownloader2
Antenati Image Download with Translation

🏛️ Antenati Downloader & AI Translator
A specialized genealogical tool built with Streamlit and Google Gemini AI to bridge the gap between digital archives and family history research. This application automates the process of retrieving high-resolution records from the Italian Antenati (National Archives) portal and provides instant, context-aware translations of 19th-century handwriting.
🚀 Features
• High-Res Image Stitching: Automatically bypasses browser viewer limitations by fetching individual IIIF tiles and stitching them into a full-quality JPEG.
• Triple-Strategy Metadata: Extracts archival context (Town, Year, Record Type) using three fallback methods:
1. IIIF Manifest Parsing for official labels.
2. HTML Web Scraping for page titles and breadcrumbs.
3. URL Deconstruction to identify specific archival units (an_ua).
• AI-Powered Translation: Uses Gemini 1.5 Flash to transcribe difficult Italian handwriting and summarize key genealogical data (parents, witnesses, dates) in English.
• Research History: Remembers your last 5 searches in a sidebar for instant back-and-forth comparison.
• Smart Caching: Reduces API costs and server load by storing results for 15 minutes per session.
🛠️ Technical Requirements
To replicate or run this app, you need the following Python environment:
Dependencies
• streamlit: The web framework.
• Pillow (PIL): For high-resolution image processing and stitching.
• requests: For handling complex HTTP headers and multi-tile downloads.
• google-generativeai: To interface with the Gemini LLM.
API Configuration
The app requires a Google Gemini API Key.
• Local development: Add GEMINI_API_KEY = "your_key_here" to .streamlit/secrets.toml.
• Streamlit Cloud: Add the key to the Secrets section in the app settings.
📖 Functional Blueprint (For Developers/AI)
If you are using an AI to recreate this app, use the following logic requirements:
1. Header Security: All requests to antenati.cultura.gov.it must include a User-Agent (Chrome/Windows) and a Referer header to prevent 403 Forbidden errors.
2. Stitching Logic: * Query info.json for total width/height.
• Loop through rows and columns based on tiles[0][width].
• Concatenate tiles into a PIL.Image object.
3. Context-Aware Prompting: * Pass the extracted "Archival Context" string directly into the AI prompt.
• Instruct the AI to specifically look for marginalia (handwritten notes in the margins), which often contain marriage or death cross-references.
4. UI State Management: * Use st.empty() placeholders for progress bars and status messages to ensure a clean "swap" from "Processing" to "Success" states.
• Implement an HTML anchor <div id="findings"></div> to allow the user to jump past the large image directly to the text results.
💡 Usage Tip
For the best results, always paste the Full URL from your browser's address bar. This provides the scraper with the town and year, which significantly increases the accuracy of the AI's transcription of local surnames.
