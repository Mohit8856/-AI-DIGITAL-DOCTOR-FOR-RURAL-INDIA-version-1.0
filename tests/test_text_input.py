from modules.text_input.text_processor import process_text

def test_process_text():
    result = process_text("FEVER, Cough!")
    assert result == "fever cough"