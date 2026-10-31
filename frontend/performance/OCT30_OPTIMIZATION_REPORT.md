# Clyptus.AI frontend optimization — 30 October 2026

The initial landing stylesheet is 16.5% smaller, and the three final-CTA labels have no grey dot separators. Workspace styles and non-critical landing styles now load with the routes or sections that need them. Features, theme, fonts, responsive layouts and animations are retained.

The reported **1,185 ms was not reproduced as the local baseline median**. The final production-build comparison was already below 600 ms before this change. The measurements verify local desktop readiness below 600 ms; they do not establish a reduction from 1,185 ms or verify deployed-host performance. Throttled mobile remains above 600 ms.

Seven cache-cleared desktop navigations per build, with tracing disabled during timing:

| Metric | Before | After |
| --- | ---: | ---: |
| Navigation load event, median | 65.7 ms | 62.4 ms |
| FCP, median | 296 ms | 284 ms |
| LCP, median | 296 ms | 284 ms |
| Initial JavaScript, decoded | 292,541 B | 292,654 B |
| Initial CSS, decoded | 266,255 B | 222,234 B |
| Initial JS + CSS bundle, decoded | 558,796 B | 514,888 B |
| Initial JavaScript, individually gzipped | 93,248 B | 93,278 B |
| Initial CSS, gzipped | 40,985 B | 33,398 B |
| Initial JS + CSS, individually gzipped | 134,233 B | 126,676 B |
| All emitted JavaScript chunks, decoded | 845,175 B | 845,176 B |
| Script execution during observation, median | 32.1 ms | 31.9 ms |
| Layout during observation, median | 118.5 ms | 108.3 ms |
| Main-thread task duration, median | 245.1 ms | 236.6 ms |

The initial code payload decreased 7.9% decoded and 5.6% gzipped. JavaScript size is essentially unchanged: Vite's CSS dependency map adds 113 initial bytes. No JavaScript bundle reduction is claimed. Gzip totals are calculated from emitted files; the preview server's actual wire compression is not assumed.

| Run | Before load | After load | Before FCP/LCP | After FCP/LCP |
| --- | ---: | ---: | ---: | ---: |
| 1 | 97.4 ms | 60.1 ms | 436 ms | 252 ms |
| 2 | 88.3 ms | 61.4 ms | 400 ms | 304 ms |
| 3 | 83.0 ms | 66.4 ms | 324 ms | 280 ms |
| 4 | 65.7 ms | 62.4 ms | 272 ms | 284 ms |
| 5 | 61.7 ms | 61.5 ms | 296 ms | 288 ms |
| 6 | 65.1 ms | 71.6 ms | 288 ms | 296 ms |
| 7 | 64.3 ms | 64.9 ms | 284 ms | 284 ms |

Conditions: Windows, isolated headless Chrome 156.0.8078.79, production Vite preview, 1440 × 900 at scale 1, no CPU/network throttling, fresh tab for each navigation, browser cache cleared and disabled, service workers bypassed, two seconds of observation after load, no input or scrolling. Before and after use ports 4174 and 4173 respectively. Host, OS, connection and font caches can still vary. The load event can precede React's first paint; FCP/LCP measure visible readiness, with the same hero heading as LCP in both builds. The small timing differences do not demonstrate statistical significance.

The first diagnostic batch had a 1,244 ms first-run baseline paint, followed by a 356 ms median across five runs. The intermediate after-build had a 300 ms median. These earlier samples remain in `results/oct30-before.json` and `results/oct30-after.json`; the table above uses the final seven-run comparison, not the more favorable intermediate comparison.

Lighthouse was run three times per build and preset, sequentially, alternating build order on the second pair. The following are medians of all three runs, with no warning-bearing samples excluded:

| Lighthouse metric | Desktop before | Desktop after | Mobile before | Mobile after |
| --- | ---: | ---: | ---: | ---: |
| Performance score | 99 | 100 | 81 | 85 |
| FCP | 275.3 ms | 275.0 ms | 1,241.1 ms | 925.3 ms |
| LCP | 275.3 ms | 275.0 ms | 1,241.1 ms | 925.3 ms |
| Total Blocking Time | 97.8 ms | 72.5 ms | 767.0 ms | 577.6 ms |
| Cumulative Layout Shift | 0 | 0 | 0 | 0 |

Lighthouse uses simulated throttling. Desktop uses the desktop preset; mobile uses its default mobile configuration. Exact version, timestamps, throttling settings, individual values and warnings are retained in the [summary](results/oct30-summary.json) and `oct30-paired-*.json` audits. Mobile FCP ranges were 911–1,252 ms before and 914–1,554 ms after. One mobile run in each build reported that the host CPU was slower than Lighthouse expects. The earlier single after-mobile audit also reported this warning and scored 78; it is retained in `oct30-after-lighthouse-mobile.json`. These variable results support the payload savings more strongly than a precise speedup claim. **Mobile does not meet 600 ms.** No field Core Web Vitals or deployed-server latency was measured.

Chrome Performance profiling found initial style calculation and layout to be larger costs than script evaluation: the baseline diagnostic trace includes an 84.6 ms layout and a 53.4 ms style update. The final trace still contains a 98.5 ms layout and a 43.2 ms style update. Lighthouse flagged unused CSS and JavaScript. Coverage is evidence of what one navigation exercised, not permission to delete features or vendor functions that interactions need.

Changes and reviewed boundaries:

- Moved workspace base, dark and responsive rules from `index.css` to `workspace.css`, imported by the existing lazy session provider. This keeps them out of the initial landing request. Project-heading variant rules travel with the workspace rules to preserve their cascade.
- Moved lower-section-specific rules from `minimal_theme.css` to `components/landing/landingSections.css`. Existing lazy landing sections and the public information pages import this stylesheet; Vite loads it before rendering those chunks. Shared initial theme rules remain in place.
- Removed only the two `trust-sep` elements between the three requested labels. Retained the shield, lock and sparkle icons. The label row uses a consistent 12 px vertical / 24 px horizontal gap and 1.5 line height, with existing responsive wrapping.
- Existing React route splitting, lazy preview resource panels, deferred lower components and CSS/Web Animations hero entrances were already present and retained. Scroll parallax already avoids React state updates and schedules compositor transforms with `requestAnimationFrame`.
- Existing small WebP logos, local WOFF2 fonts, `font-display: swap`, font subsets and critical body/heading font preloads were retained. There are no Google Fonts requests. The LCP is text, and large PNG assets for other routes are absent from initial landing requests.
- No API requests occurred in any final landing navigation. Existing browser checks also verified this with a saved token. Authentication, Markdown and Motion remain deferred to their existing routes or interactions.
- All declared runtime dependencies are used. No dependency or feature was removed solely because initial coverage did not exercise it. Lighthouse remains a diagnostic tool in the workspace cache, not an application dependency.

Validation: production TypeScript/Vite build passed; all 21 unit tests passed; 52 functional browser checks and nine animation/navigation checks passed. Lint exited successfully with existing project warnings; the changed/new performance scripts pass focused lint. `git diff --check` passed.

Computed-style comparisons cover eight routes, three widths (1440, 768, 390) and both light/dark preferences. After the focused project-heading corrections, all 48 cases have no unexpected differences in the sampled properties. The corrected project route was rechecked in all six width/theme combinations. This is a sampled CSS comparison, not exhaustive pixel equivalence. Workspace comparisons use a local guest fixture and perform no backend writes. Live authenticated RAG, ingestion and database mutations were not exercised.

Evidence: [final timings before](results/oct30-final-before.json), [final timings after](results/oct30-final-after.json), [baseline trace](results/oct30-before-trace.json), [final trace](results/oct30-final-after-trace.json), [CSS comparisons](results/oct30-css-comparison.json), [project recheck](results/oct30-project-css-comparison.json), [desktop labels](results/oct30-labels-1440.png), [mobile labels](results/oct30-labels-390.png), [combined results](results/oct30-summary.json). The combined results replace earlier project cases with the successful focused recheck and retain the original comparison evidence separately.

To reproduce, run `npm run build`, serve the final build on 4173 and the retained `.perf/oct30-before-dist` artifact on 4174, and launch an isolated headless Chrome with debugging port 9222. Run browser tests and timing/audit captures sequentially:

```powershell
node scripts/performance/measure.mjs oct30-final-before 7 http://127.0.0.1:4174/
node scripts/performance/measure.mjs oct30-final-after 7
node scripts/performance/diagnose.mjs oct30-final-after
node scripts/performance/audit-pairs.mjs ../../.perf/npm-cache/_npx/0f94ee7615faf582/node_modules/lighthouse/cli/index.js
node scripts/performance/verify-css-split.mjs
node scripts/performance/verify-css-split.mjs /app/projects/proj_brim_core performance/results/oct30-project-css-comparison.json
node scripts/performance/summarize-oct30.mjs
```

Remaining costs are initial vendor JavaScript, the remaining global stylesheet, font/text layout, and throttled mobile main-thread work. Further large reductions would require more substantial rendering or stylesheet changes and deployed-host measurements. The measured timing improvement here is modest; the deterministic result is reduced blocking CSS without removing functionality.
