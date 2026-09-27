from modules.feedback.feedback import validate_feedback

def test_valid_feedback():
    result = validate_feedback("Very useful application", 5)
    assert result is True

def test_invalid_feedback():
    result = validate_feedback("", 5)
    assert result is False