import os
import sqlite3
from datetime import datetime


BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

DATABASE = os.path.join(
    BASE_DIR,
    "database",
    "doctor.db"
)


def get_connection():

    connection = sqlite3.connect(
        DATABASE
    )

    connection.row_factory = sqlite3.Row

    return connection


def init_db():

    connection = get_connection()

    cursor = connection.cursor()

    # -------------------------------------------------
    # NEW PATIENT PROFILE TABLE
    # -------------------------------------------------

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS patient_profiles (

            patient_id TEXT PRIMARY KEY,

            name TEXT NOT NULL,

            age INTEGER NOT NULL,

            gender TEXT NOT NULL,

            medical_history TEXT DEFAULT '',

            created_at TEXT NOT NULL
        )
        """
    )

    # -------------------------------------------------
    # MEDICAL RECORDS TABLE
    # -------------------------------------------------

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS medical_records (

            record_id INTEGER PRIMARY KEY AUTOINCREMENT,

            patient_id TEXT NOT NULL,

            symptoms TEXT NOT NULL,

            prediction TEXT NOT NULL,

            confidence REAL,

            heart_rate REAL,

            spo2 REAL,

            temperature REAL,

            blood_pressure TEXT,

            created_at TEXT NOT NULL,

            FOREIGN KEY(patient_id)
                REFERENCES patient_profiles(patient_id)
        )
        """
    )

    # -------------------------------------------------
    # OLD PATIENT TABLE
    # Kept so existing project functionality is not
    # unnecessarily destroyed.
    # -------------------------------------------------

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS patients (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            symptoms TEXT,

            prediction TEXT,

            created_at TEXT
        )
        """
    )

    # -------------------------------------------------
    # FEEDBACK
    # -------------------------------------------------

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS feedback (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            message TEXT,

            rating INTEGER,

            created_at TEXT
        )
        """
    )

    # -------------------------------------------------
    # REMINDERS
    # -------------------------------------------------

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS reminders (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            medicine TEXT,

            time TEXT
        )
        """
    )

    connection.commit()

    connection.close()


def generate_patient_id():

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT patient_id
        FROM patient_profiles
        ORDER BY rowid DESC
        LIMIT 1
        """
    )

    row = cursor.fetchone()

    connection.close()

    if row is None:

        return "P10001"

    last_id = row["patient_id"]

    try:

        number = int(
            last_id.replace(
                "P",
                ""
            )
        )

    except ValueError:

        number = 10000

    return f"P{number + 1:05d}"


def create_patient(
    name,
    age,
    gender,
    medical_history=""
):

    patient_id = generate_patient_id()

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO patient_profiles
        (
            patient_id,
            name,
            age,
            gender,
            medical_history,
            created_at
        )
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            patient_id,
            name,
            age,
            gender,
            medical_history,
            datetime.now().isoformat()
        )
    )

    connection.commit()

    connection.close()

    return patient_id


def get_patient(patient_id):

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            patient_id,
            name,
            age,
            gender,
            medical_history,
            created_at
        FROM patient_profiles
        WHERE patient_id = ?
        """,
        (patient_id,)
    )

    row = cursor.fetchone()

    connection.close()

    if row is None:

        return None

    return dict(row)


def get_patient_records(patient_id):

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            record_id,
            patient_id,
            symptoms,
            prediction,
            confidence,
            heart_rate,
            spo2,
            temperature,
            blood_pressure,
            created_at
        FROM medical_records
        WHERE patient_id = ?
        ORDER BY record_id DESC
        """,
        (patient_id,)
    )

    rows = cursor.fetchall()

    connection.close()

    return [
        dict(row)
        for row in rows
    ]


def save_medical_record(
    patient_id,
    symptoms,
    prediction,
    confidence=None,
    heart_rate=None,
    spo2=None,
    temperature=None,
    blood_pressure=None
):

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO medical_records
        (
            patient_id,
            symptoms,
            prediction,
            confidence,
            heart_rate,
            spo2,
            temperature,
            blood_pressure,
            created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            patient_id,
            symptoms,
            prediction,
            confidence,
            heart_rate,
            spo2,
            temperature,
            blood_pressure,
            datetime.now().isoformat()
        )
    )

    connection.commit()

    connection.close()


# -----------------------------------------------------
# EXISTING FUNCTIONALITY
# -----------------------------------------------------

def save_patient(
    symptoms,
    prediction
):

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO patients
        (
            symptoms,
            prediction,
            created_at
        )
        VALUES (?, ?, ?)
        """,
        (
            symptoms,
            prediction,
            datetime.now().isoformat()
        )
    )

    connection.commit()

    connection.close()


def save_feedback(
    message,
    rating
):

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO feedback
        (
            message,
            rating,
            created_at
        )
        VALUES (?, ?, ?)
        """,
        (
            message,
            rating,
            datetime.now().isoformat()
        )
    )

    connection.commit()

    connection.close()


def save_reminder(
    medicine,
    time
):

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO reminders
        (
            medicine,
            time
        )
        VALUES (?, ?)
        """,
        (
            medicine,
            time
        )
    )

    connection.commit()

    connection.close()


def get_all_reminders():

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            id,
            medicine,
            time
        FROM reminders
        """
    )

    rows = cursor.fetchall()

    connection.close()

    return [
        {
            "id": row["id"],
            "medicine": row["medicine"],
            "time": row["time"]
        }
        for row in rows
    ]