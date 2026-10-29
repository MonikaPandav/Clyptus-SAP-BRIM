import { mkdir, writeFile } from 'node:fs/promises';
import { connect, delay } from './cdp.mjs';

// Serve the retained before-build on 4174 and the optimized production build on 4173.
const layouts = {};
const differences = [];
const selectors = ['.public-nav', '.nav-inner', '.nav-links', '.nav-actions', '.nav-signin',
  '.hero-main-title', '.hero-description', '.hero-actions-row', '.hero-trust-bar',
  '.hero-showcase-container', '.showcase-window-header', '.showcase-sidebar',
  '.showcase-main-workspace', '.workspace-header', '.ws-dot', '.ws-badge', '.footer'];
await mkdir('performance/results', { recursive: true });
for (const width of [1440, 768, 390]) {
  for (const [label, port] of [['before', 4174], ['after', 4173]]) {
    const cdp = await connect();
    try {
      await cdp.send('Page.enable');
      await cdp.send('Emulation.setDeviceMetricsOverride', { width, height: 900, deviceScaleFactor: 1, mobile: width === 390 });
      await cdp.send('Page.navigate', { url: `http://127.0.0.1:${port}/#about` });
      await delay(2500);
      layouts[`${label}-${width}`] = await cdp.evaluate(`Object.fromEntries(${JSON.stringify(selectors)}.map(selector => {
        const e = document.querySelector(selector);
        if (!e) return [selector, null];
        const r = e.getBoundingClientRect(), s = getComputedStyle(e);
        return [selector, { x:r.x, y:r.y, width:r.width, height:r.height, font:s.fontFamily,
          weight:s.fontWeight, size:s.fontSize, color:s.color, background:s.backgroundColor,
          border:s.border, display:s.display, gap:s.gap }];
      }))`);
      await writeFile(`performance/results/load-layout-${label}-${width}.png`, Buffer.from((await cdp.send('Page.captureScreenshot', { format: 'png' })).data, 'base64'));
    } finally { await cdp.close(); }
  }
  for (const selector of selectors) {
    const before = layouts[`before-${width}`][selector], after = layouts[`after-${width}`][selector];
    const changes = Object.keys(before ?? {}).filter(key => typeof before[key] === 'number'
      ? Math.abs(before[key] - after?.[key]) > 1
      : before[key] !== after?.[key]);
    if (changes.length || !before || !after) differences.push({ width, selector, changes, before, after });
  }
}
await writeFile('performance/results/load-layout-comparison.json', JSON.stringify({ layouts, differences }, null, 2));
console.log(JSON.stringify({ differences }, null, 2));
if (differences.length) process.exitCode = 1;
