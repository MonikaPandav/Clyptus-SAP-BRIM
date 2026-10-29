import { writeFile, mkdir } from 'node:fs/promises';
import { connect, delay } from './cdp.mjs';

await mkdir('performance/results', { recursive: true });
const cdp = await connect();
const checks = [];
const exceptions = [];
const requests = [];
cdp.on('Runtime.exceptionThrown', e => exceptions.push(e.exceptionDetails.text));
cdp.on('Network.requestWillBeSent', e => requests.push(e.request.url));
await cdp.send('Page.enable');
await cdp.send('Runtime.enable');
await cdp.send('Emulation.setFocusEmulationEnabled', { enabled: true });
await cdp.send('Network.enable');
await cdp.send('Network.setCacheDisabled', {cacheDisabled:true});
await cdp.send('Emulation.setDeviceMetricsOverride', {width:1440,height:900,deviceScaleFactor:1,mobile:false});
await cdp.send('Browser.grantPermissions', {origin:'http://127.0.0.1:4173',permissions:['clipboardReadWrite','clipboardSanitizedWrite']});

async function wait(expression, label) {
  const started = Date.now();
  while (!(await cdp.evaluate(expression))) {
    if (Date.now()-started>10000) throw new Error(`Failed: ${label}`);
    await delay(80);
  }
  checks.push(label);
}
const click = expression => cdp.evaluate(`(${expression}).click()`);
const icon = name => `document.querySelector('.sidebar-dock-icons button[aria-label="${name}"]')`;
const panel = name => `document.querySelector('[aria-label="${name} preview"]')`;
async function selectPanel(name) {
  await click(icon(name));
  await wait(`${panel(name)} && !${panel(name)}.hidden && ${icon(name)}.getAttribute('aria-pressed') === 'true'`, `${name} opens and is selected`);
  await wait(`document.querySelectorAll('.sidebar-dock-icons .active').length === 1`, 'Exactly one sidebar icon selected');
}

try {
  await cdp.send('Page.navigate',{url:'http://127.0.0.1:4173/'});
  await wait(`!!document.querySelector('.hero-main-title')`, 'Landing page renders');
  await delay(1800);
  if (requests.some(url=>/\/api\/|vendor-markdown|\/lib-[^/]+\.js|AdminDashboard|ChatPage-|AuthContext|LandingSections|PreviewResourcePanels/.test(url))) {
    throw new Error('Non-critical resources fetched on initial landing navigation: '+requests.filter(url=>/\/api\/|vendor-markdown|AdminDashboard|ChatPage-|AuthContext|LandingSections|PreviewResourcePanels/.test(url)).join(', '));
  }
  checks.push('No API, authenticated routes, Markdown, lower sections or secondary panels loaded initially');
  await selectPanel('Documents');
  await wait(`document.querySelectorAll('.resource-document').length === 4`, 'Four document references available');
  await cdp.evaluate(`(() => {const input=document.querySelector('[aria-label="Search preview documents"]');Object.getOwnPropertyDescriptor(HTMLInputElement.prototype,'value').set.call(input,'FI-CA');input.dispatchEvent(new Event('input',{bubbles:true}));})()`);
  await wait(`document.querySelectorAll('.resource-document').length === 1`, 'Document search filters references');
  await click(`document.querySelector('.resource-document')`);
  await wait(`${panel('Documents')}.textContent.includes('clearing lock or payment lock')`, 'Selected document excerpt changes');
  await selectPanel('Chat');
  await wait(`${panel('Chat')}.textContent.includes('clearing lock or payment lock')`, 'Document selection updates chat scenario');
  await selectPanel('Documents');
  await wait(`document.querySelector('[aria-label="Search preview documents"]').value === 'FI-CA'`, 'Document search preserved when switching panels');
  await selectPanel('Workflows');
  await wait(`${panel('Workflows')}.textContent.includes('Clearing Control')`, 'Workflow matches selected scenario');
  await click(`document.querySelector('[title="Copy workflow SPRO path"]')`);
  await wait(`document.querySelector('[title="Copy workflow SPRO path"]').textContent.includes('Copied')`, 'Workflow copy action confirms');
  await wait(`navigator.clipboard.readText().then(text=>text.includes('Clearing Control'))`, 'Clipboard contains actual SPRO path');
  await selectPanel('Database');
  await wait(`document.querySelectorAll('.resource-table tbody tr').length === 4`, 'Four database records available');
  await click(`document.querySelectorAll('.resource-table tbody button')[2]`);
  await wait(`${panel('Database')}.textContent.includes('som-sync') && document.querySelector('.resource-table tr.active').textContent.includes('SOM Contract Sync')`, 'Database record selection updates details');
  await click(`${panel('Database')}.querySelector('.scenario-btn')`);
  await wait(`!${panel('Chat')}.hidden && ${panel('Chat')}.textContent.includes('ODI')`, 'Open in Chat restores selected record');
  const summaries = ['Billable Item Classes define', 'standard SAP BRIM flow', 'Subscription Orders captured', 'Items are excluded'];
  for (let index=0;index<4;index++) {
    await click(`document.querySelectorAll('.sidebar-module-list .scenario-btn')[${index}]`);
    await wait(`${panel('Chat')}.textContent.includes(${JSON.stringify(summaries[index])})`, `Scenario ${index+1} displays correct chat answer`);
  }
  await click(`document.querySelector('[aria-label="Send Query"]')`);
  await delay(250);
  await wait(`!${panel('Chat')}.hidden && document.querySelector('.resolution-summary').textContent.includes('Items are excluded')`, 'Send Query keeps answer mounted');
  await click(`document.querySelector('.nav-links a[href="/#faq"]')`);
  await wait(`!!document.getElementById('faq')`, 'FAQ navigation loads deferred sections');
  await delay(1700);
  await wait(`Math.abs(document.getElementById('faq').getBoundingClientRect().top - 90) < 120`, 'FAQ anchor scrolls to correct section');
  await click(`document.querySelectorAll('.faq-question-btn')[1]`);
  await wait(`document.querySelectorAll('.faq-question-btn')[1].getAttribute('aria-expanded') === 'true'`, 'FAQ accordion remains interactive');
  await cdp.send('Page.navigate',{url:'http://127.0.0.1:4173/#about'});
  await wait(`!!document.getElementById('about')`, 'Direct About hash loads section');
  await delay(1700);
  await wait(`scrollX === 0 && scrollY === 0`, 'Direct About view starts at page top');
  await cdp.send('Page.navigate',{url:'http://127.0.0.1:4173/features'});
  await wait(`!!document.querySelector('.inner-hero')`, 'Features route loads lazily');
  await cdp.send('Page.navigate',{url:'http://127.0.0.1:4173/how-it-works'});
  await wait(`!!document.querySelector('.inner-hero')`, 'How it works route loads lazily');
  await cdp.send('Page.navigate',{url:'http://127.0.0.1:4173/login'});
  await wait(`!!document.querySelector('.auth-submit-btn')`, 'Login and lazy auth stylesheet load');
  await wait(`getComputedStyle(document.querySelector('.auth-card-panel')).borderRadius === '22px'`, 'Login styling preserved');
  await cdp.send('Page.navigate',{url:'http://127.0.0.1:4173/app'});
  await wait(`location.pathname === '/login' && !!document.querySelector('.auth-submit-btn')`, 'Protected chat redirects unauthenticated users');
  await cdp.send('Page.navigate',{url:'http://127.0.0.1:4173/admin/login'});
  await wait(`!!document.querySelector('input[type="password"]')`, 'Admin login loads');
  await cdp.send('Emulation.setDeviceMetricsOverride', {width:390,height:844,deviceScaleFactor:1,mobile:true});
  await cdp.send('Page.navigate',{url:'http://127.0.0.1:4173/'});
  await wait(`!!document.querySelector('.hero-main-title')`, 'Mobile landing renders');
  await delay(1200);
  await wait(`document.documentElement.scrollWidth <= innerWidth`, 'Mobile viewport has no horizontal overflow');
  await wait(`getComputedStyle(document.querySelector('.sidebar-dock-icons')).display !== 'none'`, 'All sidebar icons accessible on mobile');
  for (const name of ['Documents','Workflows','Database','Chat']) await selectPanel(name);
  await cdp.evaluate(`document.querySelector('.showcase-sidebar').scrollIntoView({behavior:'instant'})`);
  await delay(500);
  await writeFile('performance/results/mobile.png', Buffer.from((await cdp.send('Page.captureScreenshot',{format:'png'})).data,'base64'));
  // A saved session must not cause a landing-page API/database request.
  await cdp.evaluate(`localStorage.setItem('sap_assistant_token','performance-test-token')`);
  requests.length = 0;
  await cdp.send('Page.navigate',{url:'http://127.0.0.1:4173/'});
  await wait(`!!document.querySelector('.hero-main-title')`, 'Landing with saved token renders');
  await delay(1200);
  if (requests.some(url=>url.includes('/api/'))) throw new Error('Landing with saved token makes API requests');
  checks.push('Landing with saved token does not access API/database/RAG');
  await cdp.evaluate(`localStorage.removeItem('sap_assistant_token')`);
  if (exceptions.length) throw new Error(`Runtime errors: ${exceptions.join('; ')}`);
  console.log(JSON.stringify({passed:checks.length, checks, exceptions},null,2));
  await writeFile('performance/results/functional-checks.json',JSON.stringify({passed:checks.length,checks,exceptions},null,2));
} finally {
  await cdp.close();
}
