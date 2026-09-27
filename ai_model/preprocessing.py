import re


def clean_text(text):
    """
    Clean symptom text before sending it to the ML model.
    """

    if text is None:
        return ""

    text = str(text).lower()

    text = re.sub(
        r"[^a-zA-Z\s]",
        " ",
        text
    )

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


def validate_patient_data(age, gender, symptoms):
    """
    Validate the information required by the ML model.
    """

    try:
        age = int(age)
    except (TypeError, ValueError):
        return False

    if age < 1 or age > 120:
        return False

    if gender not in ["Male", "Female", "Other"]:
        return False

    if not symptoms or not str(symptoms).strip():
        return False

    return True