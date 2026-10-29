import { readFile, writeFile } from 'node:fs/promises';
import { resolve, basename } from 'node:path';
import { gzipSync } from 'node:zlib';

const read = async name => JSON.parse(await readFile(`performance/results/${name}.json`, 'utf8'));
const median = values => [...values].sort((a,b)=>a-b)[Math.floor(values.length/2)];
const summary = {};
for (const label of ['before', 'after']) {
  const measurement = await read(`load-${label}`);
  const resources = measurement.results[0].resources;
  const js = resources.filter(r => new URL(r.name).pathname.endsWith('.js'));
  const build = label === 'before' ? process.argv[2] : 'dist';
  const compressedBytes = build ? (await Promise.all(js.map(async r => gzipSync(await readFile(resolve(build, 'assets', basename(new URL(r.name).pathname)))).length))).reduce((a,b)=>a+b,0) : null;
  summary[label] = {
    ...measurement.summary,
    loadRange: measurement.results.map(r=>r.navigation.loadEventEnd),
    fcpRange: measurement.results.map(r=>r.paints.find(p=>p.name==='first-contentful-paint')?.startTime),
    initialJsDecodedBytes: js.reduce((sum,r)=>sum+r.decodedBodySize,0),
    initialJsGzipBytes: compressedBytes,
    initialLocalCssDecodedBytes: resources.filter(r=>new URL(r.name).pathname.endsWith('.css')).reduce((sum,r)=>sum+r.decodedBodySize,0),
    totalBlockingStylesheetBytes: resources.filter(r=>r.renderBlockingStatus==='blocking').reduce((sum,r)=>sum+r.decodedBodySize,0),
    scriptDurationMedianMs: median(measurement.results.map(r=>r.metrics.ScriptDuration*1000)),
    layoutDurationMedianMs: median(measurement.results.map(r=>r.metrics.LayoutDuration*1000)),
    recalcStyleCountMedian: median(measurement.results.map(r=>r.metrics.RecalcStyleCount)),
    mainThreadTimeMedianMs: median(measurement.results.map(r=>r.metrics.TaskDuration*1000)),
    longTasksMedianMs: median(measurement.results.map(r=>r.observed.tasks.reduce((sum,t)=>sum+t.duration,0))),
  };
  for (const mode of ['desktop', 'mobile']) {
    const audit=await read(`load-${label}-lighthouse-${mode}`);
    summary[label][`lighthouse${mode}`] = {
      version:audit.lighthouseVersion, timestamp:audit.fetchTime,
      score: audit.categories.performance.score*100,
      fcp: audit.audits['first-contentful-paint'].numericValue,
      lcp: audit.audits['largest-contentful-paint'].numericValue,
      tbt: audit.audits['total-blocking-time'].numericValue,
      cls: audit.audits['cumulative-layout-shift'].numericValue,
      throttling: audit.configSettings.throttling,
      throttlingMethod: audit.configSettings.throttlingMethod,
      warnings: audit.runWarnings,
    };
  }
}
await writeFile('performance/results/load-summary.json', JSON.stringify(summary,null,2));
console.log(JSON.stringify(summary,null,2));
