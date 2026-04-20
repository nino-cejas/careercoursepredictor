import os
import random
from pathlib import Path

import numpy as np
import pandas as pd
from flask import Flask, jsonify, request
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score
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


def rounded_metrics(metrics: dict[str, float]) -> dict[str, float]:
    return {metric: round(value, 4) for metric, value in metrics.items()}


def rounded_model_summary(summary: dict[str, dict[str, float]]) -> dict[str, dict[str, float]]:
    return {group: rounded_metrics(metrics) for group, metrics in summary.items()}


def safe_divide(numerator: float, denominator: float) -> float:
    return numerator / denominator if denominator else 0.0


def compute_holland_similarity(left: str, right: str) -> float:
    if not left or not right:
        return 0.0

    overlap = sum(1 for left_char, right_char in zip(left[:3], right[:3]) if left_char == right_char)
    return overlap / 3.0


def compute_scct_proximity(actual: float, expected: float) -> float:
    return max(0.0, 1.0 - (abs(actual - expected) / 4.0))


def compute_profile_similarity(
    user_features: dict[str, object],
    candidate_features: dict[str, object],
) -> float:
    # Weighted profile similarity that combines categorical matches and SCCT distance.
    best_subject_match = 1.0 if user_features["best_subject"] == candidate_features["best_subject"] else 0.0
    shs_strand_match = 1.0 if user_features["shs_strand"] == candidate_features["shs_strand"] else 0.0
    holland_match = compute_holland_similarity(
        str(user_features["holland_code"]),
        str(candidate_features["holland_code"]),
    )

    se_proximity = compute_scct_proximity(
        float(user_features["scct_se"]),
        float(candidate_features["scct_se"]),
    )
    oe_proximity = compute_scct_proximity(
        float(user_features["scct_oe"]),
        float(candidate_features["scct_oe"]),
    )
    b_proximity = compute_scct_proximity(
        float(user_features["scct_b"]),
        float(candidate_features["scct_b"]),
    )

    return (
        0.15 * best_subject_match
        + 0.15 * shs_strand_match
        + 0.25 * holland_match
        + 0.15 * se_proximity
        + 0.15 * oe_proximity
        + 0.15 * b_proximity
    )


def resolve_local_neighbor_count(pool_size: int) -> int:
    if pool_size <= 0:
        return 0

    # Keep neighborhoods local: 2% of pool, bounded for stability and speed.
    scaled = int(pool_size * 0.02)
    return min(pool_size, max(12, min(400, scaled)))


def compute_local_model_summary(
    user_features: dict[str, object],
    evidence: dict[str, object],
    fallback_summary: dict[str, dict[str, float]],
) -> tuple[dict[str, dict[str, float]], dict[str, float | int | str]]:
    feature_records = evidence.get("feature_records")
    y_true_labels = np.asarray(evidence.get("y_true_labels", []), dtype=object)
    top_1_pred_labels = np.asarray(evidence.get("top1_pred_labels", []), dtype=object)
    top_1_hits = np.asarray(evidence.get("top1_hits", []), dtype=float)
    top_3_hits = np.asarray(evidence.get("top3_hits", []), dtype=float)

    if not isinstance(feature_records, list) or not feature_records:
        return fallback_summary, {
            "method": "global_fallback",
            "sample_size": 0,
            "pool_size": 0,
            "average_similarity": 0.0,
        }

    pool_size = len(feature_records)
    if (
        top_1_hits.shape[0] != pool_size
        or top_3_hits.shape[0] != pool_size
        or y_true_labels.shape[0] != pool_size
        or top_1_pred_labels.shape[0] != pool_size
    ):
        return fallback_summary, {
            "method": "global_fallback",
            "sample_size": 0,
            "pool_size": pool_size,
            "average_similarity": 0.0,
        }

    similarities = np.array(
        [compute_profile_similarity(user_features, candidate) for candidate in feature_records],
        dtype=float,
    )
    neighbor_count = resolve_local_neighbor_count(pool_size)
    if neighbor_count == 0:
        return fallback_summary, {
            "method": "global_fallback",
            "sample_size": 0,
            "pool_size": pool_size,
            "average_similarity": 0.0,
        }

    neighbor_indices = np.argpartition(similarities, -neighbor_count)[-neighbor_count:]
    neighbor_similarities = similarities[neighbor_indices]
    similarity_sum = float(neighbor_similarities.sum())

    if similarity_sum > 0:
        local_weights = neighbor_similarities
        method = "local_weighted_knn_test_set"
    else:
        local_weights = np.ones(neighbor_count, dtype=float)
        method = "local_unweighted_knn_test_set"

    local_y_true = y_true_labels[neighbor_indices]
    local_top_1_pred = top_1_pred_labels[neighbor_indices]
    local_top_3_hits = top_3_hits[neighbor_indices] > 0.5

    top_1_summary = {
        "accuracy": float(accuracy_score(local_y_true, local_top_1_pred, sample_weight=local_weights)),
        "recall": float(
            recall_score(
                local_y_true,
                local_top_1_pred,
                average="weighted",
                zero_division=0,
                sample_weight=local_weights,
            )
        ),
        "f1_score": float(
            f1_score(
                local_y_true,
                local_top_1_pred,
                average="weighted",
                zero_division=0,
                sample_weight=local_weights,
            )
        ),
        "precision": float(
            precision_score(
                local_y_true,
                local_top_1_pred,
                average="weighted",
                zero_division=0,
                sample_weight=local_weights,
            )
        ),
    }

    top_3_summary = compute_top_k_confusion_summary(
        top_k_hits=local_top_3_hits,
        k=3,
        sample_weights=local_weights,
    )

    return {
        "top1": top_1_summary,
        "top3": top_3_summary,
    }, {
        "method": method,
        "sample_size": int(neighbor_count),
        "pool_size": int(pool_size),
        "average_similarity": float(neighbor_similarities.mean()),
    }


def compute_top_k_hits(
    y_true: pd.Series,
    probabilities: np.ndarray,
    class_labels: np.ndarray,
    k: int,
) -> np.ndarray:
    if probabilities.ndim != 2 or probabilities.shape[0] == 0:
        return np.array([], dtype=bool)

    top_k = max(1, min(k, probabilities.shape[1]))
    top_indices = np.argpartition(probabilities, -top_k, axis=1)[:, -top_k:]
    top_labels = class_labels[top_indices]
    y_true_values = y_true.to_numpy().reshape(-1, 1)
    return (top_labels == y_true_values).any(axis=1)


def compute_top_k_hit_rate(
    y_true: pd.Series,
    probabilities: np.ndarray,
    class_labels: np.ndarray,
    k: int,
) -> float:
    hits = compute_top_k_hits(y_true=y_true, probabilities=probabilities, class_labels=class_labels, k=k)
    if hits.size == 0:
        return 0.0
    return float(hits.mean())


def compute_top_k_confusion_summary(
    top_k_hits: np.ndarray,
    k: int,
    sample_weights: np.ndarray | None = None,
) -> dict[str, float]:
    hits = np.asarray(top_k_hits, dtype=float)
    if hits.size == 0:
        return {
            "accuracy": 0.0,
            "recall": 0.0,
            "f1_score": 0.0,
            "precision": 0.0,
        }

    if sample_weights is None:
        weights = np.ones(hits.shape[0], dtype=float)
    else:
        weights = np.asarray(sample_weights, dtype=float)
        if weights.shape[0] != hits.shape[0]:
            raise ValueError("sample_weights must match top_k_hits size.")

    total_weight = float(weights.sum())
    if total_weight <= 0:
        return {
            "accuracy": 0.0,
            "recall": 0.0,
            "f1_score": 0.0,
            "precision": 0.0,
        }

    top_k = max(1, int(k))

    weighted_tp = float(np.dot(hits, weights))
    weighted_predictions = total_weight * top_k
    weighted_actuals = total_weight

    weighted_fp = max(0.0, weighted_predictions - weighted_tp)
    weighted_fn = max(0.0, weighted_actuals - weighted_tp)

    precision = safe_divide(weighted_tp, weighted_tp + weighted_fp)
    recall = safe_divide(weighted_tp, weighted_tp + weighted_fn)
    f1 = safe_divide(2.0 * precision * recall, precision + recall)

    return {
        "accuracy": safe_divide(weighted_tp, total_weight),
        "recall": recall,
        "f1_score": f1,
        "precision": precision,
    }


def print_model_summary(summary: dict[str, dict[str, float]]) -> None:
    top_1 = summary["top1"]
    top_3 = summary["top3"]

    print("Model Summary (Top-1 vs Top-3)")
    print(f"{'Metric':<10} {'Top-1':>10} {'Top-3':>10}")
    print(f"{'Accuracy':<10} {top_1['accuracy']:>10.4f} {top_3['accuracy']:>10.4f}")
    print(f"{'Recall':<10} {top_1['recall']:>10.4f} {top_3['recall']:>10.4f}")
    print(f"{'F1-Score':<10} {top_1['f1_score']:>10.4f} {top_3['f1_score']:>10.4f}")
    print(f"{'Precision':<10} {top_1['precision']:>10.4f} {top_3['precision']:>10.4f}")


def load_and_train_model(
    dataset_path: Path,
) -> tuple[Pipeline, dict[str, dict[str, float]], dict[str, object]]:
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
    y_test_values = y_test.to_numpy()
    top_1_hits = y_pred == y_test_values

    top_1_summary = {
        "accuracy": float(accuracy_score(y_test, y_pred)),
        "recall": float(recall_score(y_test, y_pred, average="weighted", zero_division=0)),
        "f1_score": float(f1_score(y_test, y_pred, average="weighted", zero_division=0)),
        "precision": float(
            precision_score(y_test, y_pred, average="weighted", zero_division=0)
        ),
    }

    test_probabilities = model.predict_proba(X_test)
    classifier = model.named_steps["classifier"]
    class_labels = classifier.classes_
    top_3_hits = compute_top_k_hits(
        y_true=y_test,
        probabilities=test_probabilities,
        class_labels=class_labels,
        k=3,
    )
    top_3_summary = compute_top_k_confusion_summary(top_k_hits=top_3_hits, k=3)

    local_evidence = {
        "feature_records": X_test.reset_index(drop=True).to_dict("records"),
        "y_true_labels": y_test_values,
        "top1_pred_labels": y_pred,
        "top1_hits": top_1_hits,
        "top3_hits": top_3_hits,
    }

    return model, {"top1": top_1_summary, "top3": top_3_summary}, local_evidence


MODEL, MODEL_SUMMARY, MODEL_EVIDENCE = load_and_train_model(DATASET_PATH)

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

        model_features = {
            "best_subject": best_subject,
            "shs_strand": shs_strand,
            "holland_code": holland_code,
            "scct_se": scct_se,
            "scct_oe": scct_oe,
            "scct_b": scct_b,
        }

        model_input = pd.DataFrame(
            [
                model_features
            ]
        )

        local_model_summary, local_summary_meta = compute_local_model_summary(
            user_features=model_features,
            evidence=MODEL_EVIDENCE,
            fallback_summary=MODEL_SUMMARY,
        )

        probabilities = MODEL.predict_proba(model_input)[0]
        classifier = MODEL.named_steps["classifier"]
        class_labels = classifier.classes_
        top_k = min(3, len(probabilities))
        top_indices = np.argsort(probabilities)[-top_k:][::-1]

        top_predictions: list[dict[str, object]] = []
        for rank, index in enumerate(top_indices, start=1):
            label = class_labels[index]
            predicted_career, predicted_course = label.split("|||", 1)
            top_predictions.append(
                {
                    "rank": rank,
                    "best_career": predicted_career,
                    "best_course": predicted_course,
                    "confidence": round(float(probabilities[index]), 4),
                }
            )

        best_prediction = top_predictions[0]
        confidence = float(best_prediction["confidence"])

        predicted_career = str(best_prediction["best_career"])
        predicted_course = str(best_prediction["best_course"])

        return jsonify(
            {
                "best_subject": best_subject,
                "subject_averages": subject_averages,
                "riasec_scores": riasec_scores,
                "holland_code": holland_code,
                "scct_averages": scct_averages,
                "best_career": predicted_career,
                "best_course": predicted_course,
                "top_predictions": top_predictions,
                "model_accuracy": round(local_model_summary["top1"]["accuracy"], 4),
                "model_summary": rounded_model_summary(local_model_summary),
                "model_summary_meta": {
                    "method": str(local_summary_meta["method"]),
                    "sample_size": int(local_summary_meta["sample_size"]),
                    "pool_size": int(local_summary_meta["pool_size"]),
                    "average_similarity": round(float(local_summary_meta["average_similarity"]), 4),
                },
                "global_model_summary": rounded_model_summary(MODEL_SUMMARY),
                "prediction_confidence": round(confidence, 4),
                "model_input": model_features,
            }
        )

    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    except Exception as exc:
        return jsonify({"error": f"Prediction failed: {exc}"}), 500


if __name__ == "__main__":
    print_model_summary(MODEL_SUMMARY)
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "5000"))
    debug = os.getenv("FLASK_DEBUG", "0") == "1"
    app.run(host=host, port=port, debug=debug)
