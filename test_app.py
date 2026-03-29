from streamlit.testing.v1 import AppTest
import pytest

def test_app_initialization():
    """Ensure the app starts and shows the title."""
    at = AppTest.from_file("streamlit_app.py").run()
    assert any("Antenati Downloader" in m.value for m in at.title)

def test_query_params_handling():
    """Ensure passing an image_id in the URL populates the input field."""
    at = AppTest.from_file("streamlit_app.py")
    at.query_params["image_id"] = "LzPr8VJ"
    at.run()
    # verify the first text_input is correctly filled from params
    assert at.text_input[0].value == "LzPr8VJ"

def test_csv_format_logic():
    """Test the logic of the CSV row builder directly."""
    from streamlit_app import format_csv_row
    
    sample_data = {
        "type": "Nascita",
        "subject": "Mario Rossi",
        "date": "1880",
        "father": "Giuseppe",
        "mother": "Maria Biondi",
        "town": "Salerno",
        "job": "Contadino",
        "notes": "None"
    }
    
    row = format_csv_row(sample_data, "12345", "https://antenati.it/test")
    # Verify the 10-column structure (should contain 9 commas)
    assert row.count(",") == 9
