from modules.medicine_reminder.reminder import add_reminder, get_reminders

def test_add_reminder():
    result = add_reminder("Paracetamol", "10:00")

    assert result["status"] == "success"
    assert result["medicine"] == "Paracetamol"
    assert result["time"] == "10:00"

def test_get_reminders():
    result = get_reminders()
    assert isinstance(result, list)