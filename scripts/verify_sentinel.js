const fs = require('fs');
const path = require('path');

const htmlPath = path.join(__dirname, '../docs/index.html');
const html = fs.readFileSync(htmlPath, 'utf8');

if (html.includes('if (MasterBlueprint.featureFlags.enableDebugPanel) console[level]')) {
    console.log('✅ [PASS] Logger correctly checks feature flag before console output.');
    process.exit(0);
} else {
    console.error('❌ [FAIL] Logger does not check feature flag.');
    process.exit(1);
}
