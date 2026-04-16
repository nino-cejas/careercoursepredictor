import random
from pathlib import Path

import pandas as pd
from flask import Flask, jsonify, request
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

APP_ROOT = Path(__file__).resolve().parent
DATASET_PATH = APP_ROOT / "career_suggestion.csv"

FEATURE_COLUMNS = [
    "best_subject",
    "shs_strand",
    "holland_code",
    "scct_se",
    "scct_oe",
    "scct_b",
]

TARGET_CAREER = "best_career"
TARGET_COURSE = "best_course"
SHS_STRANDS = {"STEM", "ABM", "HUMSS", "ICT", "HE"}

RIASEC_QUESTION_BANK = [
    {"id": 1, "code": "R", "text": "I enjoy fixing machines or tools."},
    {"id": 2, "code": "R", "text": "I like building practical things with my hands."},
    {"id": 3, "code": "R", "text": "I prefer outdoor technical work over desk work."},
    {"id": 4, "code": "R", "text": "I am interested in operating equipment safely."},
    {"id": 5, "code": "R", "text": "I like solving physical or mechanical problems."},
    {"id": 6, "code": "R", "text": "I enjoy step-by-step work that produces visible results."},
    {"id": 7, "code": "R", "text": "I can focus on tasks that require precision and safety."},
    {"id": 8, "code": "R", "text": "I would enjoy a job involving tools, systems, or machinery."},
    {"id": 9, "code": "I", "text": "I like analyzing data to find patterns."},
    {"id": 10, "code": "I", "text": "I enjoy science and research activities."},
    {"id": 11, "code": "I", "text": "I like asking why things work the way they do."},
    {"id": 12, "code": "I", "text": "I enjoy reading about new discoveries and technologies."},
    {"id": 13, "code": "I", "text": "I like solving complex logic problems."},
    {"id": 14, "code": "I", "text": "I enjoy designing experiments or testing ideas."},
    {"id": 15, "code": "I", "text": "I am curious about math, systems, and evidence."},
    {"id": 16, "code": "I", "text": "I prefer evidence-based decisions over guesses."},
    {"id": 17, "code": "A", "text": "I enjoy creating designs, visuals, or original content."},
    {"id": 18, "code": "A", "text": "I like expressing ideas through art, writing, or media."},
    {"id": 19, "code": "A", "text": "I enjoy creative projects with flexible rules."},
    {"id": 20, "code": "A", "text": "I like brainstorming unique concepts."},
    {"id": 21, "code": "A", "text": "I enjoy improving the look and feel of products."},
    {"id": 22, "code": "A", "text": "I like combining imagination with communication."},
    {"id": 23, "code": "A", "text": "I am motivated by originality and innovation."},
    {"id": 24, "code": "A", "text": "I enjoy presenting creative work to others."},
    {"id": 25, "code": "S", "text": "I enjoy helping people solve personal or school problems."},
    {"id": 26, "code": "S", "text": "I like teaching or guiding others."},
    {"id": 27, "code": "S", "text": "I prefer work that contributes to community well-being."},
    {"id": 28, "code": "S", "text": "I am patient when listening to others."},
    {"id": 29, "code": "S", "text": "I enjoy teamwork and collaboration."},
    {"id": 30, "code": "S", "text": "I like mentoring younger students or peers."},
    {"id": 31, "code": "S", "text": "I feel fulfilled when I support others."},
    {"id": 32, "code": "S", "text": "I can communicate clearly in person."},
    {"id": 33, "code": "E", "text": "I like leading projects and making decisions."},
    {"id": 34, "code": "E", "text": "I enjoy persuading others to support ideas."},
    {"id": 35, "code": "E", "text": "I am motivated by goals, growth, and achievement."},
    {"id": 36, "code": "E", "text": "I like initiating plans and opportunities."},
    {"id": 37, "code": "E", "text": "I enjoy business or management topics."},
    {"id": 38, "code": "E", "text": "I am comfortable speaking in front of groups."},
    {"id": 39, "code": "E", "text": "I like taking responsibility for outcomes."},
    {"id": 40, "code": "E", "text": "I enjoy negotiating and strategic planning."},
    {"id": 41, "code": "C", "text": "I prefer organized tasks with clear procedures."},
    {"id": 42, "code": "C", "text": "I like checking details for accuracy."},
    {"id": 43, "code": "C", "text": "I enjoy working with records, numbers, or schedules."},
    {"id": 44, "code": "C", "text": "I like following systems and standards."},
    {"id": 45, "code": "C", "text": "I am reliable in completing tasks on time."},
    {"id": 46, "code": "C", "text": "I prefer structured environments over unpredictable ones."},
    {"id": 47, "code": "C", "text": "I enjoy planning and documenting work carefully."},
    {"id": 48, "code": "C", "text": "I am comfortable with administrative or clerical tasks."},
]

SCCT_QUESTIONS = {
    "scct_se": [
        "I can succeed in my chosen career path.",
        "I can learn difficult skills needed for my future job.",
        "I can perform well in tasks related to my career goals.",
        "I can overcome challenges while pursuing my career.",
    ],
    "scct_oe": [
        "My future career will provide good opportunities.",
        "My effort in school will help me achieve career success.",
        "A career aligned to my strengths will improve my quality of life.",
        "My chosen course can lead to meaningful work.",
    ],
    "scct_b": [
        "Financial limitations may affect my career path.",
        "Lack of resources may make my career goals difficult.",
        "Family or social pressures may influence my career decision.",
        "Limited access to opportunities may delay my plans.",
    ],
}

RIASEC_CODES = ("R", "I", "A", "S", "E", "C")


def clamp_score(value: float) -> int:
    rounded = int(value + 0.5)
    return max(1, min(5, rounded))


def average(values: list[float]) -> float:
    return sum(values) / len(values)


def validate_grade_block(grades: dict) -> dict[str, float]:
    subjects = ("Math", "English", "Science")
    averages: dict[str, float] = {}

    for subject in subjects:
        if subject not in grades or len(grades[subject]) != 4:
            raise ValueError(f"{subject} must contain 4 grade values (Grades 7-10).")
        values = [float(v) for v in grades[subject]]
        if any(v < 70 or v > 100 for v in values):
            raise ValueError(f"{subject} grades must be between 70 and 100.")
        averages[subject] = round(average(values), 2)

    return averages


def compute_riasec_scores(answers: dict) -> dict[str, int]:
    if len(answers) != 48:
        raise ValueError("Exactly 48 RIASEC answers are required.")

    scores = {code: 0 for code in RIASEC_CODES}
    questions_by_id = {str(item["id"]): item for item in RIASEC_QUESTION_BANK}

    for question_id, raw_value in answers.items():
        if str(question_id) not in questions_by_id:
            raise ValueError(f"Invalid RIASEC question id: {question_id}")
        value = int(raw_value)
        if value < 1 or value > 5:
            raise ValueError("RIASEC answers must be in range 1 to 5.")
        code = questions_by_id[str(question_id)]["code"]
        scores[code] += value

    return scores


def compute_scct_averages(scct_data: dict) -> dict[str, float]:
    result: dict[str, float] = {}
    for key in ("scct_se", "scct_oe", "scct_b"):
        values = scct_data.get(key)
        if not isinstance(values, list) or len(values) != 4:
            raise ValueError(f"{key} must contain exactly 4 answers.")
        numeric_values = [float(v) for v in values]
        if any(v < 1 or v > 5 for v in numeric_values):
            raise ValueError(f"{key} answers must be between 1 and 5.")
        result[key] = round(average(numeric_values), 2)
    return result


def compute_top_holland_code(riasec_scores: dict[str, int]) -> str:
    ordered = sorted(riasec_scores.items(), key=lambda item: (-item[1], item[0]))
    top_three = [code for code, _ in ordered[:3]]
    return "".join(top_three)


def compute_best_subject(subject_averages: dict[str, float]) -> str:
    tie_break_order = {"Math": 0, "Science": 1, "English": 2}
    return max(
        subject_averages,
        key=lambda subject: (subject_averages[subject], -tie_break_order[subject]),
    )


def load_and_train_model(dataset_path: Path) -> tuple[Pipeline, float]:
    if not dataset_path.exists():
        raise FileNotFoundError(f"Dataset not found: {dataset_path}")

    df = pd.read_csv(dataset_path)
    expected_columns = set(FEATURE_COLUMNS + [TARGET_CAREER, TARGET_COURSE])
    missing_columns = expected_columns - set(df.columns)
    if missing_columns:
        missing = ", ".join(sorted(missing_columns))
        raise ValueError(f"Dataset is missing required columns: {missing}")

    model_df = df[FEATURE_COLUMNS + [TARGET_CAREER, TARGET_COURSE]].copy()
    model_df["target_label"] = (
        model_df[TARGET_CAREER].astype(str) + "|||" + model_df[TARGET_COURSE].astype(str)
    )

    X = model_df[FEATURE_COLUMNS]
    y = model_df["target_label"]

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42,
        shuffle=True,
    )

    preprocessor = ColumnTransformer(
        transformers=[
            (
                "categorical",
                OneHotEncoder(handle_unknown="ignore"),
                ["best_subject", "shs_strand", "holland_code"],
            ),
            ("numeric", "passthrough", ["scct_se", "scct_oe", "scct_b"]),
        ]
    )

    classifier = LogisticRegression(
        solver="saga",
        max_iter=1200,
        tol=5e-3,
        random_state=42,
    )

    model = Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            ("classifier", classifier),
        ]
    )

    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)

    return model, float(accuracy)


MODEL, MODEL_ACCURACY = load_and_train_model(DATASET_PATH)

app = Flask(__name__, static_folder="public", static_url_path="")


@app.get("/")
def home() -> object:
    return app.send_static_file("index.html")


@app.get("/api/questions")
def get_questions() -> object:
    riasec_questions = random.sample(RIASEC_QUESTION_BANK, len(RIASEC_QUESTION_BANK))
    return jsonify(
        {
            "riasec": [{"id": q["id"], "text": q["text"]} for q in riasec_questions],
            "scct": SCCT_QUESTIONS,
        }
    )


@app.post("/api/predict")
def predict() -> object:
    payload = request.get_json(silent=True) or {}

    try:
        grades = payload.get("grades", {})
        shs_strand = str(payload.get("shs_strand", "")).strip().upper()
        riasec_answers = payload.get("riasec_answers", {})
        scct_answers = payload.get("scct_answers", {})

        if shs_strand not in SHS_STRANDS:
            raise ValueError("shs_strand must be one of: STEM, ABM, HUMSS, ICT, HE")

        subject_averages = validate_grade_block(grades)
        best_subject = compute_best_subject(subject_averages)

        riasec_scores = compute_riasec_scores(riasec_answers)
        holland_code = compute_top_holland_code(riasec_scores)

        scct_averages = compute_scct_averages(scct_answers)
        scct_se = clamp_score(scct_averages["scct_se"])
        scct_oe = clamp_score(scct_averages["scct_oe"])
        scct_b = clamp_score(scct_averages["scct_b"])

        model_input = pd.DataFrame(
            [
                {
                    "best_subject": best_subject,
                    "shs_strand": shs_strand,
                    "holland_code": holland_code,
                    "scct_se": scct_se,
                    "scct_oe": scct_oe,
                    "scct_b": scct_b,
                }
            ]
        )

        predicted_label = MODEL.predict(model_input)[0]
        probabilities = MODEL.predict_proba(model_input)[0]
        confidence = float(probabilities.max())

        predicted_career, predicted_course = predicted_label.split("|||", 1)

        return jsonify(
            {
                "best_subject": best_subject,
                "subject_averages": subject_averages,
                "riasec_scores": riasec_scores,
                "holland_code": holland_code,
                "scct_averages": scct_averages,
                "best_career": predicted_career,
                "best_course": predicted_course,
                "model_accuracy": round(MODEL_ACCURACY, 4),
                "prediction_confidence": round(confidence, 4),
                "model_input": {
                    "best_subject": best_subject,
                    "shs_strand": shs_strand,
                    "holland_code": holland_code,
                    "scct_se": scct_se,
                    "scct_oe": scct_oe,
                    "scct_b": scct_b,
                },
            }
        )

    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    except Exception as exc:
        return jsonify({"error": f"Prediction failed: {exc}"}), 500


if __name__ == "__main__":
    app.run(debug=True, port=5000)
