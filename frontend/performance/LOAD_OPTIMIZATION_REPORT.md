# Frontend load optimization — 29 October 2026

The final production landing page meets the 600 ms target in the local desktop measurements. The reported 1284 ms was not reproduced: the production baseline was already below 600 ms. These results establish a measured improvement from that baseline, not a verified reduction from 1284 ms. Throttled mobile LCP remains above 600 ms.

## Chrome DevTools measurements

Medians of five independent tab navigations, using the same Chrome DevTools Protocol measurement script before and after:

| Metric | Before | After |
| --- | ---: | ---: |
| Navigation load event (`loadEventEnd`) | 179.2 ms | 51.0 ms |
| First Contentful Paint (FCP) | 364 ms | 240 ms |
| Largest Contentful Paint (LCP) | 364 ms | 240 ms |
| Initially requested JavaScript, decoded | 422,942 bytes | 292,541 bytes |
| Initial JavaScript, sum of individually gzipped files | 135,339 bytes | 93,248 bytes |
| Local application CSS, decoded | 235,251 bytes | 266,255 bytes |
| All blocking stylesheets, including external font CSS | 277,507 bytes | 266,255 bytes |
| Script execution during observation | 75.5 ms | 30.6 ms |
| Layout duration during observation | 141.8 ms | 104.6 ms |
| Main-thread task duration during observation | 392.1 ms | 216.1 ms |
| Style recalculations during observation | 62 | 38 |
| Sum of long-task durations during observation | 97 ms | 104 ms |

Initial JavaScript decreased by **30.8%**. CSS now contains the original font-face declarations, so the local stylesheet grew; eliminating the separate Google Fonts stylesheet reduced the combined blocking stylesheet payload by 11,252 bytes. The long-task total did not improve in this sample, even though total script and main-thread time decreased.

| Run | Before load | After load | Before FCP/LCP | After FCP/LCP |
| --- | ---: | ---: | ---: | ---: |
| 1 | 309.0 ms | 206.5 ms | 556 ms | 240 ms |
| 2 | 165.4 ms | 51.2 ms | 364 ms | 208 ms |
| 3 | 199.1 ms | 49.1 ms | 356 ms | 244 ms |
| 4 | 171.5 ms | 51.0 ms | 344 ms | 244 ms |
| 5 | 179.2 ms | 48.4 ms | 364 ms | 232 ms |

Conditions: Chrome 156.0.8078.73, Windows, headless isolated profile; production Vite preview at `http://127.0.0.1:4173/`; desktop 1440 × 900 at device scale 1; browser cache cleared and disabled each run; service workers bypassed; no network or CPU throttling. Each navigation used a fresh tab and observed LCP for two seconds after load without input or scrolling. Connections, OS caches, browser font caches, and host load can still vary. Timing measurements did not enable tracing or precise coverage.

The load event can occur before React paints. FCP and LCP therefore provide additional evidence of visible readiness. Gzip sizes are computed from the emitted files, not assumed wire-transfer totals.

Evidence: [raw before timings](results/load-before.json), [raw after timings](results/load-after.json), [combined summary](results/load-summary.json), [before trace](results/load-before-trace.json), [after trace](results/load-after-trace.json). Import the trace JSON files into Chrome DevTools' Performance panel; coverage results are saved alongside them.

## Lighthouse

Lighthouse 13.6.0, one performance audit for each configuration and build. These are simulated lab results, reported separately from the five-run unthrottled navigation measurements.

| Metric | Desktop before | Desktop after | Mobile before | Mobile after |
| --- | ---: | ---: | ---: | ---: |
| Performance score | 100 | 100 | 93 | 98 |
| FCP | 480 ms | 246 ms | 2173 ms | 916 ms |
| LCP | 480 ms | 246 ms | 2173 ms | 916 ms |
| Total Blocking Time | 0 ms | 0 ms | 222 ms | 180 ms |
| Cumulative Layout Shift | 0.00098 | 0 | 0.02183 | 0 |

The desktop preset uses simulated 40 ms RTT, 10,240 Kbps throughput and no CPU slowdown. Mobile uses Lighthouse's default simulated mobile settings: 150 ms RTT, 1,638.4 Kbps throughput and 4× CPU slowdown. Exact settings and warnings are retained in each JSON audit. No audit reported run warnings.

The mobile result **does not meet 600 ms**. No claim is made for production hosting, arbitrary devices or networks, or field Core Web Vitals.

Audits: [desktop before](results/load-before-lighthouse-desktop.json), [desktop after](results/load-after-lighthouse-desktop.json), [mobile before](results/load-before-lighthouse-mobile.json), [mobile after](results/load-after-lighthouse-mobile.json).

## Profiling findings and implementation

- The existing application already lazy-loads public information, login, workspace and admin routes. It already defers lower landing sections and secondary preview panels, and initializes authentication only on session routes. Those boundaries were preserved and verified; they were not newly introduced in this change. Vite retains its automatic [async chunk and CSS loading](https://vite.dev/guide/features#css-code-splitting).
- The landing page still eagerly imported Motion for simple entrance animations, button hover effects, response feedback and scroll parallax. Removing those imports moved the approximately 122 KB Motion chunk out of the initial network waterfall. Motion remains available to deferred components and other routes.
- Hero entrance timings, offsets and easing are now CSS animations. Scenario hover/press feedback uses CSS transitions; the response fade uses the browser's Web Animations API. The headline remains visible on its first render.
- Parallax keeps the existing 80 px / −60 px ambient movements, 32 px preview movement and 1–1.1 glow scale. A passive scroll listener schedules one animation frame and writes transforms directly to the affected elements. Geometry is measured on size changes, not during scroll callbacks; scroll does not set React state. Effects and animations clean up on unmount and respect reduced motion.
- The Google Fonts stylesheet was a separate blocking cross-origin dependency. The same WOFF2 font files now ship under `public/fonts/`, with their OFL licenses. `font-display: swap`, original subsets and individual weight declarations are retained. Only the two critical Latin heading/body fonts are preloaded; remaining faces load when used. This follows the [font-loading guidance](https://web.dev/articles/font-best-practices) while preserving typography. An experimental consolidation of weight declarations was discarded after raster comparisons showed changed intermediate weights.
- Tailwind's automatic source discovery is restricted to application sources and the HTML entry, preventing performance artifacts or other workspace files from becoming utility sources. This did not produce a material CSS-size reduction in the final build.
- Removed the unused `clsx` and `tailwind-merge` dependencies and updated the lockfile. They were already absent from the emitted entry, so their removal is not credited with the measured bundle reduction.
- The initial page already uses small WebP logo assets; no initial PNG requests were observed. These assets and their existing dimensions were retained. Large PNGs emitted for other lazy routes do not appear in the landing network waterfall.
- Initial landing requests contain no API calls, including with a saved token. Authentication checks, protected-route redirects, backend calls and Markdown functionality remain on their existing routes.

## Validation

- Production TypeScript check and Vite build passed.
- All 21 existing frontend unit tests passed.
- All 52 existing browser checks passed: preview panel selection/filtering/state, scenarios, clipboard contents, Send Query, FAQ anchors/accordion, About behavior, lazy public pages, login styling, protected routing, admin login, mobile access and absence of landing API calls.
- Nine additional browser checks passed for initial resource boundaries, local fonts, entrance completion, scroll parallax, reduced motion, response feedback and mobile sign-in navigation.
- Sampled component geometry, typography, colors, borders and gaps matched the retained before-build at widths 1440, 768 and 390 px, within a 1 px geometry tolerance. Screenshots were captured for each build and width. This is a sampled comparison, not an exhaustive pixel-equivalence claim.
- Rasterized font comparisons cover Manrope, DM Sans and JetBrains Mono at weights 400, 550, 650 and 750 against the original Google font-face definitions.
- No live login, authenticated RAG query, ingestion or database mutation was performed. Frontend auth redirects were tested; backend integration behavior was outside the local performance run.

Evidence: [functional checks](results/functional-checks.json), [animation and mobile navigation checks](results/load-animation-checks.json), [layout comparison](results/load-layout-comparison.json), [font comparisons](results/load-font-parity.json), [desktop before](results/load-layout-before-1440.png), [desktop after](results/load-layout-after-1440.png), [mobile before](results/load-layout-before-390.png), [mobile after](results/load-layout-after-390.png).

## Remaining bottlenecks

The shared stylesheet is still approximately 266 KB decoded and remains render-blocking. It includes global rules for other pages. Further CSS extraction requires preserving the existing responsive and dark-mode cascade; it was not removed indiscriminately. React, React DOM, routing, icons and the interactive hero preview still require approximately 293 KB of initial JavaScript. The final diagnostic trace contains a roughly 105 ms layout event, and throttled mobile still reports 180 ms of Total Blocking Time. These are the main remaining frontend costs.

The WebP logos still have some image-size savings identified by Lighthouse, but they are already small and are not the LCP element. Server TTFB, production compression/cache headers, CDN behavior and geographic latency require measurements against the deployed host. Meeting a universal 600 ms target would require specifying the device/network budget and potentially a larger rendering/CSS architecture change.

## Reproduce

From `frontend`, run `npm run build`, then keep `npm run preview -- --host 127.0.0.1 --port 4173 --strictPort` running. Launch a separate headless Chrome with remote debugging on port 9222 and a dedicated profile, as described in the existing performance report.

```powershell
node scripts/performance/measure.mjs repeat-load 5
node scripts/performance/diagnose.mjs repeat-load
node scripts/performance/verify.mjs
node scripts/performance/verify-load-animations.mjs
```

Lighthouse was downloaded into the workspace's `.perf/npm-cache` as a diagnostic tool; it was not added as a project dependency:

```powershell
npm exec --offline --cache D:/Clyptus/SAP_BRIM/.perf/npm-cache -- lighthouse http://127.0.0.1:4173/ --port=9222 --only-categories=performance --preset=desktop --output=json --output-path=performance/results/repeat-lighthouse-desktop.json --quiet
```

Omit `--preset=desktop` for the mobile audit. Run audits and timing captures sequentially, without other browser tests in progress. For layout comparison, serve the retained before artifact on port 4174 and run `node scripts/performance/compare-load-layout.mjs`. The retained artifact is local at `.perf/load-before-dist` in the workspace root. `summarize-load.mjs` accepts that artifact directory as its argument to calculate before/after gzip totals.
