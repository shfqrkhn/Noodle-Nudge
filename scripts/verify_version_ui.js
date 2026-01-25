const fs = require('fs');
const path = require('path');

const htmlPath = path.join(__dirname, '../docs/index.html');
const html = fs.readFileSync(htmlPath, 'utf8');

let passed = true;

// Check Footer HTML
if (html.includes('<footer class="container text-center mt-5 mb-3 text-muted"><small>Noodle Nudge v<span id="app-version"></span></small></footer>')) {
    console.log('✅ [PASS] Footer element present.');
} else {
    console.error('❌ [FAIL] Footer element missing.');
    passed = false;
}

// Check JS Logic
if (html.includes('const vEl = document.getElementById("app-version"); if(vEl) vEl.textContent = MasterBlueprint.version;')) {
    console.log('✅ [PASS] Version population logic present.');
} else {
    console.error('❌ [FAIL] Version population logic missing.');
    passed = false;
}

if (!passed) process.exit(1);
