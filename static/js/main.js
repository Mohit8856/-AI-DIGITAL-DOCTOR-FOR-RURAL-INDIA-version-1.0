let currentPatientId = null;
let watchConnected = false;
let smartwatchTimer = null;


// =====================================================
// GENERAL
// =====================================================

function scrollToSection(id) {

    const element =
        document.getElementById(id);

    if (element) {

        element.scrollIntoView({
            behavior: "smooth"
        });
    }
}


function showToast(message) {

    const toast =
        document.getElementById("toast");

    if (!toast) {
        return;
    }

    toast.innerText = message;

    toast.style.display = "block";

    setTimeout(() => {

        toast.style.display = "none";

    }, 3000);
}


// =====================================================
// PATIENT MANAGEMENT
// =====================================================

function showNewPatientForm() {

    document.getElementById(
        "newPatientForm"
    ).style.display = "block";

    document.getElementById(
        "existingPatientForm"
    ).style.display = "none";
}


function showExistingPatientForm() {

    document.getElementById(
        "existingPatientForm"
    ).style.display = "block";

    document.getElementById(
        "newPatientForm"
    ).style.display = "none";
}


async function createPatient() {

    const name =
        document.getElementById(
            "patientName"
        ).value.trim();

    const age =
        document.getElementById(
            "patientAge"
        ).value;

    const gender =
        document.getElementById(
            "patientGender"
        ).value;

    const medicalHistory =
        document.getElementById(
            "medicalHistory"
        ).value.trim();


    if (!name || !age || !gender) {

        showToast(
            "Please enter name, age and gender."
        );

        return;
    }


    try {

        const response =
            await fetch(
                "/patient",
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body: JSON.stringify({

                        name: name,

                        age: age,

                        gender: gender,

                        medical_history:
                            medicalHistory
                    })
                }
            );


        const data =
            await response.json();


        if (!response.ok) {

            showToast(
                data.error ||
                "Unable to create patient."
            );

            return;
        }


        currentPatientId =
            data.patient.patient_id;


        displayPatient(
            data.patient,
            []
        );


        showToast(
            "Patient created successfully."
        );


        document.getElementById(
            "newPatientForm"
        ).style.display = "none";


    } catch (error) {

        showToast(
            "Unable to connect to server."
        );
    }
}


// =====================================================
// LOAD EXISTING PATIENT
// =====================================================

async function loadPatient() {

    const patientId =
        document.getElementById(
            "existingPatientId"
        ).value.trim().toUpperCase();


    if (!patientId) {

        showToast(
            "Enter your Patient ID."
        );

        return;
    }


    try {

        const response =
            await fetch(
                `/patient/${encodeURIComponent(patientId)}`
            );


        const data =
            await response.json();


        if (!response.ok) {

            showToast(
                data.error ||
                "Patient not found."
            );

            return;
        }


        currentPatientId =
            data.patient_id;


        displayPatient(
            data,
            data.records || []
        );


        showToast(
            "Patient record loaded."
        );


        document.getElementById(
            "existingPatientForm"
        ).style.display = "none";


    } catch (error) {

        showToast(
            "Unable to retrieve patient."
        );
    }
}


// =====================================================
// DISPLAY PATIENT
// =====================================================

function displayPatient(
    patient,
    records
) {

    const container =
        document.getElementById(
            "patientResult"
        );


    let historyHTML = "";


    if (
        records &&
        records.length > 0
    ) {

        historyHTML = `

            <div class="patient-history">

                <h3>
                    📋 Medical History
                </h3>

                ${records.map(
                    record => `

                    <div class="history-item">

                        <strong>
                            ${escapeHtml(
                                record.prediction
                            )}
                        </strong>

                        <p>
                            Symptoms:
                            ${escapeHtml(
                                record.symptoms
                            )}
                        </p>

                        <p>
                            Confidence:
                            ${
                                record.confidence !== null
                                ? record.confidence + "%"
                                : "N/A"
                            }
                        </p>

                        <small>
                            ${escapeHtml(
                                record.created_at
                            )}
                        </small>

                    </div>

                `
                ).join("")}

            </div>
        `;

    } else {

        historyHTML = `

            <div class="empty-state">

                <p>
                    No previous medical records
                    found for this patient.
                </p>

            </div>
        `;
    }


    container.innerHTML = `

        <div class="result-success">

            <h3>
                ✅ Patient Profile
            </h3>

            <p>
                <strong>
                    Patient ID:
                </strong>

                ${escapeHtml(
                    patient.patient_id
                )}
            </p>

            <p>
                <strong>
                    Name:
                </strong>

                ${escapeHtml(
                    patient.name
                )}
            </p>

            <p>
                <strong>
                    Age:
                </strong>

                ${patient.age}
            </p>

            <p>
                <strong>
                    Gender:
                </strong>

                ${escapeHtml(
                    patient.gender
                )}
            </p>

            <p>
                <strong>
                    Medical History:
                </strong>

                ${
                    patient.medical_history
                    ? escapeHtml(
                        patient.medical_history
                    )
                    : "None provided"
                }
            </p>

            <p>
                🆔 Keep this Patient ID:
                <strong>
                    ${escapeHtml(
                        patient.patient_id
                    )}
                </strong>
            </p>

        </div>

        ${historyHTML}
    `;


    document.getElementById(
        "activePatient"
    ).innerText =
        `👤 ${patient.name} | ID: ${patient.patient_id} | Age: ${patient.age} | ${patient.gender}`;
}


// =====================================================
// SAFE HTML
// =====================================================

function escapeHtml(value) {

    return String(value)
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
}


// =====================================================
// AI PREDICTION
// =====================================================

async function predict() {

    const symptoms =
        document.getElementById(
            "symptoms"
        ).value.trim();

    const result =
        document.getElementById(
            "result"
        );


    if (!currentPatientId) {

        showToast(
            "Please create or select a patient first."
        );

        return;
    }


    if (!symptoms) {

        showToast(
            "Please enter your symptoms first."
        );

        return;
    }


    result.innerHTML = `

        <div class="result-success">

            <p>
                🤖 AI is analyzing your
                age, gender and symptoms...
            </p>

        </div>
    `;


    try {

        const response =
            await fetch(
                "/predict",
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body: JSON.stringify({

                        patient_id:
                            currentPatientId,

                        symptoms:
                            symptoms
                    })
                }
            );


        const data =
            await response.json();


        if (!response.ok) {

            result.innerHTML = `

                <div class="result-warning">

                    ${escapeHtml(
                        data.error ||
                        "Prediction failed."
                    )}

                </div>
            `;

            return;
        }


        result.innerHTML = `

            <div class="${
                data.emergency
                ? "result-warning"
                : "result-success"
            }">

                <h3>

                    ${
                        data.emergency
                        ? "🚨 Attention"
                        : "🤖 AI Assessment"
                    }

                </h3>


                <p>

                    <strong>
                        Patient:
                    </strong>

                    ${escapeHtml(
                        data.patient_name
                    )}

                </p>


                <p>

                    <strong>
                        Possible condition:
                    </strong>

                    ${escapeHtml(
                        data.prediction
                    )}

                </p>


                <p>

                    <strong>
                        AI confidence:
                    </strong>

                    ${data.confidence}%

                </p>


                <p>

                    ${escapeHtml(
                        data.message
                    )}

                </p>


                <p>

                    <small>

                        Model features:
                        Age + Gender + Symptoms

                    </small>

                </p>

            </div>
        `;


    } catch (error) {

        result.innerHTML = `

            <div class="result-warning">

                Unable to connect to
                the AI service.

            </div>
        `;
    }
}


// =====================================================
// MEDICINE REMINDER
// =====================================================

async function addReminder() {

    const medicine =
        document.getElementById(
            "medicine"
        ).value.trim();

    const time =
        document.getElementById(
            "medicineTime"
        ).value;

    const container =
        document.getElementById(
            "reminders"
        );


    if (!medicine || !time) {

        showToast(
            "Enter medicine name and time."
        );

        return;
    }


    try {

        const response =
            await fetch(
                "/reminder",
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body: JSON.stringify({

                        medicine: medicine,

                        time: time
                    })
                }
            );


        const data =
            await response.json();


        if (
            response.ok &&
            data.status === "success"
        ) {

            container.innerHTML = `

                <div class="result-success">

                    💊 ${escapeHtml(
                        data.medicine
                    )}

                    scheduled for

                    ${escapeHtml(
                        data.time
                    )}

                </div>
            `;


            document.getElementById(
                "medicine"
            ).value = "";

            document.getElementById(
                "medicineTime"
            ).value = "";


            showToast(
                "Medicine reminder added."
            );

        } else {

            showToast(
                data.error ||
                "Unable to add reminder."
            );
        }


    } catch (error) {

        showToast(
            "Unable to connect to server."
        );
    }
}


// =====================================================
// SOS
// =====================================================

async function sendSOS() {

    const container =
        document.getElementById(
            "sosResult"
        );


    const confirmed =
        confirm(
            "Are you sure you want to activate the emergency SOS?"
        );


    if (!confirmed) {
        return;
    }


    try {

        const response =
            await fetch(
                "/sos",
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body: JSON.stringify({

                        message:
                            "Emergency assistance required"
                    })
                }
            );


        const data =
            await response.json();


        container.innerHTML = `

            <div class="result-warning">

                🚨 ${escapeHtml(
                    data.status
                )}

                <br>

                ${escapeHtml(
                    data.message
                )}

            </div>
        `;


        showToast(
            "Emergency SOS activated."
        );


    } catch (error) {

        showToast(
            "Unable to activate SOS."
        );
    }
}


// =====================================================
// HOSPITAL FINDER
// =====================================================

async function findHospitals() {

    const container =
        document.getElementById("hospitalResult");

    if (!container) {
        console.error(
            "Hospital result container not found."
        );
        return;
    }


    // -------------------------------------------------
    // SHOW LOCATION LOADING
    // -------------------------------------------------

    container.innerHTML = `

        <div class="empty-state">

            <div class="empty-icon">
                📍
            </div>

            <h3>
                Getting your current location...
            </h3>

            <p>
                Please allow location access.
            </p>

        </div>
    `;


    // -------------------------------------------------
    // CHECK GEOLOCATION SUPPORT
    // -------------------------------------------------

    if (!navigator.geolocation) {

        container.innerHTML = `

            <div class="result-warning">

                📍 Location services are not
                supported by your browser.

            </div>
        `;

        return;
    }


    // -------------------------------------------------
    // GET CURRENT GPS LOCATION
    // -------------------------------------------------

    navigator.geolocation.getCurrentPosition(

        async function(position) {

            const latitude =
                position.coords.latitude;

            const longitude =
                position.coords.longitude;

            const accuracy =
                position.coords.accuracy;


            // -------------------------------------------------
            // DEBUG - SHOW EXACT GPS COORDINATES
            // -------------------------------------------------

            console.log(
                "===================================="
            );

            console.log(
                "GPS LOCATION RECEIVED"
            );

            console.log(
                "Latitude:",
                latitude
            );

            console.log(
                "Longitude:",
                longitude
            );

            console.log(
                "GPS Accuracy:",
                accuracy,
                "meters"
            );

            console.log(
                "===================================="
            );


            // -------------------------------------------------
            // CHECK THAT COORDINATES ARE VALID
            // -------------------------------------------------

            if (
                !Number.isFinite(latitude) ||
                !Number.isFinite(longitude)
            ) {

                container.innerHTML = `

                    <div class="result-warning">

                        ❌ Invalid GPS coordinates
                        received from your browser.

                    </div>
                `;

                return;
            }


            // -------------------------------------------------
            // SHOW DETECTED LOCATION
            // -------------------------------------------------

            container.innerHTML = `

                <div class="empty-state">

                    <div class="empty-icon">
                        📍
                    </div>

                    <h3>
                        Location detected
                    </h3>

                    <p>

                        Latitude:
                        ${latitude.toFixed(6)}

                        <br>

                        Longitude:
                        ${longitude.toFixed(6)}

                        <br>

                        GPS Accuracy:
                        ±${Math.round(accuracy)}
                        meters

                    </p>

                    <p>
                        🔍 Searching hospitals
                        within 20 km...
                    </p>

                </div>
            `;


            // -------------------------------------------------
            // SEND GPS LOCATION TO FLASK
            // -------------------------------------------------

            try {

                const url =
                    `/hospitals?latitude=${encodeURIComponent(latitude)}&longitude=${encodeURIComponent(longitude)}`;


                console.log(
                    "Hospital API Request:",
                    url
                );


                const response =
                    await fetch(url);


                // -------------------------------------------------
                // CHECK SERVER RESPONSE
                // -------------------------------------------------

                if (!response.ok) {

                    let errorMessage =
                        "Server error while finding hospitals.";

                    try {

                        const errorData =
                            await response.json();

                        if (errorData.error) {
                            errorMessage =
                                errorData.error;
                        }

                    } catch (jsonError) {

                        console.error(
                            "Could not read server error:",
                            jsonError
                        );
                    }

                    throw new Error(
                        errorMessage
                    );
                }


                // -------------------------------------------------
                // READ HOSPITAL DATA
                // -------------------------------------------------

                const hospitals =
                    await response.json();


                console.log(
                    "Hospitals received:",
                    hospitals
                );


                // -------------------------------------------------
                // NO HOSPITALS FOUND
                // -------------------------------------------------

                if (
                    !Array.isArray(hospitals) ||
                    hospitals.length === 0
                ) {

                    container.innerHTML = `

                        <div class="result-warning">

                            🏥 No mapped hospitals
                            were found within
                            20 km of your location.

                        </div>
                    `;

                    return;
                }


                // -------------------------------------------------
                // DISPLAY HOSPITALS
                // -------------------------------------------------

                container.innerHTML =
                    hospitals.map(
                        hospital => `

                        <div class="hospital-card">

                            <h3>

                                🏥

                                ${escapeHtml(
                                    hospital.name ||
                                    "Hospital"
                                )}

                            </h3>


                            <p>

                                📍

                                <strong>

                                    ${
                                        hospital.distance
                                    }
                                    km away

                                </strong>

                            </p>


                            <p>

                                ${escapeHtml(
                                    hospital.address ||
                                    "Address not available"
                                )}

                            </p>


                            <p>

                                📞

                                ${escapeHtml(
                                    hospital.phone ||
                                    "Phone not available"
                                )}

                            </p>


                            <a
                                href="${hospital.maps_url}"
                                target="_blank"
                                rel="noopener noreferrer"
                                class="maps-button"
                            >

                                🗺️ Get Directions

                            </a>

                        </div>

                    `
                    ).join("");


            } catch (error) {

                // -------------------------------------------------
                // API / INTERNET ERROR
                // -------------------------------------------------

                console.error(
                    "Hospital search error:",
                    error
                );


                container.innerHTML = `

                    <div class="result-warning">

                        ❌ Unable to retrieve hospitals.

                        <br><br>

                        ${escapeHtml(
                            error.message ||
                            "Please check your internet connection."
                        )}

                    </div>
                `;
            }
        },


        // -------------------------------------------------
        // GPS ERROR
        // -------------------------------------------------

        function(error) {

            console.error(
                "GPS ERROR:",
                error
            );


            let message =
                "Unable to get your current location.";


            if (error.code === 1) {

                message =
                    "Location permission was denied. Please allow location access for this website.";

            }
            else if (error.code === 2) {

                message =
                    "Your location could not be determined. Please check your device location settings.";

            }
            else if (error.code === 3) {

                message =
                    "Location request timed out. Please try again.";

            }


            container.innerHTML = `

                <div class="result-warning">

                    📍 ${message}

                </div>
            `;
        },


        // -------------------------------------------------
        // GPS OPTIONS
        // -------------------------------------------------

        {
            enableHighAccuracy: true,

            timeout: 30000,

            // 0 means:
            // Do not use an old cached location.
            maximumAge: 0
        }
    );
}

// =====================================================
// FEEDBACK
// =====================================================

async function submitFeedback() {

    const message =
        document.getElementById(
            "feedback"
        ).value.trim();


    const rating =
        parseInt(
            document.getElementById(
                "rating"
            ).value
        );


    if (!message) {

        showToast(
            "Please enter your feedback."
        );

        return;
    }


    try {

        const response =
            await fetch(
                "/feedback",
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body: JSON.stringify({

                        message: message,

                        rating: rating
                    })
                }
            );


        const data =
            await response.json();


        if (!response.ok) {

            showToast(
                data.error ||
                "Unable to submit feedback."
            );

            return;
        }


        document.getElementById(
            "feedbackResult"
        ).innerHTML = `

            <div class="result-success">

                ⭐ Thank you for your feedback!

            </div>
        `;


        document.getElementById(
            "feedback"
        ).value = "";


    } catch (error) {

        showToast(
            "Unable to submit feedback."
        );
    }
}


// =====================================================
// VOICE INPUT
// =====================================================

function startVoiceInput() {

    const SpeechRecognition =
        window.SpeechRecognition ||
        window.webkitSpeechRecognition;


    if (!SpeechRecognition) {

        showToast(
            "Voice recognition is not supported in this browser."
        );

        return;
    }


    const recognition =
        new SpeechRecognition();


    recognition.lang =
        "en-IN";

    recognition.continuous =
        false;

    recognition.interimResults =
        false;


    showToast(
        "🎤 Listening..."
    );


    recognition.start();


    recognition.onresult =
        function(event) {

            const text =
                event.results[0][0]
                    .transcript;


            document.getElementById(
                "symptoms"
            ).value = text;


            showToast(
                "Voice converted to text."
            );
        };


    recognition.onerror =
        function() {

            showToast(
                "Unable to recognize your voice."
            );
        };
}


// =====================================================
// SMARTWATCH / IOT
// =====================================================

async function updateWatchData() {

    try {

        const response =
            await fetch(
                "/watch-data",
                {
                    cache: "no-store"
                }
            );


        if (!response.ok) {
            return;
        }


        const data =
            await response.json();


        watchConnected =
            Boolean(
                data.connected
            );


        updateWatchConnectionUI(
            data.connected,
            data.device
        );


        updateSmartwatchVitals(
            data
        );


    } catch (error) {

        watchConnected = false;

        updateWatchConnectionUI(
            false,
            "MARV NEO"
        );

        updateSmartwatchOffline();
    }
}


function updateSmartwatchVitals(data) {

    const heartRate =
        document.getElementById(
            "heartRate"
        );

    const spo2 =
        document.getElementById(
            "spo2"
        );

    const temperature =
        document.getElementById(
            "temperature"
        );

    const bloodPressure =
        document.getElementById(
            "bloodPressure"
        );


    if (
        data.heart_rate !== null &&
        data.heart_rate !== undefined
    ) {

        heartRate.innerText =
            Math.round(
                data.heart_rate
            );

    } else {

        heartRate.innerText =
            "--";
    }


    if (
        data.spo2 !== null &&
        data.spo2 !== undefined
    ) {

        spo2.innerText =
            Math.round(
                data.spo2
            );

    } else {

        spo2.innerText =
            "--";
    }


    if (
        data.temperature !== null &&
        data.temperature !== undefined
    ) {

        temperature.innerText =
            Number(
                data.temperature
            ).toFixed(1);

    } else {

        temperature.innerText =
            "--";
    }


    if (
        data.blood_pressure !== null &&
        data.blood_pressure !== undefined
    ) {

        bloodPressure.innerText =
            data.blood_pressure;

    } else {

        bloodPressure.innerText =
            "--";
    }
}


function updateSmartwatchOffline() {

    document.getElementById(
        "heartRate"
    ).innerText = "--";

    document.getElementById(
        "spo2"
    ).innerText = "--";

    document.getElementById(
        "temperature"
    ).innerText = "--";

    document.getElementById(
        "bloodPressure"
    ).innerText = "--";
}


function updateWatchConnectionUI(
    connected,
    device
) {

    const button =
        document.querySelector(
            ".outline-btn"
        );


    if (!button) {
        return;
    }


    if (connected) {

        button.innerText =
            `🟢 ${device || "MARV NEO"} Connected`;

    } else {

        button.innerText =
            "🔵 Connect IoT Device";
    }
}


function connectDevice() {

    if (watchConnected) {

        showToast(
            "🟢 MARV NEO is connected."
        );

    } else {

        showToast(
            "🔵 Searching for MARV NEO..."
        );
    }


    updateWatchData();
}


// =====================================================
// START WATCH MONITORING
// =====================================================

function startSmartwatchMonitoring() {

    if (smartwatchTimer) {

        clearInterval(
            smartwatchTimer
        );
    }


    smartwatchTimer =
        setInterval(
            updateWatchData,
            2000
        );
}


// =====================================================
// PAGE START
// =====================================================

window.addEventListener(
    "DOMContentLoaded",
    function() {

        updateWatchData();

        startSmartwatchMonitoring();

    }
);