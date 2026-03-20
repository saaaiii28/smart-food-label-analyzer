document.addEventListener("DOMContentLoaded", function () {

    const productSelect = document.getElementById("productSelect");
    const resultSection = document.getElementById("resultSection");
    const loadingSection = document.getElementById("loadingSection");

    const scoreValue = document.getElementById("scoreValue");
    const healthText = document.getElementById("healthText");
    const healthMarker = document.getElementById("healthMarker");

    const warningsList = document.getElementById("warningsList");
    const goodPointsList = document.getElementById("goodPointsList");

    const scanAgainBtn = document.getElementById("scanAgainBtn");


    // ===============================
    // Handle File Upload (Preview Only)
    // ===============================
    const fileInput = document.getElementById("fileInput");
    const imagePreview = document.getElementById("imagePreview");
    const uploadSection = document.getElementById("uploadSection");
    const previewSection = document.getElementById("previewSection");

    fileInput.addEventListener("change", function (e) {
        const file = e.target.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = function (e) {
                imagePreview.src = e.target.result;
                uploadSection.classList.add("hidden");
                previewSection.classList.remove("hidden");
            };
            reader.readAsDataURL(file);
        }
    });

    // ===============================
    // Analyze Button Logic
    // ===============================
    const analyzeBtn = document.getElementById("analyzeBtn");

    analyzeBtn.addEventListener("click", function () {
        const selectedFood = productSelect.value;
        if (selectedFood) {
            analyzeProduct(selectedFood);
            // Hide preview, show result (or at least start the process)
            previewSection.classList.add("hidden");
            loadingSection.classList.remove("hidden");
        } else {
            alert("Please select a product from the simulation list first.");
        }
    });

    // ===============================
    // When Product Selected
    // ===============================
    productSelect.addEventListener("change", function () {
        const selectedFood = productSelect.value;
        if (selectedFood) {
            analyzeProduct(selectedFood);
        }
    });

    function analyzeProduct(foodName) {
        loadingSection.classList.remove("hidden");
        resultSection.classList.add("hidden");

        fetch("/analyze", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ food: foodName })
        })
            .then(response => response.json())
            .then(data => {

                loadingSection.classList.add("hidden");

                if (data.error) {
                    alert(data.error);
                    return;
                }

                updateUI(data);

            })
            .catch(error => {
                loadingSection.classList.add("hidden");
                console.error("Error:", error);
            });
    }


    // ===============================
    // Update UI Function
    // ===============================
    function updateUI(data) {

        scoreValue.innerText = data.health_score;

        healthText.innerText = "Risk Level: " + data.risk_label;

        moveHealthBar(data.health_score);

        // Clear old lists
        warningsList.innerHTML = "";
        goodPointsList.innerHTML = "";

        // Render Explanations from Backend
        if (data.explanations && data.explanations.length > 0) {
            data.explanations.forEach(function (text) {
                if (data.risk_label === "Safe") {
                    addGoodPoint(text);
                } else {
                    addWarning(text);
                }
            });
        } else {
            // Fallback if no explanations provided
            if (data.risk_label === "Risky") addWarning("High interaction risk detected.");
            if (data.risk_label === "Moderate") addWarning("Moderate nutritional concern.");
            if (data.risk_label === "Safe") addGoodPoint("Safety profile acceptable.");
        }

        resultSection.classList.remove("hidden");
    }


    // ===============================
    // Move Health Bar
    // ===============================
    function moveHealthBar(score) {

        const percentage = Math.max(0, Math.min(score, 100));

        healthMarker.style.left = percentage + "%";

        if (score < 40) {
            healthMarker.style.backgroundColor = "#e74c3c";
        } else if (score < 70) {
            healthMarker.style.backgroundColor = "#f1c40f";
        } else {
            healthMarker.style.backgroundColor = "#2ecc71";
        }
    }


    // ===============================
    // Helpers
    // ===============================
    function addWarning(text) {
        const li = document.createElement("li");
        li.innerText = text;
        warningsList.appendChild(li);
    }

    function addGoodPoint(text) {
        const li = document.createElement("li");
        li.innerText = text;
        goodPointsList.appendChild(li);
    }


    // ===============================
    // Scan Again
    // ===============================
    scanAgainBtn.addEventListener("click", function () {

        resultSection.classList.add("hidden");
        // Reset to initial state
        previewSection.classList.add("hidden");
        uploadSection.classList.remove("hidden");
        fileInput.value = "";
        imagePreview.src = "";

        scoreValue.innerText = "--";
        healthText.innerText = "Select a product to analyze.";
        healthMarker.style.left = "0%";

        warningsList.innerHTML = "";
        goodPointsList.innerHTML = "";

    });

});
