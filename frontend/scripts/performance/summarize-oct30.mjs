import { readFile, writeFile, readdir } from 'node:fs/promises';
import { basename, resolve } from 'node:path';
import { gzipSync } from 'node:zlib';

const read = async file => JSON.parse(await readFile(`performance/results/${file}.json`, 'utf8'));
const median = values => [...values].sort((a,b) => a-b)[Math.floor(values.length/2)];
const summary = {};
for (const label of ['before', 'after']) {
  const timing = await read(`oct30-final-${label}`);
  const build = label === 'before' ? '../../.perf/oct30-before-dist' : 'dist';
  const resources = timing.results[0].resources;
  const size = async extension => {
    const files = resources.filter(r => new URL(r.name).pathname.endsWith(extension));
    const gzip = await Promise.all(files.map(async r => gzipSync(await readFile(resolve(build, 'assets', basename(new URL(r.name).pathname)))).length));
    return {decodedBytes:files.reduce((s,r) => s+r.decodedBodySize,0), gzipBytes:gzip.reduce((s,n)=>s+n,0)};
  };
  const js = await size('.js'), css = await size('.css');
  const builtAssets = await readdir(resolve(build, 'assets'));
  summary[label] = {
    ...timing.summary, js, css,
    initialCode: { decodedBytes:js.decodedBytes+css.decodedBytes, gzipBytes:js.gzipBytes+css.gzipBytes },
    allEmittedJsBytes: (await Promise.all(builtAssets.filter(f=>f.endsWith('.js')).map(async f=>(await readFile(resolve(build,'assets',f))).length))).reduce((s,n)=>s+n,0),
    loadRange: timing.results.map(r=>r.navigation.loadEventEnd),
    fcpRange: timing.results.map(r=>r.paints.find(p=>p.name==='first-contentful-paint')?.startTime),
    lcpRange: timing.results.map(r=>r.observed.lcp.at(-1)?.time),
    scriptMs:median(timing.results.map(r=>r.metrics.ScriptDuration*1000)),
    layoutMs:median(timing.results.map(r=>r.metrics.LayoutDuration*1000)),
    taskMs:median(timing.results.map(r=>r.metrics.TaskDuration*1000)),
    apiRequests:timing.results.flatMap(r=>r.requests.filter(q=>q.url.includes('/api/'))),
  };
  for (const mode of ['desktop', 'mobile']) {
    const audits = await Promise.all([1,2,3].map(i=>read(`oct30-paired-${label}-${mode}-${i}`)));
    const values = audits.map(a=>({score:a.categories.performance.score*100,
      fcp:a.audits['first-contentful-paint'].numericValue, lcp:a.audits['largest-contentful-paint'].numericValue,
      tbt:a.audits['total-blocking-time'].numericValue, cls:a.audits['cumulative-layout-shift'].numericValue,
      warnings:a.runWarnings, version:a.lighthouseVersion, timestamp:a.fetchTime}));
    summary[label][mode] = { medians:Object.fromEntries(['score','fcp','lcp','tbt','cls'].map(k=>[k,median(values.map(v=>v[k]))])), runs:values,
      throttling:audits[0].configSettings.throttling, method:audits[0].configSettings.throttlingMethod };
  }
}
const comparison = await read('oct30-css-comparison');
const recheck = await read('oct30-project-css-comparison');
const latest = new Map(comparison.comparisons.map(c=>[JSON.stringify([c.width,c.theme,c.path]),c]));
for(const c of recheck.comparisons)latest.set(JSON.stringify([c.width,c.theme,c.path]),c);
summary.validation={cssCases:latest.size,unexpectedCssDifferences:[...latest.values()].filter(c=>c.changes.length),
  expectedCtaHeightChanges:comparison.expectedChanges,
  functional:await read('functional-checks'), animations:await read('load-animation-checks')};
await writeFile('performance/results/oct30-summary.json', JSON.stringify(summary,null,2));
console.log(JSON.stringify(summary,null,2));
