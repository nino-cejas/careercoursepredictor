const gradeSubjects = ["Math", "English", "Science"];
const gradeLevels = [7, 8, 9, 10];
const riasecPageSize = 12;
const scctOrder = ["scct_se", "scct_oe", "scct_b"];
const scctTitles = {
    scct_se: "Self-Efficacy",
    scct_oe: "Outcome Expectations",
    scct_b: "Barriers",
};

const predictForm = document.getElementById("predictForm");
const statusMessage = document.getElementById("statusMessage");
const submitBtn = document.getElementById("submitBtn");
const nextBtn = document.getElementById("nextBtn");
const prevBtn = document.getElementById("prevBtn");
const riasecContainer = document.getElementById("riasecContainer");
const scctContainer = document.getElementById("scctContainer");
const resultCard = document.getElementById("resultCard");
const wizardSteps = Array.from(document.querySelectorAll(".wizard-step"));
const wizardProgressBar = document.getElementById("wizardProgressBar");
const wizardProgressText = document.getElementById("wizardProgressText");
const riasecPageText = document.getElementById("riasecPageText");
const scctPageText = document.getElementById("scctPageText");
const viewTop1Btn = document.getElementById("viewTop1Btn");
const viewTop3Btn = document.getElementById("viewTop3Btn");
const toggleTop1ExplanationBtn = document.getElementById("toggleTop1ExplanationBtn");
const toggleTop3ExplanationBtn = document.getElementById("toggleTop3ExplanationBtn");
const top1ExplanationBox = document.getElementById("top1ExplanationBox");
const top3ExplanationBox = document.getElementById("top3ExplanationBox");
const top1ExplanationText = document.getElementById("top1ExplanationText");
const top3ExplanationText = document.getElementById("top3ExplanationText");
const localTop1HitRate = document.getElementById("localTop1HitRate");
const localTop3HitRate = document.getElementById("localTop3HitRate");
const confidenceGapHighlight = document.getElementById("confidenceGapHighlight");
const confidenceLevelHighlight = document.getElementById("confidenceLevelHighlight");
const toggleDetailsBtn = document.getElementById("toggleDetailsBtn");
const detailsContainer = document.getElementById("detailsContainer");

const RESULT_VIEW_TOP1 = "top1";
const RESULT_VIEW_TOP3 = "top3";

const wizardState = {
    step: 0,
    riasecPage: 0,
    scctPage: 0,
};

let activeResultView = RESULT_VIEW_TOP3;
let latestPredictionData = null;
let isTop1ExplanationVisible = false;
let isTop3ExplanationVisible = false;
let isDetailsVisible = false;

let riasecQuestions = [];
let scctQuestions = { scct_se: [], scct_oe: [], scct_b: [] };
let riasecAnswers = {};
let scctAnswers = { scct_se: [3, 3, 3, 3], scct_oe: [3, 3, 3, 3], scct_b: [3, 3, 3, 3] };

function createGradeInputs() {
    document.querySelectorAll(".inputs-inline").forEach((container) => {
        const subject = container.dataset.subject;
        gradeLevels.forEach((level) => {
            const input = document.createElement("input");
            input.type = "number";
            input.min = "70";
            input.max = "100";
            input.step = "0.01";
            input.placeholder = `G${level}`;
            input.name = `grade_${subject}_${level}`;
            input.value = "85";
            container.appendChild(input);
        });
    });
}

function createAnswerSelect(defaultValue = "3") {
    const select = document.createElement("select");
    [1, 2, 3, 4, 5].forEach((score) => {
        const option = document.createElement("option");
        option.value = String(score);
        option.textContent = `${score}`;
        if (String(score) === defaultValue) {
            option.selected = true;
        }
        select.appendChild(option);
    });
    return select;
}

function createStarRating(initialValue, onChange) {
    const wrapper = document.createElement("div");
    wrapper.className = "star-rating";
    wrapper.setAttribute("role", "radiogroup");

    const valueText = document.createElement("span");
    valueText.className = "star-value";

    let selected = Number(initialValue);
    const buttons = [];

    function refresh() {
        buttons.forEach((button, index) => {
            const value = index + 1;
            const active = value <= selected;
            button.textContent = active ? "★" : "☆";
            button.classList.toggle("active", active);
            button.setAttribute("aria-checked", String(value === selected));
        });
        valueText.textContent = `${selected}/5`;
    }

    for (let value = 1; value <= 5; value += 1) {
        const button = document.createElement("button");
        button.type = "button";
        button.className = "star-btn";
        button.dataset.value = String(value);
        button.setAttribute("role", "radio");
        button.setAttribute("aria-label", `${value} star`);

        button.addEventListener("click", () => {
            selected = value;
            refresh();
            onChange(selected);
        });

        button.addEventListener("keydown", (event) => {
            if (event.key === "ArrowRight" || event.key === "ArrowUp") {
                event.preventDefault();
                selected = Math.min(5, selected + 1);
                refresh();
                onChange(selected);
            }
            if (event.key === "ArrowLeft" || event.key === "ArrowDown") {
                event.preventDefault();
                selected = Math.max(1, selected - 1);
                refresh();
                onChange(selected);
            }
        });

        buttons.push(button);
        wrapper.appendChild(button);
    }

    wrapper.appendChild(valueText);
    refresh();
    return wrapper;
}

function initializeAnswerState() {
    riasecAnswers = {};
    riasecQuestions.forEach((question) => {
        riasecAnswers[String(question.id)] = 3;
    });
    scctAnswers = { scct_se: [3, 3, 3, 3], scct_oe: [3, 3, 3, 3], scct_b: [3, 3, 3, 3] };
}

function totalRiasecPages() {
    return Math.ceil(riasecQuestions.length / riasecPageSize);
}

function totalScctPages() {
    return scctOrder.length;
}

function totalWizardScreens() {
    return 1 + totalRiasecPages() + totalScctPages();
}

function currentWizardScreen() {
    if (wizardState.step === 0) {
        return 1;
    }
    if (wizardState.step === 1) {
        return 1 + wizardState.riasecPage + 1;
    }
    return 1 + totalRiasecPages() + wizardState.scctPage + 1;
}

function updateProgress() {
    const current = currentWizardScreen();
    const total = totalWizardScreens();
    const pct = (current / total) * 100;
    wizardProgressBar.style.width = `${pct.toFixed(2)}%`;
    wizardProgressText.textContent = `Step ${current} of ${total}`;
}

function renderRiasecPage() {
    const page = wizardState.riasecPage;
    const start = page * riasecPageSize;
    const end = start + riasecPageSize;
    const pageQuestions = riasecQuestions.slice(start, end);

    riasecPageText.textContent = `Page ${page + 1} of ${totalRiasecPages()}`;
    riasecContainer.innerHTML = "";

    pageQuestions.forEach((question, index) => {
        const wrapper = document.createElement("div");
        wrapper.className = "question";

        const text = document.createElement("p");
        text.textContent = `${start + index + 1}. ${question.text}`;

        const rating = createStarRating(riasecAnswers[String(question.id)], (value) => {
            riasecAnswers[String(question.id)] = value;
        });

        wrapper.appendChild(text);
        wrapper.appendChild(rating);
        riasecContainer.appendChild(wrapper);
    });
}

function renderScctPage() {
    const key = scctOrder[wizardState.scctPage];
    const title = scctTitles[key];
    const questions = scctQuestions[key] || [];

    scctPageText.textContent = `${title} - Page ${wizardState.scctPage + 1} of ${totalScctPages()}`;
    scctContainer.innerHTML = "";

    const heading = document.createElement("h3");
    heading.textContent = title;
    scctContainer.appendChild(heading);

    questions.forEach((questionText, index) => {
        const wrapper = document.createElement("div");
        wrapper.className = "question";

        const text = document.createElement("p");
        text.textContent = `${index + 1}. ${questionText}`;

        const rating = createStarRating(scctAnswers[key][index], (value) => {
            scctAnswers[key][index] = value;
        });

        wrapper.appendChild(text);
        wrapper.appendChild(rating);
        scctContainer.appendChild(wrapper);
    });
}

function renderWizardStep() {
    wizardSteps.forEach((stepEl, index) => {
        stepEl.classList.toggle("hidden", index !== wizardState.step);
    });

    if (wizardState.step === 1) {
        renderRiasecPage();
    }
    if (wizardState.step === 2) {
        renderScctPage();
    }

    const atFirstScreen = wizardState.step === 0;
    const atFinalScreen = wizardState.step === 2 && wizardState.scctPage === totalScctPages() - 1;

    prevBtn.disabled = atFirstScreen;
    prevBtn.classList.toggle("hidden", atFirstScreen);

    nextBtn.classList.toggle("hidden", atFinalScreen);
    submitBtn.classList.toggle("hidden", !atFinalScreen);

    updateProgress();
}

function validateAcademicStep() {
    const strand = document.getElementById("shsStrand").value;
    if (!strand) {
        throw new Error("Please select your SHS strand before continuing.");
    }

    gradeSubjects.forEach((subject) => {
        gradeLevels.forEach((level) => {
            const input = predictForm.querySelector(`[name="grade_${subject}_${level}"]`);
            const value = Number(input.value);
            if (!Number.isFinite(value) || value < 70 || value > 100) {
                throw new Error(`Please enter valid ${subject} grade for Grade ${level} (70-100).`);
            }
        });
    });
}

function goNextScreen() {
    statusMessage.classList.remove("error");

    if (wizardState.step === 0) {
        validateAcademicStep();
        wizardState.step = 1;
        wizardState.riasecPage = 0;
    } else if (wizardState.step === 1) {
        if (wizardState.riasecPage < totalRiasecPages() - 1) {
            wizardState.riasecPage += 1;
        } else {
            wizardState.step = 2;
            wizardState.scctPage = 0;
        }
    } else if (wizardState.step === 2 && wizardState.scctPage < totalScctPages() - 1) {
        wizardState.scctPage += 1;
    }

    renderWizardStep();
}

function goPreviousScreen() {
    statusMessage.classList.remove("error");

    if (wizardState.step === 2) {
        if (wizardState.scctPage > 0) {
            wizardState.scctPage -= 1;
        } else {
            wizardState.step = 1;
            wizardState.riasecPage = totalRiasecPages() - 1;
        }
    } else if (wizardState.step === 1) {
        if (wizardState.riasecPage > 0) {
            wizardState.riasecPage -= 1;
        } else {
            wizardState.step = 0;
        }
    }

    renderWizardStep();
}

async function loadQuestions() {
    statusMessage.textContent = "Loading questions...";
    statusMessage.classList.remove("error");

    const response = await fetch("/api/questions");
    if (!response.ok) {
        throw new Error("Failed to load question bank.");
    }

    const data = await response.json();
    riasecQuestions = data.riasec;
    scctQuestions = data.scct;
    initializeAnswerState();
    renderWizardStep();
    statusMessage.textContent = "Ready.";
}

function readGrades() {
    const grades = { Math: [], English: [], Science: [] };

    gradeSubjects.forEach((subject) => {
        gradeLevels.forEach((level) => {
            const input = predictForm.querySelector(`[name="grade_${subject}_${level}"]`);
            grades[subject].push(Number(input.value));
        });
    });

    return grades;
}

function readRiasecAnswers() {
    return {...riasecAnswers };
}

function readScctAnswers() {
    return {
        scct_se: [...scctAnswers.scct_se],
        scct_oe: [...scctAnswers.scct_oe],
        scct_b: scctAnswers.scct_b.map((value) => 6 - value),
    };
}

function setResultList(elementId, items) {
    const list = document.getElementById(elementId);
    list.innerHTML = "";
    items.forEach((item) => {
        const li = document.createElement("li");
        li.textContent = item;
        list.appendChild(li);
    });
}

function toPercent(value) {
    if (value === null || value === undefined) {
        return "-";
    }

    const numericValue = Number(value);
    if (!Number.isFinite(numericValue)) {
        return "-";
    }
    return `${(numericValue * 100).toFixed(2)}%`;
}

function toFixedText(value, decimals = 2) {
    const numericValue = Number(value);
    if (!Number.isFinite(numericValue)) {
        return "-";
    }
    return numericValue.toFixed(decimals);
}

function computeConfidenceGap(predictions) {
    if (!Array.isArray(predictions) || predictions.length < 2) {
        return null;
    }

    const top1Confidence = Number(predictions[0].confidence);
    const top2Confidence = Number(predictions[1].confidence);
    if (!Number.isFinite(top1Confidence) || !Number.isFinite(top2Confidence)) {
        return null;
    }

    return Math.max(0, top1Confidence - top2Confidence);
}

function classifyConfidenceLevel(top1Confidence, confidenceGap) {
    if (!Number.isFinite(top1Confidence)) {
        return {
            label: "Unknown",
            cssClass: "confidence-level-unknown",
        };
    }

    const gap = Number.isFinite(confidenceGap) ? confidenceGap : 0;

    if (top1Confidence >= 0.5 && gap >= 0.1) {
        return {
            label: "High",
            cssClass: "confidence-level-high",
        };
    }

    if (top1Confidence >= 0.3 && gap >= 0.05) {
        return {
            label: "Medium",
            cssClass: "confidence-level-medium",
        };
    }

    return {
        label: "Low",
        cssClass: "confidence-level-low",
    };
}

function applyExplanationToggleState() {
    top1ExplanationBox.classList.toggle("hidden", !isTop1ExplanationVisible);
    top3ExplanationBox.classList.toggle("hidden", !isTop3ExplanationVisible);

    toggleTop1ExplanationBtn.textContent = isTop1ExplanationVisible ?
        "Hide Model Summary Explanation" :
        "Show Model Summary Explanation";
    toggleTop3ExplanationBtn.textContent = isTop3ExplanationVisible ?
        "Hide Model Summary Explanation" :
        "Show Model Summary Explanation";

    toggleTop1ExplanationBtn.setAttribute("aria-expanded", String(isTop1ExplanationVisible));
    toggleTop3ExplanationBtn.setAttribute("aria-expanded", String(isTop3ExplanationVisible));
}

function toggleModelSummaryExplanation(target) {
    if (target === RESULT_VIEW_TOP1) {
        isTop1ExplanationVisible = !isTop1ExplanationVisible;
    }
    if (target === RESULT_VIEW_TOP3) {
        isTop3ExplanationVisible = !isTop3ExplanationVisible;
    }
    applyExplanationToggleState();
}

function applyDetailsToggleState() {
    detailsContainer.classList.toggle("hidden", !isDetailsVisible);
    toggleDetailsBtn.textContent = isDetailsVisible ?
        "Hide Additional Details & RIASEC Scores" :
        "Show Additional Details & RIASEC Scores";
    toggleDetailsBtn.setAttribute("aria-expanded", String(isDetailsVisible));
}

function toggleDetailsVisibility() {
    isDetailsVisible = !isDetailsVisible;
    applyDetailsToggleState();
}

function applyResultViewMode() {
    const isTop1Only = activeResultView === RESULT_VIEW_TOP1;

    resultCard.classList.toggle("view-top1", isTop1Only);
    resultCard.classList.toggle("view-top3", !isTop1Only);

    viewTop1Btn.classList.toggle("active", isTop1Only);
    viewTop3Btn.classList.toggle("active", !isTop1Only);
    viewTop1Btn.setAttribute("aria-pressed", String(isTop1Only));
    viewTop3Btn.setAttribute("aria-pressed", String(!isTop1Only));
}

function setResultViewMode(mode) {
    if (mode !== RESULT_VIEW_TOP1 && mode !== RESULT_VIEW_TOP3) {
        return;
    }

    activeResultView = mode;
    applyResultViewMode();

    if (latestPredictionData) {
        renderResult(latestPredictionData, false);
    }
}

function renderTopPredictions(predictions) {
    const list = document.getElementById("topPredictionsList");
    list.innerHTML = "";

    if (!Array.isArray(predictions) || predictions.length === 0) {
        const emptyItem = document.createElement("li");
        emptyItem.className = "top-prediction-item";
        emptyItem.textContent = "No Top-3 recommendations available.";
        list.appendChild(emptyItem);
        return;
    }

    predictions.forEach((prediction) => {
        const item = document.createElement("li");
        item.className = "top-prediction-item";
        item.textContent = `#${prediction.rank} ${prediction.best_career} - ${prediction.best_course} (${toPercent(
            prediction.confidence
        )})`;
        list.appendChild(item);
    });
}

function renderResult(data, shouldScroll = true) {
    latestPredictionData = data;

    const modelSummary = data.model_summary || {};
    const modelSummaryMeta = data.model_summary_meta || {};
    const globalModelSummary = data.global_model_summary || {};
    const top1Metrics = modelSummary.top1 || {};
    const top3Metrics = modelSummary.top3 || {};
    const globalTop1Metrics = globalModelSummary.top1 || {};
    const globalTop3Metrics = globalModelSummary.top3 || {};
    const summaryMethod = String(modelSummaryMeta.method || "");
    const isLocalSummary = summaryMethod.startsWith("local_");
    const localSampleSize = Number(modelSummaryMeta.sample_size);
    const localPoolSize = Number(modelSummaryMeta.pool_size);
    const localAverageSimilarity = Number(modelSummaryMeta.average_similarity);

    document.getElementById("bestSubjectHighlight").textContent = data.best_subject;
    document.getElementById("shsStrandHighlight").textContent = data.model_input.shs_strand;
    document.getElementById("hollandCodeHighlight").textContent = data.holland_code;
    document.getElementById("scctSeHighlight").textContent = toFixedText(data.scct_averages.scct_se);
    document.getElementById("scctOeHighlight").textContent = toFixedText(data.scct_averages.scct_oe);
    document.getElementById("scctBHighlight").textContent = toFixedText(data.scct_averages.scct_b);
    document.getElementById("bestCareerHighlight").textContent = data.best_career;
    document.getElementById("bestCourseHighlight").textContent = data.best_course;
    document.getElementById("predictionConfidenceHighlight").textContent = toPercent(
        data.prediction_confidence
    );

    const top1Accuracy =
        top1Metrics.accuracy !== undefined ? top1Metrics.accuracy : data.model_accuracy;
    const top3Accuracy = top3Metrics.accuracy;

    const confidenceGap = computeConfidenceGap(data.top_predictions);
    const confidenceLevel = classifyConfidenceLevel(data.prediction_confidence, confidenceGap);

    localTop1HitRate.textContent = toPercent(top1Accuracy);
    localTop3HitRate.textContent = toPercent(top3Accuracy);

    confidenceGapHighlight.textContent = toPercent(confidenceGap);
    confidenceLevelHighlight.textContent = confidenceLevel.label;
    confidenceLevelHighlight.classList.remove(
        "confidence-level-high",
        "confidence-level-medium",
        "confidence-level-low",
        "confidence-level-unknown"
    );
    confidenceLevelHighlight.classList.add(confidenceLevel.cssClass);

    document.getElementById("top1Accuracy").textContent = toPercent(top1Accuracy);
    document.getElementById("top1Recall").textContent = toPercent(top1Metrics.recall);
    document.getElementById("top1F1Score").textContent = toPercent(top1Metrics.f1_score);
    document.getElementById("top1Precision").textContent = toPercent(top1Metrics.precision);

    document.getElementById("top3Accuracy").textContent = toPercent(top3Accuracy);
    document.getElementById("top3Recall").textContent = toPercent(top3Metrics.recall);
    document.getElementById("top3F1Score").textContent = toPercent(top3Metrics.f1_score);
    document.getElementById("top3Precision").textContent = toPercent(top3Metrics.precision);

    if (isLocalSummary) {
        top1ExplanationText.textContent = `Top-1 summary is dynamic for this user profile. It uses the most similar test-set neighbors (${localSampleSize}/${localPoolSize}) and reports how often a matching profile's true label was captured at rank #1. Current local Top-1 hit rate is ${toPercent(
            top1Accuracy
        )}, with average profile similarity ${toPercent(localAverageSimilarity)}.`;
        top3ExplanationText.textContent = `Top-3 summary is also dynamic for this user profile. Using the same neighborhood (${localSampleSize}/${localPoolSize}), metrics are computed from top-k confusion logic: a hit contributes one true positive, while each non-true recommended label contributes false positives. Local Top-3 hit rate is ${toPercent(
            top3Metrics.accuracy
        )}, with precision/recall/F1 shown from that confusion view.`;
    } else {
        top1ExplanationText.textContent = `Top-1 summary uses exact first-choice matching on the test set. Accuracy ${toPercent(
            top1Accuracy
        )} means only the #1 predicted career-course pair is counted as correct. Weighted recall, F1-score, and precision are influenced by class frequency, so common labels affect these values more.`;
        top3ExplanationText.textContent = `Top-3 summary uses ranked hit logic with top-k confusion accounting. Accuracy ${toPercent(
            top3Metrics.accuracy
        )} counts a hit when the true label appears in the top 3, while precision/recall/F1 are derived from top-k true/false positives and false negatives.`;
    }
    applyExplanationToggleState();

    renderTopPredictions(data.top_predictions);

    const featureSummaryItems = [
        `Math Avg: ${toFixedText(data.subject_averages.Math)}`,
        `English Avg: ${toFixedText(data.subject_averages.English)}`,
        `Science Avg: ${toFixedText(data.subject_averages.Science)}`,
        `Model Input SCCT-SE (clamped): ${data.model_input.scct_se}`,
        `Model Input SCCT-OE (clamped): ${data.model_input.scct_oe}`,
        `Model Input SCCT-B (clamped): ${data.model_input.scct_b}`,
        `Confidence Gap (#1 - #2): ${toPercent(confidenceGap)}`,
        `Confidence Level: ${confidenceLevel.label} (High >= 50% and gap >= 10%; Medium >= 30% and gap >= 5%)`,
        `${isLocalSummary ? "Top-1 Local Hit Rate" : "Top-1 Model Accuracy"}: ${toPercent(top1Accuracy)}`,
    ];

    if (isLocalSummary) {
        featureSummaryItems.push(`Neighborhood Evidence Size: ${localSampleSize}/${localPoolSize}`);
        featureSummaryItems.push(`Neighborhood Avg Similarity: ${toPercent(localAverageSimilarity)}`);
        featureSummaryItems.push(
            `Global Top-1 Baseline: ${toPercent(globalTop1Metrics.accuracy)}`
        );
    }

    if (activeResultView === RESULT_VIEW_TOP3) {
        featureSummaryItems.push(
            `${isLocalSummary ? "Top-3 Local Hit Rate" : "Top-3 Model Accuracy"}: ${toPercent(
                top3Accuracy
            )}`
        );
        if (isLocalSummary) {
            featureSummaryItems.push(`Global Top-3 Baseline: ${toPercent(globalTop3Metrics.accuracy)}`);
        }
    }

    setResultList("featureSummary", featureSummaryItems);

    setResultList(
        "riasecSummary",
        Object.entries(data.riasec_scores)
        .sort((a, b) => b[1] - a[1])
        .map(([code, score]) => `${code}: ${score}`)
    );

    resultCard.classList.remove("hidden");
    if (shouldScroll) {
        resultCard.scrollIntoView({ behavior: "smooth", block: "start" });
    }
}

viewTop1Btn.addEventListener("click", () => {
    setResultViewMode(RESULT_VIEW_TOP1);
});

viewTop3Btn.addEventListener("click", () => {
    setResultViewMode(RESULT_VIEW_TOP3);
});

toggleTop1ExplanationBtn.addEventListener("click", () => {
    toggleModelSummaryExplanation(RESULT_VIEW_TOP1);
});

toggleTop3ExplanationBtn.addEventListener("click", () => {
    toggleModelSummaryExplanation(RESULT_VIEW_TOP3);
});

toggleDetailsBtn.addEventListener("click", () => {
    toggleDetailsVisibility();
});

nextBtn.addEventListener("click", () => {
    try {
        goNextScreen();
    } catch (error) {
        statusMessage.textContent = error.message;
        statusMessage.classList.add("error");
    }
});

prevBtn.addEventListener("click", () => {
    goPreviousScreen();
});

predictForm.addEventListener("submit", async(event) => {
    event.preventDefault();

    submitBtn.disabled = true;
    statusMessage.textContent = "Computing prediction...";
    statusMessage.classList.remove("error");

    try {
        validateAcademicStep();

        const payload = {
            grades: readGrades(),
            shs_strand: document.getElementById("shsStrand").value,
            riasec_answers: readRiasecAnswers(),
            scct_answers: readScctAnswers(),
        };

        const response = await fetch("/api/predict", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify(payload),
        });

        const data = await response.json();
        if (!response.ok) {
            throw new Error(data.error || "Prediction failed.");
        }

        renderResult(data);
        statusMessage.textContent = "Prediction complete.";
    } catch (error) {
        statusMessage.textContent = error.message;
        statusMessage.classList.add("error");
    } finally {
        submitBtn.disabled = false;
    }
});

(async function init() {
    createGradeInputs();
    applyResultViewMode();
    applyExplanationToggleState();
    applyDetailsToggleState();
    renderWizardStep();
    try {
        await loadQuestions();
    } catch (error) {
        statusMessage.textContent = error.message;
        statusMessage.classList.add("error");
    }
})();