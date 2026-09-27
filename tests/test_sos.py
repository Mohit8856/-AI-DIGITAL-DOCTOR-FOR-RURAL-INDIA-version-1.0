from modules.sos.sos_alert import send_sos

def test_sos():
    result = send_sos("Emergency assistance required")

    assert result["status"] == "SOS triggered"
    assert result["message"] == "Emergency assistance required"