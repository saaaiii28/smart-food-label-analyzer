/**
 * Smart Food Label Analyzer - Core Logic
 * 
 * Analyzes nutritional data based on Indian packaged food context.
 * Focuses on combinations (e.g., Sugar + Fat) and practical validation.
 */

const Analyzer = {

    /**
     * Thresholds based on general health guidelines (per 100g/100ml)
     * These can be calibrated with the Excel sheet data later.
     */
    THRESHOLDS: {
        SUGAR: { HIGH: 10, MODERATE: 5 },       // g
        SODIUM: { HIGH: 600, MODERATE: 300 },   // mg
        SAT_FAT: { HIGH: 5, MODERATE: 2 },      // g
        TRANS_FAT: { HIGH: 0.2 },               // g (Strict No)
        FIBER: { LOW: 3 },                      // g (Good to have > 3)
        ADDITIVES: { HIGH: 3 }                  // Count
    },

    /**
     * Analyze a product and return a full report.
     * @param {Object} product - The product object from data.js
     */
    analyzeProduct: function (product) {
        let score = 100;
        let warnings = [];
        let goodPoints = [];
        let criticalFlags = 0; // Counts red flags

        // --- 1. Sugar Analysis ---
        if (product.sugar_g > this.THRESHOLDS.SUGAR.HIGH) {
            score -= 30;
            warnings.push(`High Sugar (${product.sugar_g}g): Limits your daily intake.`);
            criticalFlags++;
        } else if (product.sugar_g > this.THRESHOLDS.SUGAR.MODERATE) {
            score -= 10;
            warnings.push(`Moderate Sugar (${product.sugar_g}g).`);
        } else {
            goodPoints.push("Low in Sugar.");
        }

        // --- 2. Salt/Sodium Analysis ---
        if (product.sodium_mg > this.THRESHOLDS.SODIUM.HIGH) {
            score -= 30;
            warnings.push(`High Sodium (${product.sodium_mg}mg): Bad for blood pressure.`);
            criticalFlags++;
        } else if (product.sodium_mg > this.THRESHOLDS.SODIUM.MODERATE) {
            score -= 10;
            warnings.push(`Moderate Sodium.`);
        }

        // --- 3. Fat Analysis ---
        if (product.sat_fat_g > this.THRESHOLDS.SAT_FAT.HIGH) {
            score -= 20;
            warnings.push(`High Saturated Fat (${product.sat_fat_g}g).`);
            criticalFlags++;
        }
        if (product.trans_fat_g > this.THRESHOLDS.TRANS_FAT.HIGH) {
            score -= 50; // Huge penalty
            warnings.push(`Contains Trans Fat (${product.trans_fat_g}g): Avoid if possible.`);
            criticalFlags += 2;
        }

        // --- 4. Additives & Processing ---
        if (product.additive_count > this.THRESHOLDS.ADDITIVES.HIGH) {
            score -= 15;
            warnings.push(`Highly Processed (${product.additive_count} additives).`);
        }
        if (product.refined_carb === 1) {
            score -= 10;
            warnings.push("Contains Refined Carbs (Maida/White Flour).");
        }

        // --- 5. Positive Boosts ---
        if (product.fiber_g > this.THRESHOLDS.FIBER.LOW) {
            score += 10;
            goodPoints.push("Good Source of Fiber.");
        }
        if (score < 40 && criticalFlags === 0) {
            // Boost score slightly if no critical flags but accumulated minor ones
            score += 10;
        }

        // --- 6. Combination Logic (The "Smart" Part) ---
        // High Sugar + High Fat = "Hyper-Palatable" (Addictive junk food)
        if (product.sugar_g > this.THRESHOLDS.SUGAR.HIGH && product.total_fat_g > 10) {
            score -= 10;
            warnings.push("⚠ High Sugar & Fat Combo: Calorie dense and addictive.");
        }

        // High Sodium + Refined Carbs (e.g., Chips, Instant Noodles)
        if (product.sodium_mg > 600 && product.refined_carb === 1) {
            score -= 10;
            warnings.push("⚠ Salty Refined Carb: Not filling, high craving risk.");
        }

        // Clamp Score
        score = Math.max(0, Math.min(100, score));

        // Find Alternative if score is low
        let alternative = null;
        if (score < 60 && product.better_alternative_id && typeof productsDB !== 'undefined') {
            alternative = productsDB.find(p => p.id === product.better_alternative_id);
        }

        return {
            score: score,
            trafficLight: this.getTrafficLight(score, criticalFlags),
            warnings: warnings,
            goodPoints: goodPoints,
            recommendation: this.getRecommendation(score, criticalFlags),
            // Nutrient Details for UI Bars
            nutrients: {
                sugar: { value: product.sugar_g, max: 15, label: 'Sugar', unit: 'g' },
                salt: { value: product.sodium_mg, max: 900, label: 'Sodium', unit: 'mg' },
                fat: { value: product.sat_fat_g, max: 10, label: 'Sat. Fat', unit: 'g' }
            },
            alternative: alternative
        };
    },

    /**
     * Determine Traffic Light Color
     */
    getTrafficLight: function (score, criticalFlags) {
        if (criticalFlags >= 3 || score < 40) return 'red';
        if (score < 75) return 'yellow';
        return 'green';
    },

    /**
     * Generate Actionable Advice
     */
    getRecommendation: function (score, criticalFlags) {
        if (score >= 75) return "Great choice! This seems healthy for regular consumption.";
        if (score >= 40) return "Okay generally, but consume in moderation due to identified ingredients.";
        return "Limit intake. Contains high levels of sugar, salt, or bad fats.";
    }
};

// Export
if (typeof window !== 'undefined') {
    window.Analyzer = Analyzer;
}
if (typeof module !== 'undefined') {
    module.exports = Analyzer;
}
