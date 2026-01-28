const { performance } = require('perf_hooks');

const reIdentifiers = /[a-zA-Z_][\w]*/g;
const reScoreSuffix = /([a-zA-Z_][\w]*)_score\b/g;

// Mock ruleMap (using Set to simulate .has() check)
const ruleMap = new Set(['extraversion', 'agreeableness', 'conscientiousness', 'neuroticism', 'openness']);

const calculations = [
    "SUM_AND_AVERAGE([ipip_e1, ipip_e3], REVERSE_SCORE([ipip_e2, ipip_e4]))",
    "NORMALIZE(openness_score, 1, 5, 0, 100)",
    "(0.4 * NORMALIZE(neuroticism_score, 1, 5, 0, 100)) + (0.4 * NORMALIZE(conscientiousness_score, 1, 5, 0, 100)) + (0.2 * (100 - NORMALIZE(agreeableness_score, 1, 5, 0, 100)))",
    "CONCAT( (extraversion_score > 3.0 ? 'E' : 'I'), (openness_score > 3.0 ? 'N' : 'S'), (agreeableness_score > 3.0 ? 'F' : 'T'), (conscientiousness_score > 3.0 ? 'J' : 'P') )"
];

function extractDependenciesOld(calc) {
    const matches = [...calc.matchAll(reIdentifiers)];
    const dependencies = [...new Set(matches.map(m => m[0]))]
        .filter(id => id.endsWith('_score') && ruleMap.has(id.replace('_score', '')));
    return dependencies;
}

function extractDependenciesNew(calc) {
    const matches = [...calc.matchAll(reScoreSuffix)];
    const dependencies = [...new Set(matches.map(m => m[0]))]
         .filter(id => ruleMap.has(id.replace('_score', '')));
    return dependencies;
}

const iterations = 100000;

console.log(`Running ${iterations} iterations over ${calculations.length} expressions...`);

// Warmup
for (let i = 0; i < 1000; i++) {
    for (const calc of calculations) extractDependenciesOld(calc);
    for (const calc of calculations) extractDependenciesNew(calc);
}

const startOld = performance.now();
for (let i = 0; i < iterations; i++) {
    for (const calc of calculations) {
        extractDependenciesOld(calc);
    }
}
const endOld = performance.now();
const timeOld = endOld - startOld;
console.log(`Old approach: ${timeOld.toFixed(2)} ms`);

const startNew = performance.now();
for (let i = 0; i < iterations; i++) {
    for (const calc of calculations) {
        extractDependenciesNew(calc);
    }
}
const endNew = performance.now();
const timeNew = endNew - startNew;
console.log(`New approach: ${timeNew.toFixed(2)} ms`);

const improvement = ((timeOld - timeNew) / timeOld) * 100;
console.log(`Improvement: ${improvement.toFixed(2)}%`);

// Verification of correctness
const testCalc = "(0.4 * NORMALIZE(neuroticism_score, 1, 5, 0, 100))";
const oldDeps = extractDependenciesOld(testCalc);
const newDeps = extractDependenciesNew(testCalc);

console.log('\nCorrectness Check:');
console.log('Old:', oldDeps);
console.log('New:', newDeps);

if (JSON.stringify(oldDeps) === JSON.stringify(newDeps)) {
    console.log("✅ Results match.");
} else {
    console.error("❌ Results do not match!");
}
