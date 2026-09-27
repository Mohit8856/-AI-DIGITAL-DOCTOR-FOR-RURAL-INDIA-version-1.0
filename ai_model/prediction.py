import pandas as pd

from ai_model.model import get_model
from ai_model.preprocessing import (
    clean_text,
    validate_patient_data
)


model = get_model()


def predict_disease(
    age,
    gender,
    symptoms
):

    symptoms = clean_text(
        symptoms
    )

    if not validate_patient_data(
        age,
        gender,
        symptoms
    ):

        return {
            "error":
                "Valid age, gender and symptoms are required."
        }

    age = int(age)

    input_data = pd.DataFrame(
        [
            {
                "age": age,
                "gender": gender,
                "symptoms": symptoms
            }
        ]
    )

    prediction = model.predict(
        input_data
    )[0]

    probabilities = model.predict_proba(
        input_data
    )[0]

    confidence = (
        max(probabilities) * 100
    )

    emergency_conditions = [
        "Respiratory Condition"
    ]

    emergency = (
        prediction
        in emergency_conditions
    )

    if emergency:

        message = (
            "Breathing or chest-related "
            "symptoms may require prompt "
            "medical attention."
        )

    else:

        message = (
            "This is an AI-assisted prediction "
            "based on the provided age, gender "
            "and symptoms. It is not a medical "
            "diagnosis."
        )

    return {

        "prediction": prediction,

        "confidence": round(
            confidence,
            2
        ),

        "emergency": emergency,

        "message": message,

        "age": age,

        "gender": gender,

        "symptoms": symptoms
    }