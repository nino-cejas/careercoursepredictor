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

const wizardState = {
    step: 0,
    riasecPage: 0,
    scctPage: 0,
};

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

function renderResult(data) {
    document.getElementById("bestCareer").textContent = data.best_career;
    document.getElementById("bestCourse").textContent = data.best_course;
    document.getElementById("modelAccuracy").textContent = `${(data.model_accuracy * 100).toFixed(2)}%`;
    document.getElementById("predictionConfidence").textContent = `${(data.prediction_confidence * 100).toFixed(2)}%`;

    setResultList("featureSummary", [
        `Best Subject: ${data.best_subject}`,
        `SHS Strand: ${data.model_input.shs_strand}`,
        `Holland Code (Top 3): ${data.holland_code}`,
        `Math Avg: ${data.subject_averages.Math}`,
        `English Avg: ${data.subject_averages.English}`,
        `Science Avg: ${data.subject_averages.Science}`,
        `SCCT-SE Avg: ${data.scct_averages.scct_se}`,
        `SCCT-OE Avg: ${data.scct_averages.scct_oe}`,
        `SCCT-B Avg: ${data.scct_averages.scct_b}`,
    ]);

    setResultList(
        "riasecSummary",
        Object.entries(data.riasec_scores)
        .sort((a, b) => b[1] - a[1])
        .map(([code, score]) => `${code}: ${score}`)
    );

    resultCard.classList.remove("hidden");
    resultCard.scrollIntoView({ behavior: "smooth", block: "start" });
}

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
    renderWizardStep();
    try {
        await loadQuestions();
    } catch (error) {
        statusMessage.textContent = error.message;
        statusMessage.classList.add("error");
    }
})();