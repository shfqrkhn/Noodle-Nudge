## 2026-01-25 - Sentinel - jsDelivr SRI Incompatibility
**Insight:** jsDelivr dynamically generates minified files (adding headers) for packages that lack them (e.g., Chart.js UMD). These headers warn against using SRI because the file content (and hash) may change.
**Protocol:** When adding SRI to jsDelivr links, ensure the target file is a static asset from the npm package (often unminified) rather than a dynamically generated one.

## 2026-01-25 - Sentinel - Unsafe Eval with External Content
**Insight:** The scoring engine used `new Function` to evaluate expressions defined in external JSON files. This creates a Critical Injection Risk (XSS/RCE) if the content source is compromised.
**Protocol:** When dynamic evaluation is strictly necessary for content logic, input MUST be sanitized against a strict Allowlist of identifiers and SAFE operators/characters before execution.

## 2026-01-25 - Bolt - Service Worker Cache Key Mismatch
**Insight:** The Service Worker cached content using `refs/heads/main` URLs, while the app requested content using `main` URLs. This caused a complete cache miss, redundant network requests, and broke offline functionality because the cache keys (URL strings) did not match.
**Protocol:** Use relative paths (e.g., `./JSON/`) for all local content resources in both the application logic and the Service Worker configuration to ensure consistency and portability.
