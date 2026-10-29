# Local production performance — 29 October 2026

The local production build meets the requested navigation-load target in all five final runs. Navigation load was already below 600 ms in the production baseline; the reported 1195 ms came from the development server at `http://localhost:5173/` and is not a comparable production baseline. The main measured improvement is earlier visible content.

| Metric, median of five runs | Before | After |
| --- | ---: | ---: |
| Navigation `loadEventEnd` | 163.8 ms | 156.6 ms |
| First Contentful Paint | 568 ms | 380 ms |
| Largest Contentful Paint | 1252 ms | 380 ms |
| Initial JavaScript resource bytes, decoded | 834,296 | 422,028 |
| Initial application CSS resource bytes, decoded | 241,373 | 231,543 |
| Image resource bytes during observation, decoded | 163,836 | 24,526 |
| Initial DOM elements | 970 | 275 |
| Layout duration during observation, median | 401 ms | 207 ms |

JavaScript fell by 49.4%. LCP fell by 69.6%. Resource totals include module-preload requests, not just resources whose initiator is `script`. Image totals include repeated favicon/image requests with the cache disabled. These are decoded resource sizes, not compressed network-transfer estimates.

## Conditions and raw measurements

Both builds were measured with the same script, using Chrome DevTools Protocol against actual Chrome on Windows. The baseline was captured before source changes. A copy of that production artifact was retained separately for the later layout comparison.

- Chrome `156.0.8078.73`, headless, isolated browser profile.
- Production: `npm run build`, served by Vite preview at `http://127.0.0.1:4173/`.
- Desktop viewport: 1440 × 900, device scale factor 1.
- Browser cache cleared and disabled for each navigation; service workers bypassed.
- No CPU or network throttling, no blocked resources, no mocked API responses.
- Five navigations, each in a fresh tab. No scrolling or clicking during timing.
- Native Navigation Timing, Paint Timing, and buffered LCP observers. Observation ends two seconds after the load event; LCP is the last candidate in that window.
- Timing runs did not enable tracing or precise coverage. The separate diagnostic trace is intentionally not used for before/after timing comparisons.
- External Google Fonts requests remained unchanged. Browser profile, DNS/connection state, host load, and external network timing can introduce normal run-to-run variance.

| Run | Before load | After load | Before FCP | After FCP | Before LCP | After LCP |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 268.4 | 212.5 | 848 | 504 | 1348 | 504 |
| 2 | 264.2 | 138.8 | 632 | 372 | 1300 | 372 |
| 3 | 141.8 | 156.6 | 476 | 380 | 1160 | 380 |
| 4 | 152.6 | 150.8 | 512 | 356 | 676 | 356 |
| 5 | 163.8 | 198.8 | 568 | 440 | 1252 | 440 |

All times are milliseconds. Final navigation load ranged from 138.8 to 212.5 ms; final FCP/LCP ranged from 356 to 504 ms. This verifies the target under these local conditions, not on arbitrary devices or networks. In a React SPA, the load event can precede the first React commit, so FCP and LCP are also reported rather than treating load-event timing as visible readiness.

Raw data: [before](results/baseline.json), [after](results/optimized.json), [Chrome trace](results/baseline-trace.json). The trace can be imported into Chrome DevTools' Performance panel. Instrumentation uses the [Chrome DevTools Protocol](https://chromedevtools.github.io/devtools-protocol/).

## Observed bottlenecks and changes

1. The landing entry eagerly imported authenticated, administrative, and shared-prompt pages. The initial network waterfall fetched Markdown even though the landing page does not render Markdown. Routes now load through React `lazy`/`Suspense`. Removing the previous manual vendor grouping also removed a transitive Motion → Markdown chunk dependency; the final browser check verifies that Markdown is absent from initial requests.
2. The baseline rendered 970 DOM elements, including all lower-page sections and three hidden resource panels. The trace showed large whole-document layout/style work, including layout forced from Motion callbacks. Lower sections now load when approaching the viewport or navigating to their hash anchors. Secondary panels load on first use and stay mounted afterward, preserving their state. The preview chatbot remains available immediately.
3. The hero heading started at opacity zero and waited for its entrance animation. It now renders visibly on its first frame. The final layout, colors, type, other entrance animations, and parallax remain intact. No heading or LCP content was hidden, removed, shrunk, or replaced to improve the metric.
4. Large PNG logos were decoded for very small display sizes. New proportionate WebP variants use lossless encoding after resizing; originals remain available for other uses. Brand image dimensions are explicit.
5. Authentication and Markdown styles were part of the blocking landing stylesheet. They now load with the corresponding lazy routes. Shared theme and public-page styles retain their existing cascade.
6. The global auth provider initialized even on public pages. It now wraps session routes only, preventing a saved token from causing a landing-page `/auth/me` request and eliminating unrelated auth-state updates from the public tree. The token initializer also no longer reads storage on every provider render.

The landing network checks confirm zero API requests both with and without a saved token. Opening the landing page therefore does not invoke backend RAG or database endpoints. Backend startup validation, database readiness checks, and RAG processing code were left intact; their lifecycle is independent of the static landing page.

## Validation and limits

- Production build passed.
- Existing automated API tests: 10 passed.
- Chrome browser assertions: [52 passed](results/functional-checks.json), no runtime exceptions. Checks cover all four sidebar panels, document filtering and preserved search state, selected-record synchronization, actual clipboard contents, all four scenarios, Send Query, FAQ and direct About hash navigation, FAQ interaction, lazy public routes, login styling, unauthenticated chat protection, admin login, mobile overflow/access, and absence of landing API calls with a saved token.
- Sampled top-of-page geometry, fonts, colors, backgrounds, and display values matched exactly at both desktop and 390 px mobile widths: [layout comparison](results/layout-comparison.json). Screenshots: [before](results/baseline.png), [after](results/optimized.png), [mobile before](results/baseline-mobile-top.png), [mobile after](results/optimized-mobile-top.png).
- Lint completed without errors for changed components; existing warnings remain in AuthContext, LoginPage, and ChatMessage.
- No live authenticated RAG query, database mutation, or document ingestion was run. The production backend was not needed for landing measurements; live backend behavior is outside this verification.
- Layout-shift totals in the initial observation remain small, but increased from approximately 0.0002 to 0.0012. The comparison does not claim zero CLS.

An experimental `content-visibility` change failed the anchor-navigation browser check and was removed before the final tests and measurements. The final implementation uses lazy loading without that change.

## Reproduce

From the frontend directory, with Node.js 22+ and Chrome installed:

```powershell
npm run build
npm run preview -- --host 127.0.0.1 --port 4173 --strictPort
```

Keep the preview server running. In another PowerShell terminal, start a separate headless Chrome profile (adjust the paths if needed):

```powershell
Start-Process -FilePath 'C:/Program Files/Google/Chrome/Application/chrome.exe' -ArgumentList '--headless=new','--remote-debugging-port=9222','--user-data-dir=D:/Clyptus/SAP_BRIM/.perf/chrome-profile','--no-first-run','--no-default-browser-check','about:blank' -WindowStyle Hidden
node scripts/performance/measure.mjs repeat 5
node scripts/performance/verify.mjs
```

The scripts use native Node WebSocket support and require no additional packages. Results are written to `performance/results/`; use a fresh label to preserve the captured baseline and optimized data. Optional diagnostic capture: `node scripts/performance/diagnose.mjs diagnostic`. Diagnostic coverage/tracing has overhead and must not replace the untraced timing comparison.
