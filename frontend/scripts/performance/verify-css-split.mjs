import { writeFile } from 'node:fs/promises';
import { connect, delay } from './cdp.mjs';

// Compare the production builds served on 4174 (before) and 4173 (after).
// Use an isolated, local guest fixture; no credentials or backend writes.
const cases = [
  ['/#features', '.final-cta-card'], ['/features', '.product-info-page'],
  ['/how-it-works', '.product-info-page'], ['/login', '.auth-submit-btn'],
  ['/app', '.app-shell textarea'], ['/app/settings', '.settings-page'],
  ['/app/profile', '.profile-card'], ['/app/projects/proj_brim_core', '.project-heading'],
];
const properties = ['display', 'position', 'font-family', 'font-size', 'font-weight',
  'line-height', 'color', 'background-color', 'border', 'padding', 'margin', 'gap',
  'grid-template-columns', 'flex-direction', 'align-items', 'justify-content',
  'width', 'height', 'min-width', 'max-width', 'border-radius', 'overflow'];
const comparisons = [], differences = [], expectedChanges = [];
const selectedCases = process.argv[2] ? cases.filter(([path]) => path === process.argv[2]) : cases;
const output = process.argv[3] ?? 'performance/results/oct30-css-comparison.json';
const cdp = await connect();
try {
  await cdp.send('Page.enable');
  await cdp.send('Emulation.setEmulatedMedia', { features: [{ name: 'prefers-reduced-motion', value: 'reduce' }] });
  await cdp.send('Page.addScriptToEvaluateOnNewDocument', { source: `
    localStorage.removeItem('sap_assistant_token');
    localStorage.setItem('clyptus_demo_user', JSON.stringify({id:'perf-fixture', name:'Preview User', email:'preview@example.invalid', isGuest:true, profileCompleted:true}));
  ` });
  for (const width of [1440, 768, 390]) {
    await cdp.send('Emulation.setDeviceMetricsOverride', { width, height: 900, deviceScaleFactor: 1, mobile: width === 390 });
    for (const theme of ['light', 'dark']) {
      for (const [path, ready] of selectedCases) {
        const snapshots = [];
        for (const port of [4174, 4173]) {
          await cdp.send('Page.navigate', { url: `http://127.0.0.1:${port}/` });
          await delay(100);
          await cdp.evaluate(`localStorage.setItem('clyptus-appearance', '${theme}')`);
          await cdp.send('Page.navigate', { url: `http://127.0.0.1:${port}${path}` });
          const start = Date.now();
          while (!(await cdp.evaluate(`!!document.querySelector(${JSON.stringify(ready)})`))) {
            if (Date.now() - start > 10000) throw new Error(`Timed out: ${port}${path} (${ready})`);
            await delay(100);
          }
          await cdp.evaluate('document.fonts.ready');
          await delay(600);
          snapshots.push(await cdp.evaluate(`(() => {
            const props=${JSON.stringify(properties)};
            return [...document.querySelectorAll('#root *')]
              .filter(e=>!e.closest('.cta-trust-indicators') && !e.closest('svg') && e.tagName!=='STYLE')
              .map(e=>({tag:e.tagName, classes:e.getAttribute('class'), containsCta:!!e.querySelector('.cta-trust-indicators'), styles:Object.fromEntries(props.map(p=>[p,getComputedStyle(e).getPropertyValue(p)]))}));
          })()`));
          if (port === 4173 && path === '/#features') {
            const labels = await cdp.evaluate(`(() => {
              const bar=document.querySelector('.cta-trust-indicators');
              return {labels:[...bar.querySelectorAll('.trust-indicator-item span')].map(e=>e.textContent), separators:bar.querySelectorAll('.trust-sep').length, overflow:document.documentElement.scrollWidth>innerWidth};
            })()`);
            if (labels.separators || labels.labels.length !== 3 || labels.overflow) throw new Error(JSON.stringify(labels));
            if (theme === 'light') {
              await cdp.evaluate(`document.querySelector('.final-cta-card').scrollIntoView({behavior:'instant',block:'center'})`);
              await delay(800);
              await writeFile(`performance/results/oct30-labels-${width}.png`, Buffer.from((await cdp.send('Page.captureScreenshot', { format:'png' })).data, 'base64'));
            }
          }
        }
        const [before, after] = snapshots;
        const changes = [];
        if (before.length !== after.length) changes.push({ nodeCounts: [before.length, after.length] });
        for (let i = 0; i < Math.min(before.length, after.length); i++) {
          if (before[i].tag !== after[i].tag || before[i].classes !== after[i].classes) {
            changes.push({ node: i, before: before[i], after: after[i] }); continue;
          }
          for (const property of properties) {
            const a=before[i].styles[property], b=after[i].styles[property];
            if (a!==b && property==='height' && before[i].containsCta) {
              expectedChanges.push({width,theme,path,node:i,property,before:a,after:b,reason:'Requested CTA label spacing and line height'}); continue;
            }
            if (a!==b && !(a.endsWith('px') && b.endsWith('px') && Math.abs(parseFloat(a)-parseFloat(b))<0.1))
              changes.push({node:i, classes:before[i].classes, property, before:a, after:b});
          }
        }
        const result = { width, theme, path, comparedNodes: before.length, changes };
        comparisons.push(result);
        if (changes.length) differences.push(result);
        await writeFile(output, JSON.stringify({ comparisons, differences, expectedChanges }, null, 2));
        console.log(JSON.stringify({ width, theme, path, nodes:before.length, differences:changes.length }));
      }
    }
  }
} finally { await cdp.close(); }
await writeFile(output, JSON.stringify({ comparisons, differences, expectedChanges }, null, 2));
if (differences.length) process.exitCode = 1;
