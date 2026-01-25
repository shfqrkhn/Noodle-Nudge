const fs = require('fs');
const path = require('path');

const htmlPath = path.join(__dirname, '../docs/index.html');
const html = fs.readFileSync(htmlPath, 'utf8');

let passed = true;

// Check Prev Day Button
// We look for the source code string
const prevBtnRegex = /<button[^>]*data-action="prev-day"[^>]*>/;
const prevMatch = html.match(prevBtnRegex);

if (prevMatch) {
    if (prevMatch[0].includes('aria-label="Previous Day"')) {
        console.log('✅ [PASS] Previous Day button has aria-label.');
    } else {
        console.error('❌ [FAIL] Previous Day button missing aria-label.');
        passed = false;
    }
} else {
    console.error('❌ [FAIL] Previous Day button not found in source.');
    passed = false;
}

// Check Next Day Button
const nextBtnRegex = /<button[^>]*data-action="next-day"[^>]*>/;
const nextMatch = html.match(nextBtnRegex);

if (nextMatch) {
    if (nextMatch[0].includes('aria-label="Next Day"')) {
        console.log('✅ [PASS] Next Day button has aria-label.');
    } else {
        console.error('❌ [FAIL] Next Day button missing aria-label.');
        passed = false;
    }
} else {
    console.error('❌ [FAIL] Next Day button not found in source.');
    passed = false;
}

// Check for aria-current logic
if (html.includes("setAttribute('aria-current','page')") || html.includes('setAttribute("aria-current","page")') || html.includes("setAttribute('aria-current', 'page')")) {
    console.log('✅ [PASS] Navigation update logic includes aria-current setting.');
} else {
    console.error('❌ [FAIL] Navigation update logic missing aria-current setting.');
    passed = false;
}

if (!passed) process.exit(1);
