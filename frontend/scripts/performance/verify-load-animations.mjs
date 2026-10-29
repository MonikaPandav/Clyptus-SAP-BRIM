import { writeFile } from 'node:fs/promises';
import { connect, delay } from './cdp.mjs';

const cdp = await connect();
const checks = [], requests = [];
cdp.on('Network.requestWillBeSent', e => requests.push(e.request.url));
const assert = (condition, description) => {
  if (!condition) throw new Error(description);
  checks.push(description);
};
try {
  await cdp.send('Page.enable');
  await cdp.send('Network.enable');
  await cdp.send('Emulation.setDeviceMetricsOverride', { width:1440, height:900, deviceScaleFactor:1, mobile:false });
  await cdp.send('Page.navigate', { url:'http://127.0.0.1:4173/' });
  await delay(1800);
  assert(!requests.some(url => /fonts\.google|\/api\/|\/proxy-|LandingSections|AuthContext|PreviewResourcePanels/.test(url)), 'Initial viewport excludes third-party fonts, Motion, API, session and deferred-section resources');
  assert(await cdp.evaluate(`document.fonts.check('750 68px Manrope') && document.fonts.check('400 16px "DM Sans"')`), 'Existing heading and body fonts are available');
  assert(await cdp.evaluate(`['.kicker-pill-subtle','.hero-description','.hero-actions-row','.hero-trust-bar','.hero-showcase-container'].every(s=>getComputedStyle(document.querySelector(s)).opacity === '1')`), 'All hero entrance animations finish visibly');

  await cdp.evaluate(`scrollTo({top:300,behavior:'instant'})`);
  await delay(200);
  assert(await cdp.evaluate(`(() => {
    const hero=document.querySelector('.hero-minimal-section'), rect=hero.getBoundingClientRect();
    const progress=Math.max(0,Math.min(1,-rect.top/rect.height));
    const y=s=>new DOMMatrixReadOnly(getComputedStyle(document.querySelector(s)).transform).m42;
    return Math.abs(y('.orb-left')-80*progress)<0.1 && Math.abs(y('.orb-right')+60*progress)<0.1
      && parseFloat(getComputedStyle(document.querySelector('.hero-showcase-container')).translate.split(' ')[1])>0;
  })()`), 'Ambient layers and preview retain their scroll parallax');

  await cdp.send('Emulation.setEmulatedMedia', { features:[{name:'prefers-reduced-motion',value:'reduce'}] });
  await delay(100);
  assert(await cdp.evaluate(`getComputedStyle(document.querySelector('.orb-left')).transform==='none' && getComputedStyle(document.querySelector('.hero-description')).animationName==='none'`), 'Reduced motion disables parallax and entrance movement');
  await cdp.send('Emulation.setEmulatedMedia', { features:[] });
  await cdp.evaluate(`document.querySelector('[aria-label="Send Query"]').click()`);
  await delay(300);
  assert(await cdp.evaluate(`getComputedStyle(document.querySelector('[aria-live="polite"]')).opacity==='1' && document.querySelector('.resolution-summary').textContent.includes('Billable Item Classes')`), 'Native response animation finishes with the answer visible');

  await cdp.send('Emulation.setDeviceMetricsOverride', { width:390, height:844, deviceScaleFactor:1, mobile:true });
  await cdp.send('Page.navigate', { url:'http://127.0.0.1:4173/' });
  await delay(1200);
  assert(await cdp.evaluate(`getComputedStyle(document.querySelector('.nav-actions')).display==='none' && getComputedStyle(document.querySelector('.nav-links')).display==='none'`), 'Mobile navigation remains closed initially');
  await cdp.evaluate(`document.querySelector('.mobile-menu-toggle').click()`);
  assert(await cdp.evaluate(`getComputedStyle(document.querySelector('.nav-links')).display==='flex' && document.querySelectorAll('.mobile-nav-actions a').length===1 && document.querySelector('.mobile-nav-actions a').getAttribute('href')==='/login'`), 'Mobile menu exposes only the existing Sign In action');
  await cdp.evaluate(`document.querySelector('.mobile-nav-actions a').click()`);
  await delay(800);
  assert(await cdp.evaluate(`location.pathname==='/login' && !!document.querySelector('.auth-submit-btn')`), 'Mobile Sign In still opens the login route');
  await writeFile('performance/results/load-animation-checks.json', JSON.stringify({passed:checks.length,checks},null,2));
  console.log(JSON.stringify({passed:checks.length,checks},null,2));
} finally { await cdp.close(); }
