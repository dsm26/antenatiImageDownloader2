import streamlit as st

def show_instructions():
    with st.expander("ℹ️ Instructions"):
        st.markdown("""
        This tool is designed for use with the official [Antenati portal](https://antenati.cultura.gov.it/), 
        not the copies found on FamilySearch.

        **How to use:**
        1. Find the record image you want to download on the Antenati website.
        2. Look for the link labeled "Copia link del bookmark" on that page and click it to copy the address.
        3. Paste that link into the box below.

        **Example URLs:**
        * https://antenati.cultura.gov.it/ark:/12657/an_ua264421/LzPr8VJ - 1871 Civile Nati
        * https://antenati.cultura.gov.it/ark:/12657/an_ua264421/LzPr8x9 - 1871 Civile Nati index page
        * https://antenati.cultura.gov.it/ark:/12657/an_ua36205266/Le8qveo - 1816 Matrimoni index page
        * https://antenati.cultura.gov.it/ark:/12657/an_ua36203217/Lz7XnvP - 1841 Censimento page

        **Example ID:** LzPr8VJ

        **📥 Best Way to Save**
        For the best results, always use the **"Download" button** rather than right-clicking the image. The button automatically names your file using the **Image ID** and will embed the **original Antenati URL** in the file's internal metadata.


        🔗 **Quick Link:** Pass parameters in the browser bar using `?url=FULL_URL` or `?image_id=ID`.


        💡 **AI Use:** By default, this page uses a shared Google Gemini AI account with a daily rate limit for the AI translations. If you plan to perform many translations (e.g. over 100), please [create your own free Gemini API key](https://aistudio.google.com/api-keys) and specify it in the left sidebar. There is no rate limit for the image downloading.
        """)
