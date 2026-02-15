# CLAUDE.md - Noodle Nudge Development Guide

## Project Overview

**Noodle Nudge** is a privacy-focused, offline-first Progressive Web App (PWA) for self-discovery and personal growth. It provides daily inspirational content (quotes, reflections, meditations, cognitive biases) and psychological assessments based on validated frameworks like the Big Five personality model.

**Current Version:** v1.2.10
**Live Demo:** https://shfqrkhn.github.io/Noodle-Nudge/
**License:** MIT

### Core Philosophy
- **Privacy First**: All data stays on-device via IndexedDB - no server-side storage
- **Offline First**: Full functionality without network connectivity after initial load
- **Open Source**: Free and open under MIT license

## Architecture

### Single-File Architecture
The entire application is contained in `docs/index.html` with inlined JavaScript modules. This design choice prioritizes:
- Simplified deployment to GitHub Pages
- Reduced HTTP requests for offline-first operation
- Self-contained PWA bundle

### Module System (NoodleNudge.*)
All modules are namespaced under the global `NoodleNudge` object:

| Module | Purpose |
|--------|---------|
| `NoodleNudge.Utils` | Utility functions (`getDayOfYear`, `sanitizeHTML`) |
| `NoodleNudge.L10N` | Localization/internationalization strings |
| `NoodleNudge.State` | Reactive state management with PubSub pattern |
| `NoodleNudge.Logger` | Debug logging (only active when `?debug` URL param present) |
| `NoodleNudge.DB` | IndexedDB wrapper for persistence |
| `NoodleNudge.Content` | Content fetching and loading |
| `NoodleNudge.Daily` | Daily content rotation based on day-of-year |
| `NoodleNudge.UI` | View rendering and UI components |
| `NoodleNudge.Scoring` | Assessment scoring engine with expression evaluation |
| `NoodleNudge.SettingsManager` | Data export/import/reset functionality |
| `NoodleNudge.App` | Main application router and initialization |

### Configuration Object
`MasterBlueprint` is the immutable configuration object containing:
- Feature flags
- Database configuration
- Content URLs
- State schema
- Localization strings

**Important:** MasterBlueprint is frozen (`Object.freeze`) to prevent runtime modification.

## Directory Structure

```
Noodle-Nudge/
├── docs/                      # GitHub Pages deployment directory
│   ├── index.html             # Main application (all JS inlined)
│   ├── service-worker.js      # PWA caching logic
│   ├── manifest.json          # PWA manifest
│   ├── favicon.ico
│   ├── icons/                 # PWA icons (192x192, 512x512)
│   └── JSON/                  # Content data files
│       ├── Q1_Core Personality.json    # Assessment definitions
│       ├── Q2_Core Values.json
│       ├── ...                         # Q3-Q10 assessments
│       ├── Content_Quotes.json         # Daily content
│       ├── Content_Reflections.json
│       ├── Content_Meditations.json
│       └── Content_CognitiveBiases.json
├── scripts/                   # Verification & benchmark scripts
│   ├── verify_*.py            # Playwright E2E verification tests
│   ├── benchmark_*.py         # Performance benchmarks
│   └── benchmark_*.js
├── verification/              # Test artifacts
├── .jules/                    # AI assistant memory/insights
│   └── steward.md
├── README.md
├── LICENSE
└── CLAUDE.md                  # This file
```

## Key Technical Details

### State Management
Custom reactive state with PubSub pattern:
```javascript
NoodleNudge.State.subscribe(callback)  // Subscribe to state changes
NoodleNudge.State.get()                // Get current state (shallow copy)
NoodleNudge.State.set(newState, opts)  // Merge new state
```

**Important:** State persistence happens automatically on `set()`. The `assessments` and `dailyContent` are excluded from persistence (loaded fresh from JSON).

### IndexedDB Storage
- Database: `NoodleNudgeDB`
- Store: `appState`
- Stored data: `userAnswers`, `userResults`, `appConfig`, `debugLog`

### Service Worker Strategy
- **Cache-First** strategy for offline functionality
- Cache name includes version: `noodle-nudge-cache-v1.2.9`
- All assets pre-cached on install

### Assessment Scoring Engine
The `NoodleNudge.Scoring` module implements a sophisticated expression evaluator:
- Supports functions: `SUM`, `SUM_AND_AVERAGE`, `AVERAGE_SCORE`, `NORMALIZE`, `CONCAT`, `IF`
- Card-sort specific: `COLLECT_ITEMS_FROM_CATEGORY`, `IDENTIFY_MAX_SCORE_DIMENSION`
- Uses topological sort for dependency resolution
- **Security:** Input sanitization against allowlist before `new Function` evaluation
- **Strict Regex:** Identifiers must not contain backslashes (no Unicode escapes) and globals are shadowed.

### Assessment Types
1. **Likert Scale** (`interactionType: 'likertScale'`): Standard questionnaires with 5-point scales
2. **Card Sort** (`interactionType: 'cardSort'`): Drag-and-drop card categorization

## Development Workflow

### Local Development
```bash
# Start local server (Python)
cd docs && python -m http.server 8000

# Or use Node's http-server
npx http-server docs -p 8000
```

Access at: http://localhost:8000/

### Debug Mode
Append `?debug` to URL to enable debug panel:
- http://localhost:8000/?debug

This reveals:
- Live state viewer
- Log viewer
- Test actions (force reload, fill random data, etc.)

### Running Verification Tests
Tests use Playwright for E2E verification:
```bash
# Install dependencies
pip install playwright
playwright install chromium

# Run with local server running on port 8000 (if needed by script)
python scripts/verify_scoring.py
python scripts/verify_xss.py
python scripts/verify_settings.py
python scripts/verify_sentinel_guard.py # Self-contained (starts own server)
python scripts/simulate_24_months.py    # Long-running simulation
```

### Version Bumping Protocol
When releasing a new version, update ALL of these locations:
1. `docs/index.html` - `MasterBlueprint.version`
2. `docs/index.html` - `MasterBlueprint.pwaConfig.cacheName`
3. `docs/service-worker.js` - `CACHE_NAME`
4. `README.md` - Version badge

## Code Conventions

### Security Requirements
1. **XSS Prevention**: Always use `NoodleNudge.Utils.sanitizeHTML()` when rendering user/JSON content
2. **Expression Evaluation**: The scoring engine validates inputs against allowlist before `new Function`
3. **No External Data Leakage**: Never send user data to external servers

### HTML Rendering
All dynamic content must be sanitized:
```javascript
// CORRECT
element.innerHTML = `<p>${NoodleNudge.Utils.sanitizeHTML(userInput)}</p>`;

// WRONG - XSS vulnerability
element.innerHTML = `<p>${userInput}</p>`;
```

### State Updates
Batch related updates in single `State.set()` call to minimize IndexedDB writes:
```javascript
// CORRECT - single write
NoodleNudge.State.set({ userAnswers: newAnswers, userResults: newResults });

// AVOID - two writes
NoodleNudge.State.set({ userAnswers: newAnswers });
NoodleNudge.State.set({ userResults: newResults });
```

### Subscriber Safety
When iterating subscribers, copy the set first:
```javascript
[...subscribers].forEach(cb => cb(state));  // Safe
subscribers.forEach(cb => cb(state));       // Can cause infinite loops
```

### CSS/Styling
- Bootstrap 5.3.3 via CDN
- Custom fonts: Merriweather (headings), Source Sans Pro (body)
- CSS custom properties defined in `:root`

## Assessment JSON Schema

Assessments follow this structure:
```json
{
  "id": "assessment_id_v1.0.0",
  "version": "1.0.0",
  "tier": "Tier 1|Tier 2",
  "title": "Display Title",
  "description": "Card description",
  "instructions": "Instructions shown during assessment",
  "interactionType": "likertScale|cardSort",
  "responseScale": [...],
  "questions": [...],
  "scoringRubric": {
    "primaryScores": [...],
    "derivativeInsights": [...]
  }
}
```

## Common Tasks

### Adding a New Assessment
1. Create JSON file in `docs/JSON/`
2. Add URL to `MasterBlueprint.contentUrls.assessments`
3. Add URL to `service-worker.js` CONTENT_URLS
4. Test scoring with `?debug` mode

### Adding Daily Content
1. Update appropriate JSON file in `docs/JSON/Content_*.json`
2. Ensure `day` property matches intended day-of-year (1-365)

### Modifying Scoring Logic
1. Edit `NoodleNudge.Scoring` module in `index.html`
2. Test with `scripts/verify_scoring.py`
3. Check for security implications if adding new expression functions

## Known Patterns & Learnings

From `.jules/steward.md`:

1. **jsDelivr SRI**: Use static npm assets for SRI hashes, not dynamically generated minified files
2. **Cache Keys**: Use relative paths (`./JSON/`) consistently between app and service worker
3. **Debug Mode**: Must default to `false` in production
4. **Configuration Immutability**: Always freeze critical config objects
5. **PubSub Safety**: Copy subscriber set before iteration

## External Dependencies (CDN)

| Library | Version | Purpose |
|---------|---------|---------|
| Bootstrap CSS | 5.3.3 | UI framework |
| Bootstrap JS | 5.3.3 | UI components |
| Chart.js | 4.4.2 | Radar charts for results |
| Google Fonts | - | Merriweather, Source Sans Pro |

## Testing Checklist

Before any release:
- [ ] `verify_scoring.py` - Assessment flow works
- [ ] `verify_xss.py` - XSS protection intact
- [ ] `verify_settings.py` - Data export/import/reset works
- [ ] `simulate_24_months.py` - Verify long-term stability
- [ ] Manual: Test offline mode (airplane mode)
- [ ] Manual: Test PWA install on mobile
- [ ] Version numbers synchronized across all files
