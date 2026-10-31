import { spawn } from 'node:child_process';
import { readFile } from 'node:fs/promises';

// Pass the Lighthouse CLI path; keep Lighthouse out of application dependencies.
const cli = process.argv[2];
if (!cli) throw new Error('Usage: node scripts/performance/audit-pairs.mjs <lighthouse/cli/index.js>');
for (let run = 1; run <= 3; run++) {
  for (const mode of ['desktop', 'mobile']) {
    // Alternate build order to reduce systematic warm-up/order effects.
    for (const label of run % 2 ? ['before', 'after'] : ['after', 'before']) {
      const output = `performance/results/oct30-paired-${label}-${mode}-${run}.json`;
      const args = [cli, `http://127.0.0.1:${label === 'before' ? 4174 : 4173}/`,
        '--port=9222', '--only-categories=performance', '--output=json',
        `--output-path=${output}`, '--quiet'];
      if (mode === 'desktop') args.push('--preset=desktop');
      await new Promise((resolve, reject) => {
        const child = spawn(process.execPath, args, { stdio: 'inherit', windowsHide: true });
        child.on('error', reject);
        child.on('exit', code => code === 0 ? resolve() : reject(new Error(`Lighthouse exited ${code}`)));
      });
      const audit = JSON.parse(await readFile(output, 'utf8'));
      console.log(JSON.stringify({ label, mode, run, score: audit.categories.performance.score * 100,
        fcp: audit.audits['first-contentful-paint'].numericValue,
        lcp: audit.audits['largest-contentful-paint'].numericValue,
        tbt: audit.audits['total-blocking-time'].numericValue, warnings: audit.runWarnings }));
    }
  }
}
