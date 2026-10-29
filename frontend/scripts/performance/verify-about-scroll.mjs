import { mkdir, writeFile } from 'node:fs/promises';
import { connect, delay } from './cdp.mjs';

const base = process.env.ABOUT_TEST_URL ?? 'http://127.0.0.1:4173';
const cdp = await connect();
const checks = [];
const errors = [];
await cdp.send('Page.enable');
await cdp.send('Runtime.enable');
await cdp.send('Emulation.setFocusEmulationEnabled', { enabled: true });
await cdp.send('Page.addScriptToEvaluateOnNewDocument', { source: `window.__scrollDoc = crypto.randomUUID();window.__pageShows=[];window.addEventListener('pageshow',e=>window.__pageShows.push(e.persisted));` });
cdp.on('Runtime.exceptionThrown', event => errors.push(event.exceptionDetails.text));

async function wait(expression, label) {
  const started = Date.now();
  while (!(await cdp.evaluate(expression))) {
    if (Date.now() - started > 10000) throw new Error(`Failed: ${label}; current=${JSON.stringify(await cdp.evaluate('({url:location.href,x:scrollX,y:scrollY,mode:history.scrollRestoration})'))}`);
    await delay(80);
  }
  checks.push(label);
}
async function settledAtTop(label) {
  await wait(`location.hash==='#about' && !!document.getElementById('about') && scrollX===0 && scrollY===0`, label);
  await delay(450);
  if (!(await cdp.evaluate('scrollX===0 && scrollY===0'))) throw new Error(`Scroll moved after settling: ${label}`);
}
async function scroll(y) {
  await cdp.evaluate(`window.scrollTo({left:0,top:${y},behavior:'instant'})`);
  await delay(250);
}
async function open(path) {
  await cdp.send('Page.navigate', { url: base + path });
  await wait(`!!document.querySelector('main h1') && location.pathname===${JSON.stringify(path.split('#')[0] || '/')}`, `${path} renders`);
  await delay(500);
}
async function click(selector) {
  await cdp.evaluate(`document.querySelector(${JSON.stringify(selector)}).click()`);
}

try {
  for (const width of [1440, 390]) {
    await cdp.send('Emulation.setDeviceMetricsOverride', { width, height: 900, deviceScaleFactor: 1, mobile: width < 640 });
    await open('/#about');
    await settledAtTop(`Direct About URL starts at (0,0), ${width}px`);
    await scroll(800);
    await wait(`scrollY===800`, `Users can still scroll normally on About, ${width}px`);
    const oldDoc = await cdp.evaluate('window.__scrollDoc');
    await cdp.send('Page.reload');
    await wait(`window.__scrollDoc !== ${JSON.stringify(oldDoc)} && !!document.querySelector('main h1')`, 'Refresh creates a new document');
    await settledAtTop(`Refresh ignores the saved About position, ${width}px`);

    await scroll(950);
    await click('.public-nav a[href="/#about"]');
    await settledAtTop(`Re-selecting About resets to top, ${width}px`);
    await scroll(950);
    await click('.footer a[href="/#about"]');
    await settledAtTop(`Footer About link resets to top, ${width}px`);

    await open('/features');
    await scroll(550);
    await click('.public-nav a[href="/#about"]');
    await settledAtTop(`About navigation from Features resets to top, ${width}px`);
    await cdp.evaluate('history.back()');
    await wait(`location.pathname==='/features' && scrollY===550`, `Back preserves Features scroll position, ${width}px`);
    await cdp.evaluate('history.forward()');
    await settledAtTop(`Forward into About starts at top, ${width}px`);

    await scroll(1000);
    await click('.public-nav a[href="/how-it-works"]');
    await wait(`location.pathname==='/how-it-works' && !!document.getElementById('process')`, 'React Router navigation leaves About');
    await wait(`history.scrollRestoration==='auto'`, 'Native scroll restoration restored outside About');
    await scroll(450);
    await cdp.evaluate('history.back()');
    await settledAtTop(`React Router back into About resets to top, ${width}px`);
    await cdp.evaluate('history.forward()');
    await wait(`location.pathname==='/how-it-works' && scrollY===450`, `Forward preserves How It Works scroll position, ${width}px`);

    await click('.public-nav a[href="/#about"]');
    await settledAtTop(`About navigation from How It Works resets to top, ${width}px`);
    await click('.public-nav a[href="/#faq"]');
    await wait(`location.hash==='#faq' && !!document.getElementById('faq')`, 'FAQ remains available');
    await delay(1500);
    await wait(`Math.abs(document.getElementById('faq').getBoundingClientRect().top-90)<120`, `FAQ anchor behavior preserved, ${width}px`);
    await wait(`history.scrollRestoration==='auto'`, 'FAQ retains native restoration');
    await cdp.evaluate('history.back()');
    await settledAtTop(`Hash-history back into About resets to top, ${width}px`);

    // Full-document history navigation also covers pageshow/BFCache restoration.
    await scroll(1000);
    await cdp.evaluate(`location.href=${JSON.stringify(base + '/features')}`);
    await wait(`location.pathname==='/features' && !!document.querySelector('.info-feature-grid')`, 'Full document navigation leaves About');
    await wait(`history.scrollRestoration==='auto'`, 'Full document destination retains native restoration');
    await scroll(500);
    await cdp.evaluate('history.back()');
    await settledAtTop(`Full document back into About resets to top, ${width}px`);
    await cdp.evaluate('history.forward()');
    await wait(`location.pathname==='/features' && scrollY===500`, `Full document forward preserves other-page scrolling, ${width}px`);

    await open('/#features');
    await wait(`!!document.getElementById('features')`, 'Features section loads');
    await delay(1500);
    await wait(`Math.abs(document.getElementById('features').getBoundingClientRect().top-90)<120`, `Features anchor behavior preserved, ${width}px`);
  }
  if (errors.length) throw new Error(errors.join('; '));
  await mkdir('performance/results', { recursive: true });
  await writeFile('performance/results/about-scroll-checks.json', JSON.stringify({ passed: checks.length, checks, errors }, null, 2));
  console.log(JSON.stringify({ passed: checks.length, checks, errors }, null, 2));
} finally {
  await cdp.close();
}
