from datetime import datetime

def send_sos(message):
    return {
        "status": "SOS triggered",
        "message": message,
        "time": datetime.now().isoformat()
    }