## 2026-01-25 - Sentinel - jsDelivr SRI Incompatibility
**Insight:** jsDelivr dynamically generates minified files (adding headers) for packages that lack them (e.g., Chart.js UMD). These headers warn against using SRI because the file content (and hash) may change.
**Protocol:** When adding SRI to jsDelivr links, ensure the target file is a static asset from the npm package (often unminified) rather than a dynamically generated one.

## 2026-01-25 - Sentinel - Unsafe Eval with External Content
**Insight:** The scoring engine used `new Function` to evaluate expressions defined in external JSON files. This creates a Critical Injection Risk (XSS/RCE) if the content source is compromised.
**Protocol:** When dynamic evaluation is strictly necessary for content logic, input MUST be sanitized against a strict Allowlist of identifiers and SAFE operators/characters before execution.

## 2026-01-25 - Bolt - Service Worker Cache Key Mismatch
**Insight:** The Service Worker cached content using `refs/heads/main` URLs, while the app requested content using `main` URLs. This caused a complete cache miss, redundant network requests, and broke offline functionality because the cache keys (URL strings) did not match.
**Protocol:** Use relative paths (e.g., `./JSON/`) for all local content resources in both the application logic and the Service Worker configuration to ensure consistency and portability.

## 2026-01-25 - Sentinel - Default Debug Mode Exposure
**Insight:** The application had the Debug Panel enabled by default in production (`enableDebugPanel: true`), exposing internal logs and state management tools to end-users.
**Protocol:** Feature flags for debugging/admin tools must default to `false` and require explicit activation (e.g., URL parameters or auth) to adhere to the Principle of Least Privilege.

## 2026-01-25 - Bolt - Redundant IndexedDB Serialization
**Insight:** The application serialized and wrote the entire state to IndexedDB on every `State.set` call. Separate calls for related data (e.g., `userAnswers` and `userResults`) doubled the I/O overhead.
**Protocol:** Batch related state updates into a single `State.set` transaction to minimize serialization cost and database write operations.

## 2026-01-25 - Sentinel - Mutable Global Configuration
**Insight:** While scoped to a module, the `MasterBlueprint` configuration object (containing feature flags and endpoints) was mutable. Internal code could accidentally modify critical settings at runtime.
**Protocol:** Critical configuration objects must be deeply frozen (`Object.freeze`) immediately upon definition to guarantee immutability and integrity throughout the application lifecycle.

## 2026-01-25 - Bolt - Async Loader & Reactive State
**Insight:** A simple PubSub implementation using `Set.forEach` can cause infinite loops if a subscriber removes itself and adds a new subscriber synchronously during the callback execution (e.g., a View that re-renders and re-subscribes).
**Protocol:** Always iterate over a copy of the subscribers set (`[...subscribers].forEach`) when dispatching events.

## 2026-01-25 - Bolt - Cache Busting
**Insight:** Offline-first PWAs with Cache-First strategies require explicit version bumping in `service-worker.js` to trigger updates for cached assets (like `index.html`).
**Protocol:** When modifying core files cached by the Service Worker, always increment `CACHE_NAME` in `service-worker.js` and synchronize the version in `index.html` and `README.md`.

## 2026-02-06 - Razor - Temporary Artifacts
**Insight:** Temporary automation scripts and verification artifacts were inadvertently proposed for commit.
**Protocol:** All temporary scripts and artifacts generated during the verification process must be deleted before submission to maintain repository hygiene.

## 2026-02-11 - Sentinel - Constructor Vulnerability
**Insight:** The expression engine allowed access to the `Function` constructor via `"".constructor.constructor` or `Reflect.construct(Function, ...)`, enabling arbitrary code execution despite regex filters.
**Protocol:** Explicitly ban `constructor`, `prototype`, `__proto__`, `arguments`, `callee` in `reSecurity` and shadow `Reflect`, `Proxy`, `Function`, `Object` in `evaluateExpression`.

## 2026-02-12 - Sentinel - UI Component XSS Sinks
**Insight:** The generic `showToast` utility injected the message argument via `innerHTML`, creating an XSS vulnerability when displaying errors or dynamic content.
**Protocol:** All generic UI utilities accepting string content must default to `textContent` or explicitly sanitize input (e.g., via `sanitizeHTML`) before insertion into the DOM.

## 2026-02-13 - Sync - Auxiliary Documentation Drift
**Insight:** Development guides (like CLAUDE.md) can drift from the actual codebase version, leading to confusion about the current state of the application.
**Protocol:** When bumping versions, grep for the old version string across the ENTIRE repository (including docs/guides) to ensure no file is left behind.

## 2026-02-18 - Sentinel - Import Data Type Confusion
**Insight:** `JSON.parse` is not enough to validate imported data structure. Loose typing allowed a string value for `userAnswers` to corrupt the application state, leading to runtime errors.
**Protocol:** When importing complex state from external sources (JSON), explicitly validate that all root keys correspond to their expected types (e.g., `isObject(data.userAnswers)`) before persistence.
