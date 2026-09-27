from flask import (
    Flask,
    render_template,
    request,
    jsonify
)

from ai_model.prediction import (
    predict_disease
)

from database.database import (
    init_db,
    save_feedback,
    save_patient,
    create_patient,
    get_patient,
    get_patient_records,
    save_medical_record
)

from modules.hospital.hospital_finder import (
    find_hospitals
)

from modules.sos.sos_alert import (
    send_sos
)

from modules.medicine_reminder.reminder import (
    add_reminder,
    get_reminders
)

from hardware.smartwatch_ble import (
    smartwatch
)

from hardware.sensor_data import (
    process_sensor_data
)


app = Flask(__name__)


# -----------------------------------------------------
# DATABASE
# -----------------------------------------------------

init_db()


# -----------------------------------------------------
# SMARTWATCH
# -----------------------------------------------------

smartwatch.start()


# -----------------------------------------------------
# HOME
# -----------------------------------------------------

@app.route("/")
def home():

    return render_template(
        "index.html"
    )


# -----------------------------------------------------
# CREATE NEW PATIENT
# -----------------------------------------------------

@app.route(
    "/patient",
    methods=["POST"]
)
def create_new_patient():

    data = request.get_json()

    if not data:

        return jsonify({
            "error": "No patient data received"
        }), 400

    name = str(
        data.get("name", "")
    ).strip()

    age = data.get("age")

    gender = str(
        data.get("gender", "")
    ).strip()

    medical_history = str(
        data.get(
            "medical_history",
            ""
        )
    ).strip()

    if not name:

        return jsonify({
            "error": "Patient name is required"
        }), 400

    try:

        age = int(age)

    except (TypeError, ValueError):

        return jsonify({
            "error": "Valid age is required"
        }), 400

    if age < 1 or age > 120:

        return jsonify({
            "error": "Age must be between 1 and 120"
        }), 400

    if gender not in [
        "Male",
        "Female",
        "Other"
    ]:

        return jsonify({
            "error": "Valid gender is required"
        }), 400

    patient_id = create_patient(
        name,
        age,
        gender,
        medical_history
    )

    patient = get_patient(
        patient_id
    )

    return jsonify({
        "message":
            "Patient created successfully.",
        "patient": patient
    })


# -----------------------------------------------------
# GET EXISTING PATIENT
# -----------------------------------------------------

@app.route(
    "/patient/<patient_id>",
    methods=["GET"]
)
def existing_patient(patient_id):

    patient_id = patient_id.strip()

    patient = get_patient(
        patient_id
    )

    if patient is None:

        return jsonify({
            "error":
                "Patient ID not found."
        }), 404

    records = get_patient_records(
        patient_id
    )

    patient["records"] = records

    return jsonify(
        patient
    )


# -----------------------------------------------------
# PREDICT DISEASE
# -----------------------------------------------------

@app.route(
    "/predict",
    methods=["POST"]
)
def predict():

    data = request.get_json()

    if not data:

        return jsonify({
            "error": "No data received"
        }), 400

    symptoms = str(
        data.get(
            "symptoms",
            ""
        )
    ).strip()

    patient_id = str(
        data.get(
            "patient_id",
            ""
        )
    ).strip()

    # ---------------------------------------------
    # PATIENT IS REQUIRED
    # ---------------------------------------------

    if not patient_id:

        return jsonify({
            "error":
                "Please create or select a patient first."
        }), 400

    patient = get_patient(
        patient_id
    )

    if patient is None:

        return jsonify({
            "error":
                "Patient ID not found."
        }), 404

    if not symptoms:

        return jsonify({
            "error":
                "Please enter symptoms"
        }), 400

    # ---------------------------------------------
    # GET CURRENT SMARTWATCH DATA
    # ---------------------------------------------

    watch_data = smartwatch.get_data()

    sensor_data = process_sensor_data(
        watch_data
    )

    # ---------------------------------------------
    # ML PREDICTION
    # AGE + GENDER + SYMPTOMS
    # ---------------------------------------------

    result = predict_disease(
        patient["age"],
        patient["gender"],
        symptoms
    )

    if "error" in result:

        return jsonify(result), 400

    # ---------------------------------------------
    # SAVE OLD PATIENT RECORD
    # Preserves previous functionality
    # ---------------------------------------------

    save_patient(
        symptoms,
        result["prediction"]
    )

    # ---------------------------------------------
    # SAVE NEW MEDICAL RECORD
    # ---------------------------------------------

    save_medical_record(

        patient_id=patient_id,

        symptoms=result["symptoms"],

        prediction=result["prediction"],

        confidence=result.get(
            "confidence"
        ),

        heart_rate=sensor_data.get(
            "heart_rate"
        ),

        spo2=sensor_data.get(
            "spo2"
        ),

        temperature=sensor_data.get(
            "temperature"
        ),

        blood_pressure=sensor_data.get(
            "blood_pressure"
        )
    )

    result["patient_id"] = patient_id

    result["patient_name"] = patient[
        "name"
    ]

    result["vitals"] = sensor_data

    return jsonify(result)


# -----------------------------------------------------
# HOSPITALS
# -----------------------------------------------------

@app.route(
    "/hospitals",
    methods=["GET"]
)
def hospitals():

    latitude = request.args.get(
        "latitude"
    )

    longitude = request.args.get(
        "longitude"
    )

    if not latitude or not longitude:

        return jsonify({
            "error":
                "Location not provided"
        }), 400

    try:

        latitude = float(
            latitude
        )

        longitude = float(
            longitude
        )

    except ValueError:

        return jsonify({
            "error":
                "Invalid location"
        }), 400

    result = find_hospitals(
        latitude,
        longitude
    )

    return jsonify(result)


# -----------------------------------------------------
# SOS
# -----------------------------------------------------

@app.route(
    "/sos",
    methods=["POST"]
)
def sos():

    data = request.get_json()

    if not data:

        data = {}

    message = data.get(
        "message",
        "Emergency assistance required"
    )

    result = send_sos(
        message
    )

    return jsonify(result)


# -----------------------------------------------------
# REMINDER
# -----------------------------------------------------

@app.route(
    "/reminder",
    methods=["POST"]
)
def reminder():

    data = request.get_json()

    if not data:

        return jsonify({
            "error":
                "No data received"
        }), 400

    medicine = data.get(
        "medicine"
    )

    time = data.get(
        "time"
    )

    if not medicine or not time:

        return jsonify({
            "error":
                "Medicine and time are required"
        }), 400

    result = add_reminder(
        medicine,
        time
    )

    return jsonify(result)


@app.route(
    "/reminders",
    methods=["GET"]
)
def reminders():

    return jsonify(
        get_reminders()
    )


# -----------------------------------------------------
# FEEDBACK
# -----------------------------------------------------

@app.route(
    "/feedback",
    methods=["POST"]
)
def feedback():

    data = request.get_json()

    if not data:

        return jsonify({
            "error":
                "No feedback received"
        }), 400

    message = data.get(
        "message",
        ""
    )

    rating = data.get(
        "rating",
        0
    )

    try:

        rating = int(rating)

    except (TypeError, ValueError):

        return jsonify({
            "error":
                "Invalid rating"
        }), 400

    if not message:

        return jsonify({
            "error":
                "Feedback message is required"
        }), 400

    if rating < 1 or rating > 5:

        return jsonify({
            "error":
                "Rating must be between 1 and 5"
        }), 400

    save_feedback(
        message,
        rating
    )

    return jsonify({
        "message":
            "Feedback submitted successfully"
    })


# -----------------------------------------------------
# WATCH DATA
# -----------------------------------------------------

@app.route(
    "/watch-data",
    methods=["GET"]
)
def watch_data():

    data = smartwatch.get_data()

    processed = process_sensor_data(
        data
    )

    processed["connected"] = data.get(
        "connected",
        False
    )

    processed["device"] = data.get(
        "device",
        "MARV NEO"
    )

    return jsonify(
        processed
    )


# -----------------------------------------------------
# WATCH STATUS
# -----------------------------------------------------

@app.route(
    "/watch-status",
    methods=["GET"]
)
def watch_status():

    data = smartwatch.get_data()

    return jsonify({

        "connected":
            data.get(
                "connected",
                False
            ),

        "device":
            data.get(
                "device",
                "MARV NEO"
            )
    })


# -----------------------------------------------------
# SHUTDOWN
# -----------------------------------------------------

if __name__ == "__main__":

    try:

        app.run(
            host="0.0.0.0",
            port=5000,
            debug=True,
            use_reloader=False
        )

    finally:

        smartwatch.stop()