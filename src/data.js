// Mock Data mimicking the user's Excel sheet structure
// Columns: product_name, sugar_g, sodium_mg, total_fat_g, sat_fat_g, trans_fat_g, fiber_g, calories_kcal, refined_carb, caffeine, additive_count

const productsDB = [
    {
        id: "p1",
        product_name: "Generic Glucose Biscuits",
        sugar_g: 25,         // High
        sodium_mg: 300,      // Moderate
        total_fat_g: 15,
        sat_fat_g: 8,        // High
        trans_fat_g: 0.5,
        fiber_g: 1,
        calories_kcal: 450,
        refined_carb: 1,     // 1 = Yes, 0 = No
        caffeine: 0,
        additive_count: 2,
        better_alternative_id: "p3" // Oats/Multi-Grain
    },
    {
        id: "p2",
        product_name: "Instant Masala Noodles",
        sugar_g: 2,
        sodium_mg: 1200,     // Very High (Traffic Light Red)
        total_fat_g: 18,
        sat_fat_g: 9,        // High
        trans_fat_g: 0,
        fiber_g: 2,
        calories_kcal: 380,
        refined_carb: 1,
        caffeine: 0,
        additive_count: 5,    // High additives
        better_alternative_id: "p3" // Suggest Oats instead
    },
    {
        id: "p3",
        product_name: "Healthy Oats Multi-Grain",
        sugar_g: 3,          // Low
        sodium_mg: 50,       // Low
        total_fat_g: 6,
        sat_fat_g: 1,        // Low
        trans_fat_g: 0,
        fiber_g: 10,         // High
        calories_kcal: 360,
        refined_carb: 0,
        caffeine: 0,
        additive_count: 0
    },
    {
        id: "p4",
        product_name: "Cola Drink",
        sugar_g: 11,         // High (per 100ml usually, assuming 100g/ml basis)
        sodium_mg: 10,
        total_fat_g: 0,
        sat_fat_g: 0,
        trans_fat_g: 0,
        fiber_g: 0,
        calories_kcal: 45,
        refined_carb: 0,
        caffeine: 10,        // Present
        additive_count: 4,
        better_alternative_id: "filter_coffee" // Adding a dummy or we can add a new product
    },
    {
        id: "p5",
        product_name: "Spicy Potato Chips",
        sugar_g: 4,
        sodium_mg: 800,      // High
        total_fat_g: 35,     // Very High
        sat_fat_g: 15,       // Very High
        trans_fat_g: 0,
        fiber_g: 3,
        calories_kcal: 540,
        refined_carb: 1,
        caffeine: 0,
        additive_count: 3,
        better_alternative_id: "p6" // Roasted foxnuts (makhana) - need to add p6
    },
    {
        id: "p6", // New healthy snack
        product_name: "Roasted Makhana (Foxnuts)",
        sugar_g: 0,
        sodium_mg: 150,
        total_fat_g: 10,
        sat_fat_g: 1,
        trans_fat_g: 0,
        fiber_g: 5,
        calories_kcal: 350,
        refined_carb: 0,
        caffeine: 0,
        additive_count: 1
    }
];

// Export for use in other files if we were using modules, 
// but for simple vanilla JS inclusion, we just leave it in global scope or attach to window.
if (typeof window !== 'undefined') {
    window.productsDB = productsDB;
}

// For Node.js testing environment
if (typeof module !== 'undefined') {
    module.exports = productsDB;
}
