/**
 * Smart Food Label Analyzer - Frontend Controller
 */

document.addEventListener('DOMContentLoaded', () => {
    // Elements
    const fileInput = document.getElementById('fileInput');
    const imagePreview = document.getElementById('imagePreview');
    const analyzeBtn = document.getElementById('analyzeBtn');
    const scanAgainBtn = document.getElementById('scanAgainBtn');
    const resetBtn = document.getElementById('resetBtn');
    const productSelect = document.getElementById('productSelect');

    // Sections
    const uploadSection = document.getElementById('uploadSection');
    const previewSection = document.getElementById('previewSection');
    const loadingSection = document.getElementById('loadingSection');
    const resultSection = document.getElementById('resultSection');

    // 1. Initialize Mock Data Dropdown
    if (typeof productsDB !== 'undefined') {
        productsDB.forEach((product, index) => {
            const option = document.createElement('option');
            option.value = product.id;
            option.textContent = product.product_name;
            if (index === 0) option.selected = true; // Default
            productSelect.appendChild(option);
        });
    }

    // 2. Handle File Upload
    fileInput.addEventListener('change', (e) => {
        const file = e.target.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = (e) => {
                imagePreview.src = e.target.result;
                uploadSection.classList.add('hidden');
                previewSection.classList.remove('hidden');
            };
            reader.readAsDataURL(file);
        }
    });

    // 3. Handle Remove Image
    resetBtn.addEventListener('click', () => {
        fileInput.value = '';
        imagePreview.src = '';
        uploadSection.classList.remove('hidden');
        previewSection.classList.add('hidden');
    });

    // 4. Handle Analyze Click
    analyzeBtn.addEventListener('click', () => {
        // Show Loading
        previewSection.classList.add('hidden');
        loadingSection.classList.remove('hidden');

        // Simulate Delay
        setTimeout(() => {
            loadingSection.classList.add('hidden');
            showResults();
        }, 1500);
    });

    // 5. Handle Scan Again
    scanAgainBtn.addEventListener('click', () => {
        resultSection.classList.add('hidden');
        uploadSection.classList.remove('hidden');
        fileInput.value = '';
        imagePreview.src = '';
    });

    // Core Logic
    function showResults() {
        const selectedId = productSelect.value;
        const product = productsDB.find(p => p.id === selectedId);

        if (!product) {
            alert("Error: No product data found for simulation.");
            return;
        }

        const result = Analyzer.analyzeProduct(product);

        // Update UI
        document.getElementById('scoreValue').textContent = result.score;
        document.getElementById('healthText').textContent = result.recommendation;

        const trafficLightEl = document.getElementById('trafficLight');
        trafficLightEl.className = `traffic-light ${result.trafficLight}`;

        // Lists
        const warningsList = document.getElementById('warningsList');
        warningsList.innerHTML = '';
        if (result.warnings.length > 0) {
            result.warnings.forEach(warn => {
                const li = document.createElement('li');
                li.textContent = `⚠️ ${warn}`;
                warningsList.appendChild(li);
            });
        } else {
            warningsList.innerHTML = '<li>✅ No major concerns.</li>';
        }

        const goodPointsList = document.getElementById('goodPointsList');
        goodPointsList.innerHTML = '';
        if (result.goodPoints.length > 0) {
            result.goodPoints.forEach(point => {
                const li = document.createElement('li');
                li.textContent = `✅ ${point}`;
                goodPointsList.appendChild(li);
            });
        } else {
            goodPointsList.innerHTML = '<li>-</li>';
        }

        resultSection.classList.remove('hidden');
    }
});
