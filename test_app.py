import streamlit as st
# 1. Mock the secret BEFORE importing or running the app
if "GEMINI_API_KEY" not in st.secrets:
    st.secrets["GEMINI_API_KEY"] = "test_key"

from streamlit.testing.v1 import AppTest
import pytest

def test_app_initialization():
    """Ensure the app starts and shows the title."""
    at = AppTest.from_file("streamlit_app.py").run()
    # Using a more flexible check in case other markdowns exist
    assert any("Antenati Downloader" in m.value for m in at.title)

def test_query_params_handling():
    """Ensure passing an image_id in the URL populates the input field."""
    at = AppTest.from_file("streamlit_app.py")
    at.query_params["image_id"] = "LzPr8VJ"
    at.run()
    
    # Now that secrets are mocked, this element will exist
    assert at.text_input[0].value == "LzPr8VJ"

def test_csv_format_logic():
    """Test the logic of the CSV row builder directly."""
    # We import inside the test to ensure st.secrets is already mocked
    from streamlit_app import format_csv_row
    
    sample_data = {
        "type": "Nascita",
        "subject": "Mario Rossi",
        "date": "1880",
        "father": "Giuseppe",
        "mother": "Maria Biondi",
        "town": "Salerno",
        "job": "Contadino",
        "notes": "Twin"
    }
    
    row = format_csv_row(sample_data, "12345", "https://antenati.it/test")
    
    # Check for 10 columns (9 commas)
    assert row.count(",") == 9
    assert "Contadino" in row
