// Frontend interaction test: API traffic is fulfilled with explicit test fixtures.
// This does not exercise or modify a live backend, and is not a performance test.
import { mkdir, writeFile } from 'node:fs/promises';
import { connect, delay } from './cdp.mjs';

const base = process.env.BRIM_TEST_URL ?? 'http://127.0.0.1:4173';
const smoke = process.argv.includes('--strict-smoke');
const checks = [];
const errors = [];
const cdp = await connect();
const submitted = [];
let created = 0;
const user = { id: 'brim-browser-test', name: 'Browser Tester', email: 'brim-tester@example.invalid', is_admin: false };
const headers = [
  { name: 'Access-Control-Allow-Origin', value: '*' },
  { name: 'Access-Control-Allow-Headers', value: '*' },
  { name: 'Access-Control-Allow-Methods', value: 'GET, POST, OPTIONS' },
];

await cdp.send('Page.enable');
await cdp.send('Runtime.enable');
await cdp.send('Emulation.setFocusEmulationEnabled', { enabled: true });
await cdp.send('Fetch.enable', { patterns: [{ urlPattern: 'http://localhost:8000/api/*' }] });
cdp.on('Runtime.exceptionThrown', event => errors.push(event.exceptionDetails.text));
cdp.on('Fetch.requestPaused', event => {
  void (async () => {
    const { requestId, request } = event;
    const path = new URL(request.url).pathname;
    let payload = [];
    let contentType = 'application/json';
    if (path.endsWith('/auth/me')) payload = user;
    else if (/\/auth\/(login|register|demo)$/.test(path)) payload = { access_token: 'browser-test-token', user };
    else if (path.endsWith('/chats') && request.method === 'POST') {
      const now = new Date().toISOString();
      payload = { id: `browser-test-chat-${++created}`, title: 'BRIM test', created_at: now, updated_at: now };
    } else if (/\/chats\/[^/]+\/messages$/.test(path) && request.method === 'POST') {
      submitted.push(JSON.parse(request.postData).content);
      contentType = 'text/event-stream';
      payload = [
        { type: 'token', content: 'Browser test response.' },
        { type: 'done', message_id: `browser-test-answer-${submitted.length}`, answer: 'Browser test response.', citations: [], web_sources: [] },
      ].map(event => `data: ${JSON.stringify(event)}\n\n`).join('');
    }
    await cdp.send('Fetch.fulfillRequest', {
      requestId,
      responseCode: request.method === 'OPTIONS' ? 204 : 200,
      responseHeaders: [...headers, { name: 'Content-Type', value: contentType }],
      body: request.method === 'OPTIONS' ? '' : Buffer.from(contentType === 'text/event-stream' ? payload : JSON.stringify(payload)).toString('base64'),
    });
  })().catch(error => errors.push(error.message));
});

async function wait(expression, label) {
  const started = Date.now();
  while (!(await cdp.evaluate(expression))) {
    if (Date.now() - started > 12000) throw new Error(`Failed: ${label}`);
    await delay(80);
  }
  checks.push(label);
}
async function check(condition, label) {
  if (!condition) throw new Error(`Failed: ${label}`);
  checks.push(label);
}
async function home(signedIn = true, width = 1440) {
  await cdp.send('Emulation.setDeviceMetricsOverride', { width, height: 900, deviceScaleFactor: 1, mobile: width < 640 });
  await cdp.send('Page.navigate', { url: base });
  await wait(`!!document.querySelector('.hero-main-title')`, 'Landing renders');
  await cdp.evaluate(`localStorage.removeItem('clyptus_demo_user'); localStorage.removeItem('clyptus_trial_query_count'); ${signedIn ? "localStorage.setItem('sap_assistant_token','browser-test-token')" : "localStorage.removeItem('sap_assistant_token')"}`);
  await cdp.evaluate(`location.hash = 'features'`);
  await wait(`document.querySelectorAll('[data-brim-topic]').length === 4`, 'Four BRIM question cards load');
  await check(await cdp.evaluate(`!document.body.textContent.includes('ECOSYSTEM INTEGRATION') && !document.body.textContent.includes('Connect with Your Enterprise Tools') && document.getElementById('brim-conversation-title').textContent === 'Your BRIM Landscape, Connected'`), 'New section replaces integration heading and diagram');
}
async function choose(topic) {
  const question = await cdp.evaluate(`document.querySelector('[data-brim-topic="${topic}"]').dataset.sampleQuestion`);
  await cdp.evaluate(`document.querySelector('[data-brim-topic="${topic}"]').click()`);
  return question;
}
async function confirmSubmission(question, previous) {
  const started = Date.now();
  while (submitted.length === previous) {
    if (Date.now() - started > 12000) throw new Error('No chat stream request was submitted');
    await delay(80);
  }
  await delay(500);
  await check(submitted.length === previous + 1 && submitted.at(-1) === question, 'Exact selected question submitted once to existing chat stream endpoint');
  await wait(`document.body.textContent.includes('Browser test response.') && document.body.textContent.includes(${JSON.stringify(question)})`, 'Chat displays selected question and streamed response');
}

try {
  for (const topic of smoke ? ['som'] : ['som', 'cc', 'ci', 'fica']) {
    await home();
    const previous = submitted.length;
    const question = await choose(topic);
    await confirmSubmission(question, previous);
  }
  let previous = submitted.length;
  await cdp.send('Page.reload');
  await wait(`!!document.querySelector('textarea')`, 'Chat reloads');
  await delay(600);
  await check(submitted.length === previous, 'Refresh does not resubmit consumed prompt intent');

  if (!smoke) {
    for (const mode of ['demo', 'login', 'register']) {
      await home(false);
      previous = submitted.length;
      const question = await choose('ci');
      await wait(`location.pathname === '/login' && !!document.querySelector('.auth-demo-btn')`, 'Signed-out card uses existing sign-in gate');
      await check(submitted.length === previous, 'No chat request sent before authentication');
      if (mode === 'demo') await cdp.evaluate(`document.querySelector('.auth-demo-btn').click()`);
      else {
        if (mode === 'register') await cdp.evaluate(`document.querySelectorAll('.auth-tab-btn')[1].click()`);
        await cdp.evaluate(`(() => {for (const input of document.querySelectorAll('.auth-input-field')) {const value=input.type === 'password' ? 'BrowserTest123!' : input.type === 'email' ? 'brim-tester@example.invalid' : 'Browser Tester'; Object.getOwnPropertyDescriptor(HTMLInputElement.prototype,'value').set.call(input,value);input.dispatchEvent(new Event('input',{bubbles:true}));} })()`);
        await cdp.evaluate(`document.querySelector('form').requestSubmit()`);
      }
      await confirmSubmission(question, previous);
      checks.push(`Prompt survives ${mode} flow`);
    }
    for (const width of [1440, 390]) {
      await home(true, width);
      await cdp.evaluate(`document.querySelector('.card-brim-conversation').scrollIntoView({behavior:'instant',block:'center'})`);
      await delay(900);
      await wait(`document.documentElement.scrollWidth <= innerWidth`, `No horizontal overflow at ${width}px`);
      const columns = await cdp.evaluate(`getComputedStyle(document.querySelector('.brim-conversation-grid')).gridTemplateColumns.split(' ').length`);
      await check(columns === 1, `Vertical process map at ${width}px`);
      await check(await cdp.evaluate(`document.querySelectorAll('.brim-hub-connector').length === 3`), 'All four process nodes are connected');
      await cdp.evaluate(`document.querySelector('[data-brim-topic="cc"]').focus({preventScroll:true})`);
      await wait(`document.querySelector('.brim-hub-prompt .brim-conversation-question').textContent === document.querySelector('[data-brim-topic="cc"]').dataset.sampleQuestion`, 'Keyboard focus previews the relevant question');
      await wait(`document.querySelector('[data-brim-topic="cc"]').classList.contains('is-highlighted')`, 'Focused process node is highlighted');
      const screenshot = await cdp.send('Page.captureScreenshot', { format: 'png' });
      await mkdir('performance/results', { recursive: true });
      await writeFile(`performance/results/brim-cards-${width}.png`, Buffer.from(screenshot.data, 'base64'));
    }
    await cdp.send('Emulation.setEmulatedMedia', { features: [{ name: 'prefers-reduced-motion', value: 'reduce' }] });
    await wait(`parseFloat(getComputedStyle(document.querySelector('.brim-conversation-topic')).transitionDuration) < 0.001`, 'Reduced-motion preference respected');
    await wait(`getComputedStyle(document.querySelector('.brim-hub-flow-dot')).display === 'none'`, 'Flow animations disabled for reduced motion');
    // Preserve the existing shared-prompt flow: prefill must not automatically send.
    await home(true);
    previous = submitted.length;
    await cdp.evaluate(`history.pushState({usr:{prefillPrompt:'Shared prompt remains a draft.'},key:'prefill-test',idx:1},'', '/app'); location.reload()`);
    await wait(`document.querySelector('textarea')?.value === 'Shared prompt remains a draft.'`, 'Shared prompt remains prefilled');
    await delay(500);
    await check(submitted.length === previous, 'Shared prompt is not auto-submitted');
    await home();
    previous = submitted.length;
    await cdp.evaluate(`localStorage.setItem('clyptus_demo_user', ${JSON.stringify(JSON.stringify({ ...user, isGuest: true }))});localStorage.setItem('clyptus_trial_query_count','2')`);
    await choose('fica');
    await wait(`document.body.textContent.includes("You've reached your free preview limit")`, 'Existing guest query limit still applies');
    await check(submitted.length === previous, 'Exhausted guest quota does not submit a backend question');
  }
  await check(errors.length === 0, 'No browser runtime exceptions');
  const result = { mode: smoke ? 'development StrictMode smoke' : 'production frontend integration', api: 'CDP test fixtures; no live backend calls', passed: checks.length, checks, submitted, errors };
  await mkdir('performance/results', { recursive: true });
  await writeFile(`performance/results/brim-cards-${smoke ? 'strict' : 'checks'}.json`, JSON.stringify(result, null, 2));
  console.log(JSON.stringify(result, null, 2));
} finally {
  await cdp.evaluate(`localStorage.removeItem('sap_assistant_token');localStorage.removeItem('clyptus_demo_user');localStorage.removeItem('clyptus_trial_query_count')`).catch(() => {});
  await cdp.close();
}
