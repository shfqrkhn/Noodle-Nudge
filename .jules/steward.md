## 2026-01-25 - Sentinel - jsDelivr SRI Incompatibility
**Insight:** jsDelivr dynamically generates minified files (adding headers) for packages that lack them (e.g., Chart.js UMD). These headers warn against using SRI because the file content (and hash) may change.
**Protocol:** When adding SRI to jsDelivr links, ensure the target file is a static asset from the npm package (often unminified) rather than a dynamically generated one.
