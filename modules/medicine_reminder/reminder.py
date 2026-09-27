from database.database import save_reminder, get_all_reminders

def add_reminder(medicine, time):
    save_reminder(medicine, time)

    return {
        "status": "success",
        "medicine": medicine,
        "time": time
    }

def get_reminders():
    return get_all_reminders()