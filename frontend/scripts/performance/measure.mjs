import { writeFile, mkdir } from 'node:fs/promises';
import { connect, delay } from './cdp.mjs';

const label = process.argv[2] ?? 'baseline';
const runs = Number(process.argv[3] ?? 5);
const url = process.argv[4] ?? 'http://127.0.0.1:4173/';
const results = [];
const browser = await fetch('http://127.0.0.1:9222/json/version').then(r => r.json());
await mkdir('performance/results', { recursive: true });
for (let run = 1; run <= runs; run++) {
  const cdp = await connect();
  const failures = [];
  const requests = [];
  cdp.on('Network.requestWillBeSent', e => requests.push({ url: e.request.url, type: e.type, initiator: e.initiator.type }));
  cdp.on('Network.loadingFailed', e => failures.push({ requestId: e.requestId, error: e.errorText }));
  await cdp.send('Page.enable');
  await cdp.send('Network.enable');
  await cdp.send('Performance.enable');
  await cdp.send('Network.clearBrowserCache');
  await cdp.send('Network.setCacheDisabled', { cacheDisabled: true });
  await cdp.send('Network.setBypassServiceWorker', { bypass: true });
  await cdp.send('Emulation.setDeviceMetricsOverride', { width: 1440, height: 900, deviceScaleFactor: 1, mobile: false });
  await cdp.send('Page.addScriptToEvaluateOnNewDocument', { source: `
    window.__perf = {lcp: [], shifts: [], tasks: []};
    new PerformanceObserver(l => l.getEntries().forEach(e => window.__perf.lcp.push({time:e.startTime, size:e.size, element:e.element?.outerHTML?.slice(0,300)}))).observe({type:'largest-contentful-paint', buffered:true});
    new PerformanceObserver(l => l.getEntries().forEach(e => { if (!e.hadRecentInput) window.__perf.shifts.push({time:e.startTime,value:e.value}); })).observe({type:'layout-shift', buffered:true});
    new PerformanceObserver(l => l.getEntries().forEach(e => window.__perf.tasks.push({start:e.startTime,duration:e.duration}))).observe({type:'longtask', buffered:true});
  ` });
  await cdp.send('Page.navigate', { url });
  const started = Date.now();
  while (!(await cdp.evaluate('performance.getEntriesByType("navigation")[0]?.loadEventEnd > 0'))) {
    if (Date.now() - started > 30000) throw new Error('Navigation did not load within 30s');
    await delay(100);
  }
  // Observe the same two-second interval after load in every run, without scrolling or clicking.
  await delay(2000);
  const page = await cdp.evaluate(`({
    navigation: performance.getEntriesByType('navigation')[0].toJSON(),
    paints: performance.getEntriesByType('paint').map(e=>e.toJSON()),
    resources: performance.getEntriesByType('resource').map(e=>e.toJSON()),
    observed: window.__perf,
    nodes: document.querySelectorAll('*').length,
    fonts: document.fonts.status,
    images: [...document.images].map(i=>({src:i.currentSrc,width:i.width,height:i.height,naturalWidth:i.naturalWidth,naturalHeight:i.naturalHeight,complete:i.complete})),
    scrollHeight: document.documentElement.scrollHeight
  })`);
  const metrics = await cdp.send('Performance.getMetrics');
  const result = { run, ...page, metrics: Object.fromEntries(metrics.metrics.map(m => [m.name, m.value])), requests, failures };
  results.push(result);
  console.log(JSON.stringify({ run, load: page.navigation.loadEventEnd, fcp: page.paints.find(p=>p.name==='first-contentful-paint')?.startTime, lcp: page.observed.lcp.at(-1)?.time, jsBytes: page.resources.filter(r=>new URL(r.name).pathname.endsWith('.js')).reduce((sum,r)=>sum+r.decodedBodySize,0), longTasks:page.observed.tasks }));
  if (run === 1) {
    const shot = await cdp.send('Page.captureScreenshot', { format: 'png' });
    await writeFile(`performance/results/${label}.png`, Buffer.from(shot.data, 'base64'));
  }
  await cdp.close();
}
const median = values => [...values].sort((a,b)=>a-b)[Math.floor(values.length/2)];
const summary = {
  label, url, browser: browser.Browser, viewport: '1440x900 @1', cache: 'disabled and cleared each run', throttling: 'none (CPU and network)', observation: '2 seconds after load',
  loadMedian: median(results.map(r=>r.navigation.loadEventEnd)),
  fcpMedian: median(results.map(r=>r.paints.find(p=>p.name==='first-contentful-paint')?.startTime ?? 0)),
  lcpMedian: median(results.map(r=>r.observed.lcp.at(-1)?.time ?? 0)),
};
await writeFile(`performance/results/${label}.json`, JSON.stringify({ summary, results }, null, 2));
console.log(JSON.stringify(summary));
