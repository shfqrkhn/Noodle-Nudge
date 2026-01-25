
const assert = require('assert');

// Mock helpers from the codebase
const helpers = {
    NORMALIZE: (val, min, max) => (val - min) / (max - min) * 100,
    CONCAT: (...args) => args.join(''),
    IF: (c, t, e) => c ? t : e,
    IS_IN_TOP_CATEGORY: () => false,
    COUNT_SUBTYPE_IN_TOP_CATEGORY: () => 0,
    COMPARE_SUBTYPE_COUNTS: () => 'personal',
    IDENTIFY_HIGHEST_SCORE_DIMENSIONS: () => '',
    SUM: () => 0,
    SUM_AND_AVERAGE: () => 0,
    AVERAGE_SCORE: () => 0,
    COLLECT_ITEMS_FROM_CATEGORY: () => '',
    IDENTIFY_MAX_SCORE_DIMENSION: () => ''
};

// The Function under test
const evaluateExpression = (expression) => {
    let processedExpr = expression;

    // Security Sanitization Logic (The Fix)
    const cleanExpr = processedExpr.replace(/["'](?:\\.|[^"'\\])*["']/g, '');
    const tokens = cleanExpr.match(/[a-zA-Z_$][\w$]*/g) || [];
    const allowed = new Set(['true', 'false', 'null', 'undefined', 'NaN', 'Infinity', ...Object.keys(helpers)]);
    const badChars = /[{};]/;

    if (badChars.test(cleanExpr)) {
        throw new Error("Security Violation: Objects/Blocks not allowed");
    }

    for (const t of tokens) {
        if (!allowed.has(t)) {
            throw new Error(`Security Violation: Unauthorized token '${t}'`);
        }
    }

    // If safe, we attempt execution (mocked)
    // In real code: return new Function(...)(...)
    return "SAFE";
};

const runTests = () => {
    console.log("Running Sentinel Verification Tests...");
    let passed = 0;
    let failed = 0;

    const test = (name, expr, shouldPass) => {
        try {
            evaluateExpression(expr);
            if (shouldPass) {
                console.log(`✅ [PASS] ${name}`);
                passed++;
            } else {
                console.error(`❌ [FAIL] ${name} - Expected failure but passed.`);
                failed++;
            }
        } catch (e) {
            if (!shouldPass) {
                console.log(`✅ [PASS] ${name} - Blocked as expected: ${e.message}`);
                passed++;
            } else {
                console.error(`❌ [FAIL] ${name} - Expected pass but failed: ${e.message}`);
                failed++;
            }
        }
    };

    // Valid Scenarios (from JSONs)
    test("Basic Math", "(0.4 * 50) + (0.4 * 60)", true);
    test("Helper Call", "NORMALIZE(50, 0, 100)", true);
    test("Complex Helper", "(0.4 * NORMALIZE(50, 1, 5, 0, 100)) + (0.2 * (100 - NORMALIZE(30, 1, 5, 0, 100)))", true);
    test("Ternary and Concat", "CONCAT((50 > 30 ? 'E' : 'I'), 'N')", true);
    test("Nested Helpers", "IF(true, NORMALIZE(10,0,100), 0)", true);
    test("Strings with spaces", "CONCAT('Hello World', '!')", true);

    // Invalid Scenarios (Attacks)
    test("IIFE", "(function(){ return 1; })()", false);
    test("Alert", "alert(1)", false);
    test("Object Access", "Object.keys(helpers)", false); // Object is not allowed
    test("Window Access", "window.location", false);
    test("Process Exit", "process.exit()", false);
    test("Assignment", "x = 5", false); // x is not allowed
    test("Block", "{ var x = 1; }", false); // {} banned
    test("Array Constructor exploit", "[].map.constructor('alert(1)')()", false); // map/constructor not allowed
    test("Math (Disallowed)", "Math.max(1, 2)", false); // Math removed from allowed list in my plan, let's confirm

    // Boundary Check: Math
    // In the script above I included 'Math' in allowed set?
    // Wait, in the plan I said I'd exclude it. Let's adjust the script to match the plan.
    // I will modify the allowed set inside the function to exclude Math if I want to enforce that.
    // For now, let's see if the script passes with Math allowed or not.
    // The previous tool call included 'Math' in the set.
    // "const allowed = new Set(['Math', ...])"
    // I should align with the decision. The decision was: "I will exclude Math from the allowlist to be strict."

    // I will update the file in the next step to remove 'Math' if this test fails (which it won't because I included it).
    // Let's assume for this test run that Math IS allowed, and then I'll decide.
    // Actually, I should edit the script to REMOVE Math to verify it fails.

    console.log(`\nTests Completed. Passed: ${passed}, Failed: ${failed}`);
    if (failed > 0) process.exit(1);
};

runTests();
