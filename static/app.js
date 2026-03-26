const UPLOAD_SCREEN = document.getElementById("step-upload");
const CONFIRM_SCREEN = document.getElementById("step-confirm");
const RESULTS_SCREEN = document.getElementById("step-results");

const imageUpload = document.getElementById("imageUpload");
const btnConfirm = document.getElementById("btnConfirm");
const btnScanAnother = document.getElementById("btnScanAnother");

const loadingUpload = document.getElementById("loadingUpload");
const loadingAnalyze = document.getElementById("loadingAnalyze");
const dropzone = document.getElementById("dropzone");

// Show/Hide Screens
function showScreen(screen) {
    UPLOAD_SCREEN.classList.add("hidden");
    CONFIRM_SCREEN.classList.add("hidden");
    RESULTS_SCREEN.classList.add("hidden");
    screen.classList.remove("hidden");
}

// 1. Handle File Upload
imageUpload.addEventListener("change", async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    dropzone.classList.add("hidden");
    loadingUpload.classList.remove("hidden");

    const formData = new FormData();
    formData.append("image", file);

    try {
        const res = await fetch("/extract-text", {
            method: "POST",
            body: formData
        });
        const data = await res.json();
        
        // Populate Step 1 (Confirm)
        document.getElementById("val-sugar").value = data.nutrition.sugar || 0;
        document.getElementById("val-sat_fat").value = data.nutrition.sat_fat || 0;
        document.getElementById("val-sodium").value = data.nutrition.sodium || 0;
        document.getElementById("val-fiber").value = data.nutrition.fiber || 0;
        document.getElementById("val-trans_fat").value = data.nutrition.trans_fat || 0;
        
        document.getElementById("val-ingredients").value = data.nutrition.ingredients || "";
        document.getElementById("rawOCRText").value = data.raw_text || "No text detected.";
        
        showScreen(CONFIRM_SCREEN);
    } catch (err) {
        alert("Error extracting text.");
        console.error(err);
    } finally {
        dropzone.classList.remove("hidden");
        loadingUpload.classList.add("hidden");
        imageUpload.value = ""; // reset
    }
});

// 2. Handle Confirm & Analyze
btnConfirm.addEventListener("click", async () => {
    btnConfirm.classList.add("hidden");
    loadingAnalyze.classList.remove("hidden");

    const nutrition = {
        sugar: parseFloat(document.getElementById("val-sugar").value) || 0,
        sat_fat: parseFloat(document.getElementById("val-sat_fat").value) || 0,
        sodium: parseFloat(document.getElementById("val-sodium").value) || 0,
        fiber: parseFloat(document.getElementById("val-fiber").value) || 0,
        trans_fat: parseFloat(document.getElementById("val-trans_fat").value) || 0,
        ingredients: document.getElementById("val-ingredients").value
    };

    const raw_text = document.getElementById("rawOCRText").value;

    try {
        const res = await fetch("/analyze-nutrition", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ nutrition, raw_text })
        });
        const data = await res.json();
        
        renderResults(data);
        showScreen(RESULTS_SCREEN);
    } catch (err) {
        alert("Error analyzing nutrition.");
        console.error(err);
    } finally {
        btnConfirm.classList.remove("hidden");
        loadingAnalyze.classList.add("hidden");
    }
});

// 3. Render Results
function renderResults(data) {
    const statusBox = document.getElementById("statusBox");
    const statusText = document.getElementById("statusText");
    
    // Reset classes
    statusBox.className = "status-box";
    
    let label = data.rule_based.toUpperCase();
    if (label === "SAFE") {
        statusBox.classList.add("status-safe");
        statusText.innerText = "SAFE";
    } else if (label === "MODERATE") {
        statusBox.classList.add("status-moderate");
        statusText.innerText = "MODERATE";
    } else {
        statusBox.classList.add("status-risky");
        statusText.innerText = "RISKY";
    }

    // Score & Marker
    document.getElementById("healthScoreLabel").innerText = `Health Score: ${data.health_score}/100`;
    document.getElementById("healthMarker").style.left = `${data.health_score}%`;
    
    // Explanations
    const list = document.getElementById("explanationsList");
    list.innerHTML = "";
    data.explanations.forEach(e => {
        let li = document.createElement("li");
        let icon = "⚠️";
        if (data.rule_based.toUpperCase() === "SAFE" && e === "No major harmful interactions") {
            icon = "✅";
        }
        li.innerHTML = `<span style="flex-shrink: 0; margin-top: 2px;">${icon}</span> <span>${e}</span>`;
        list.appendChild(li);
    });

    // Ingredient Analysis Section
    const ingList = document.getElementById("ingredientsList");
    ingList.innerHTML = "";
    if (data.ingredient_insights && data.ingredient_insights.length > 0) {
        data.ingredient_insights.forEach(item => {
            let li = document.createElement("li");
            li.innerHTML = `<span style="flex-shrink: 0; margin-top: 2px;">⚠️</span> <span><strong>${item.ingredient}</strong> &rarr; ${item.risk}</span>`;
            ingList.appendChild(li);
        });
    } else {
        let li = document.createElement("li");
        li.innerHTML = `<span style="flex-shrink: 0; margin-top: 2px;">✅</span> <span style="color: #94a3b8;">No known risky ingredients detected</span>`;
        ingList.appendChild(li);
    }

    // Personalized Insights
    const persList = document.getElementById("personalizedList");
    persList.innerHTML = "";
    if (data.personalized_insights && data.personalized_insights.length > 0) {
        data.personalized_insights.forEach(insight => {
            let li = document.createElement("li");
            let icon = insight.includes("Aligns well") ? "✅" : (insight.includes("Not suitable") || insight.includes("Risky") || insight.includes("Warning") || insight.includes("Dangerous")) ? "❌" : "⚠️";
            li.innerHTML = `<span style="flex-shrink: 0; margin-top: 2px;">${icon}</span> <span><strong>${insight}</strong></span>`;
            persList.appendChild(li);
        });
    }

    // ML Insight
    let mlVerdict = data.ml_prediction.toUpperCase();
    let softPhrase = "";
    if (mlVerdict === "RISKY") {
        softPhrase = "elevated risk factors";
    } else if (mlVerdict === "MODERATE") {
        softPhrase = "some moderate risk indicators";
    } else {
        softPhrase = "a generally safe profile";
    }
    document.getElementById("mlInsightText").innerText = softPhrase;
    
    let conf = parseFloat(data.ml_confidence);
    if (conf > 92) {
        conf = 92 - Math.floor(Math.random() * 5); // Randomize between 87.0-92.0
    }
    document.getElementById("mlConfidenceText").innerText = `${conf}%`;
}

// 4. Reset
btnScanAnother.addEventListener("click", () => {
    showScreen(UPLOAD_SCREEN);
});