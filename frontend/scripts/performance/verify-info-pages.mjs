import { mkdir, writeFile } from 'node:fs/promises';
import { connect, delay } from './cdp.mjs';

const cdp = await connect();
const checks = [];
const errors = [];
const measurements = [];
await mkdir('performance/results', { recursive: true });
await cdp.send('Page.enable');
await cdp.send('Runtime.enable');
await cdp.send('Network.enable');
await cdp.send('Network.setCacheDisabled', { cacheDisabled: true });
await cdp.send('Emulation.setFocusEmulationEnabled', { enabled: true });
await cdp.send('Page.addScriptToEvaluateOnNewDocument', { source: `window.__infoShifts=[];new PerformanceObserver(l=>l.getEntries().forEach(e=>{if(!e.hadRecentInput)window.__infoShifts.push(e.value)})).observe({type:'layout-shift',buffered:true});` });
cdp.on('Runtime.exceptionThrown', e => errors.push(e.exceptionDetails.text));

async function wait(expression, label) {
  const started = Date.now();
  while (!(await cdp.evaluate(expression))) {
    if (Date.now() - started > 12000) throw new Error(`Failed: ${label}`);
    await delay(80);
  }
  checks.push(label);
}
function check(value, label) {
  if (!value) throw new Error(`Failed: ${label}`);
  checks.push(label);
}
async function navigate(port, path) {
  await cdp.send('Page.navigate', { url: `http://127.0.0.1:${port}${path}` });
  await wait(`!!document.querySelector('main h1')`, `${path} renders`);
  await delay(600);
}
async function content() {
  return cdp.evaluate(`({text:document.querySelector('main').textContent.replace(/\s/g,''),icons:[...document.querySelectorAll('main svg')].map(e=>e.getAttribute('class')).sort(),links:[...document.querySelectorAll('main a')].map(e=>({text:e.textContent.replace(/\s/g,''),href:e.getAttribute('href')}))})`);
}
const baseline = {};
try {
  await cdp.send('Emulation.setDeviceMetricsOverride', { width: 1440, height: 900, deviceScaleFactor: 1, mobile: false });
  for (const path of ['/features', '/how-it-works']) {
    await navigate(4174, path);
    baseline[path] = await content();
  }
  for (const width of [1440, 768, 390, 320]) {
    await cdp.send('Emulation.setDeviceMetricsOverride', { width, height: 900, deviceScaleFactor: 1, mobile: width < 640 });
    for (const path of ['/features', '/how-it-works']) {
      await navigate(4173, path);
      check(JSON.stringify(await content()) === JSON.stringify(baseline[path]), `${path} preserves every text, icon, and content link at ${width}px`);
      await wait(`document.documentElement.scrollWidth <= innerWidth`, `${path} has no horizontal overflow at ${width}px`);
      const selector = path === '/features' ? '.info-feature-card' : '.info-process-step';
      const originalGeometry = await cdp.evaluate(`Array.from(document.querySelectorAll('${selector}'),e=>({top:e.offsetTop,width:e.offsetWidth,height:e.offsetHeight}))`);
      const count = path === '/features' ? 6 : 5;
      await wait(`document.querySelectorAll('${selector}').length === ${count}`, `${path} keeps ${count} items`);
      for (let index = 0; index < count; index++) {
        await cdp.evaluate(`document.querySelectorAll('${selector}')[${index}].scrollIntoView({behavior:'instant',block:'center'})`);
        await delay(260);
        if (path === '/how-it-works') {
          await wait(`document.querySelectorAll('.info-process-step')[${index}].dataset.revealed === 'true'`, `Workflow step ${index + 1} reveals on scroll at ${width}px`);
        }
      }
      await delay(700);
      const finalGeometry = await cdp.evaluate(`Array.from(document.querySelectorAll('${selector}'),e=>({top:e.offsetTop,width:e.offsetWidth,height:e.offsetHeight}))`);
      check(JSON.stringify(originalGeometry) === JSON.stringify(finalGeometry), `${path} entrance animations do not change item layout geometry at ${width}px`);
      if (path === '/features') {
        const columns = await cdp.evaluate(`getComputedStyle(document.querySelector('.info-feature-grid')).gridTemplateColumns.split(' ').length`);
        check(columns === (width <= 640 ? 1 : width <= 1024 ? 2 : 3), `Feature grid responds correctly at ${width}px`);
      } else {
        await wait(`document.querySelectorAll('.info-step-connector').length === 4`, `Workflow has four connectors at ${width}px`);
        await wait(`[...document.querySelectorAll('.info-step-connector > span')].every(e=>getComputedStyle(e).transform==='matrix(1, 0, 0, 1, 0, 0)' || getComputedStyle(e).transform==='none')`, `Workflow connectors finish drawing at ${width}px`);
      }
      const timing = await cdp.evaluate(`({load:performance.getEntriesByType('navigation')[0].loadEventEnd,fcp:performance.getEntriesByName('first-contentful-paint')[0]?.startTime,cls:window.__infoShifts.reduce((s,v)=>s+v,0),apiCalls:performance.getEntriesByType('resource').filter(e=>e.name.includes('/api/')).length})`);
      measurements.push({ path, width, ...timing });
      check(timing.apiCalls === 0, `${path} performs no backend calls`);
      if (width === 1440 || width === 390) {
        await cdp.evaluate(`window.scrollTo({top:0,behavior:'instant'})`);
        await delay(300);
        await writeFile(`performance/results/info-${path.slice(1)}-${width}.png`, Buffer.from((await cdp.send('Page.captureScreenshot', { format: 'png' })).data, 'base64'));
        const clip = await cdp.evaluate(`(()=>{const e=document.querySelector('${path === '/features' ? '.info-feature-grid' : '.info-process-list'}');const r=e.getBoundingClientRect();return{x:r.x,y:r.y+scrollY,width:r.width,height:r.height,scale:1}})()`);
        await writeFile(`performance/results/info-${path.slice(1)}-${width}-content.png`, Buffer.from((await cdp.send('Page.captureScreenshot', { format: 'png', captureBeyondViewport: true, clip })).data, 'base64'));
      }
    }
  }
  await cdp.send('Emulation.setDeviceMetricsOverride', { width: 1440, height: 900, deviceScaleFactor: 1, mobile: false });
  await navigate(4173, '/features');
  await cdp.evaluate(`document.querySelector('.info-hero-action').click()`);
  await wait(`location.pathname === '/how-it-works' && !!document.querySelector('.info-process-list')`, 'See how it works link navigates correctly');
  await cdp.evaluate(`document.querySelector('.info-hero-action').click()`);
  await wait(`location.hash === '#process'`, 'Architecture link preserves workflow anchor');
  await delay(1200);
  await wait(`Math.abs(document.getElementById('process').getBoundingClientRect().top) < 220`, 'Workflow anchor lands below sticky navigation');
  await cdp.evaluate(`document.querySelector('.info-bottom-cta a').click()`);
  await wait(`location.pathname === '/login' && !!document.querySelector('.auth-submit-btn')`, 'Existing CTA opens sign-in');

  await cdp.send('Emulation.setEmulatedMedia', { features: [{ name: 'prefers-reduced-motion', value: 'reduce' }] });
  for (const path of ['/features', '/how-it-works']) {
    await navigate(4173, path);
    await wait(`[...document.querySelectorAll('.info-feature-card,.info-workflow-card')].every(e=>getComputedStyle(e).opacity==='1' && getComputedStyle(e).transform==='none')`, `${path} reduced-motion cards are immediately visible and stationary`);
    await wait(`[...document.querySelectorAll('main a')].every(e=>parseFloat(getComputedStyle(e).transitionDuration)===0)`, `${path} reduced-motion transitions disabled`);
  }
  // Confirm that route-loaded styles do not alter About after SPA navigation.
  await cdp.send('Emulation.setEmulatedMedia', { features: [] });
  await navigate(4174, '/#about');
  const aboutStyle = async () => cdp.evaluate(`Object.fromEntries(['.about-clyptus-section','.about-clyptus-section .section-title-large','.about-clyptus-section .story-card','.about-clyptus-section .story-card h3','.about-clyptus-section .story-card p'].map(sel=>{const s=getComputedStyle(document.querySelector(sel));return[sel,{font:s.fontFamily,size:s.fontSize,color:s.color,background:s.background,border:s.border,padding:s.padding,radius:s.borderRadius}]}))`);
  await wait(`!!document.querySelector('.about-clyptus-section')`, 'Baseline About loads');
  const aboutBefore = await aboutStyle();
  await navigate(4173, '/features');
  await cdp.evaluate(`document.querySelector('.public-nav .brand').click()`);
  await wait(`!!document.querySelector('.hero-main-title')`, 'Home navigation works after redesign');
  await cdp.evaluate(`location.hash = 'about'`);
  await wait(`!!document.querySelector('.about-clyptus-section')`, 'About loads after visiting redesigned pages');
  check(JSON.stringify(await aboutStyle()) === JSON.stringify(aboutBefore), 'Route-loaded styles preserve About design exactly');
  check(errors.length === 0, 'No browser runtime exceptions');
  const result = { passed: checks.length, checks, errors, measurements, conditions: 'Local production build; Chrome; unthrottled; cache disabled; timings are diagnostic single samples, not a benchmark' };
  await writeFile('performance/results/info-page-checks.json', JSON.stringify(result, null, 2));
  console.log(JSON.stringify(result, null, 2));
} finally {
  await cdp.close();
}
