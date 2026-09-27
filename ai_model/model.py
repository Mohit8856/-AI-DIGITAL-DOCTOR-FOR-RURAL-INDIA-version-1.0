import os
import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

DATA_DIR = os.path.join(
    BASE_DIR,
    "data"
)

TRAINING_FILE = os.path.join(
    DATA_DIR,
    "training.csv"
)

TESTING_FILE = os.path.join(
    DATA_DIR,
    "testing.csv"
)

VALIDATION_FILE = os.path.join(
    DATA_DIR,
    "validation.csv"
)


def load_dataset(file_path):

    if not os.path.exists(file_path):

        raise FileNotFoundError(
            f"Dataset not found: {file_path}"
        )

    data = pd.read_csv(file_path)

    required_columns = [
        "age",
        "gender",
        "symptoms",
        "disease"
    ]

    for column in required_columns:

        if column not in data.columns:

            raise ValueError(
                f"Missing column '{column}' "
                f"in {file_path}"
            )

    data["age"] = pd.to_numeric(
        data["age"],
        errors="coerce"
    )

    data["gender"] = (
        data["gender"]
        .astype(str)
        .str.strip()
    )

    data["symptoms"] = (
        data["symptoms"]
        .astype(str)
        .str.strip()
    )

    data["disease"] = (
        data["disease"]
        .astype(str)
        .str.strip()
    )

    data = data.dropna(
        subset=[
            "age",
            "gender",
            "symptoms",
            "disease"
        ]
    )

    return data


def build_model():

    preprocessor = ColumnTransformer(

        transformers=[

            (
                "symptoms",
                TfidfVectorizer(
                    lowercase=True,
                    ngram_range=(1, 2),
                    min_df=1
                ),
                "symptoms"
            ),

            (
                "gender",
                OneHotEncoder(
                    handle_unknown="ignore"
                ),
                ["gender"]
            ),

            (
                "age",
                StandardScaler(),
                ["age"]
            )
        ]
    )

    classifier = LogisticRegression(
        max_iter=2000
    )

    pipeline = Pipeline(

        steps=[

            (
                "preprocessor",
                preprocessor
            ),

            (
                "classifier",
                classifier
            )
        ]
    )

    return pipeline


def train_model():

    training_data = load_dataset(
        TRAINING_FILE
    )

    testing_data = load_dataset(
        TESTING_FILE
    )

    validation_data = load_dataset(
        VALIDATION_FILE
    )

    X_train = training_data[
        [
            "age",
            "gender",
            "symptoms"
        ]
    ]

    y_train = training_data[
        "disease"
    ]

    X_test = testing_data[
        [
            "age",
            "gender",
            "symptoms"
        ]
    ]

    y_test = testing_data[
        "disease"
    ]

    X_validation = validation_data[
        [
            "age",
            "gender",
            "symptoms"
        ]
    ]

    y_validation = validation_data[
        "disease"
    ]

    model = build_model()

    model.fit(
        X_train,
        y_train
    )

    test_predictions = model.predict(
        X_test
    )

    validation_predictions = model.predict(
        X_validation
    )

    test_accuracy = accuracy_score(
        y_test,
        test_predictions
    )

    validation_accuracy = accuracy_score(
        y_validation,
        validation_predictions
    )

    print("=" * 60)
    print("AI DIGITAL DOCTOR MODEL")
    print("=" * 60)

    print(
        f"Training records: {len(training_data)}"
    )

    print(
        f"Testing records: {len(testing_data)}"
    )

    print(
        f"Validation records: {len(validation_data)}"
    )

    print(
        f"Testing Accuracy: "
        f"{test_accuracy * 100:.2f}%"
    )

    print(
        f"Validation Accuracy: "
        f"{validation_accuracy * 100:.2f}%"
    )

    print(
        "Classes:",
        sorted(
            y_train.unique()
        )
    )

    print("=" * 60)

    return (
        model,
        test_accuracy,
        validation_accuracy
    )


_model = None


def get_model():

    global _model

    if _model is None:

        _model, _, _ = train_model()

    return _model