const fs = require('fs');
const path = require('path');

const htmlPath = path.join(__dirname, '../docs/index.html');
const html = fs.readFileSync(htmlPath, 'utf8');

// Check for positive guard OR negative early return guard
const positiveGuard = 'if (MasterBlueprint.featureFlags.enableDebugPanel) console[level]';
const negativeGuard = 'if (!MasterBlueprint.featureFlags.enableDebugPanel) return;';

if (html.includes(positiveGuard) || html.includes(negativeGuard)) {
    console.log('✅ [PASS] Logger correctly checks feature flag before console output.');
    process.exit(0);
} else {
    console.error('❌ [FAIL] Logger does not check feature flag.');
    console.error('Expected one of:');
    console.error(`  - ${positiveGuard}`);
    console.error(`  - ${negativeGuard}`);
    process.exit(1);
}
