def validate_sensor_data(data):
    if not isinstance(data, dict):
        return False

    if "heart_rate" not in data:
        return False

    return True


def process_sensor_data(data):

    result = {
        "heart_rate": None,
        "spo2": None,
        "temperature": None,
        "blood_pressure": None
    }

    if data.get("heart_rate") is not None:
        try:
            result["heart_rate"] = float(data["heart_rate"])
        except (TypeError, ValueError):
            result["heart_rate"] = None

    if data.get("spo2") is not None:
        try:
            value = float(data["spo2"])

            if 0 < value <= 100:
                result["spo2"] = value

        except (TypeError, ValueError):
            result["spo2"] = None

    if data.get("temperature") is not None:
        try:
            value = float(data["temperature"])

            if 20 <= value <= 45:
                result["temperature"] = value

        except (TypeError, ValueError):
            result["temperature"] = None

    if data.get("blood_pressure") is not None:
        result["blood_pressure"] = str(
            data["blood_pressure"]
        )

    return result