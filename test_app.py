from streamlit.testing.v1 import AppTest
import pytest
from unittest.mock import patch

def test_app_initialization():
    """Basic check to see if the app title renders."""
    at = AppTest.from_file("streamlit_app.py").run(timeout=15)
    assert any("Antenati" in m.value for m in at.title)

def test_csv_format_logic():
    """Verify the 10-column CSV structure exactly."""
    from streamlit_app import format_csv_row
    
    # We include 'job' and 'notes' to ensure we get all 10 columns
    sample_data = {
        "type": "Nascita",
        "subject": "Mario Rossi",
        "date": "1880",
        "father": "Giuseppe",
        "mother": "Maria Biondi",
        "town": "Salerno",
        "job": "Contadino",
        "notes": "Twin birth"
    }
    
    # This should produce exactly 10 quoted values separated by commas
    row = format_csv_row(sample_data, "LzPr8VJ", "https://antenati.it/test")
    
    # Logic check: 10 columns = 9 commas
    comma_count = row.count(",")
    assert comma_count == 9, f"Expected 9 commas for 10 columns, but found {comma_count}. Row: {row}"
    assert '"Contadino"' in row
    assert '"https://antenati.it/test"' in row

@patch("streamlit_app.get_stitched_image")
def test_query_params_handling(mock_stitch):
    """Ensure image_id from URL is recognized."""
    mock_stitch.return_value = b"fakeimage"
    at = AppTest.from_file("streamlit_app.py")
    at.query_params["image_id"] = "LzPr8VJ"
    at.run(timeout=15)
    assert at.text_input[0].value == "LzPr8VJ"
