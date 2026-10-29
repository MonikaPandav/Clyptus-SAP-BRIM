// Uses controlled HTTP/SSE test responses; never calls or changes a live backend.
import { createServer } from 'node:http';
import { mkdir, writeFile } from 'node:fs/promises';
import { connect, delay } from './cdp.mjs';

let activeStream;
let createRequest;
let creates = 0;
let streams = 0;
const responses = new Set();
const cors = { 'Access-Control-Allow-Origin': '*', 'Access-Control-Allow-Headers': '*', 'Access-Control-Allow-Methods': 'GET, POST, OPTIONS' };
const server = createServer((request, response) => {
  request.resume();
  response.writeHead(200, { ...cors, 'Content-Type': 'text/event-stream', 'Cache-Control': 'no-cache' });
  response.flushHeaders();
  responses.add(response);
  response.on('close', () => responses.delete(response));
  activeStream = response;
});
await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
const streamUrl = `http://127.0.0.1:${server.address().port}/stream`;
const cdp = await connect();
const checks = [];
const errors = [];
await cdp.send('Page.enable');
await cdp.send('Runtime.enable');
await cdp.send('Emulation.setFocusEmulationEnabled', { enabled: true });
await cdp.send('Fetch.enable', { patterns: [{ urlPattern: 'http://localhost:8000/api/*' }] });
cdp.on('Runtime.exceptionThrown', event => errors.push(event.exceptionDetails.text));

async function fulfill(requestId, value, status = 200) {
  await cdp.send('Fetch.fulfillRequest', {
    requestId, responseCode: status,
    responseHeaders: [...Object.entries(cors).map(([name,value])=>({name,value})), { name:'Content-Type',value:'application/json' }],
    body: status === 204 ? '' : Buffer.from(JSON.stringify(value)).toString('base64'),
  });
}
cdp.on('Fetch.requestPaused', event => {
  void (async () => {
    const { request, requestId } = event;
    const path = new URL(request.url).pathname;
    if (request.method === 'OPTIONS') return fulfill(requestId, {}, 204);
    if (path.endsWith('/auth/me')) return fulfill(requestId, { id:'thinking-browser-test', name:'Browser Tester', email:'thinking@example.invalid', is_admin:true });
    if (path.endsWith('/chats') && request.method === 'POST') {
      creates++;
      createRequest = requestId; // Deliberately hold creation to inspect the loading state.
      return;
    }
    if (/\/chats\/[^/]+\/messages$/.test(path) && request.method === 'POST') {
      streams++;
      await cdp.send('Fetch.continueRequest', { requestId, url:streamUrl });
      return;
    }
    return fulfill(requestId, []);
  })().catch(error => errors.push(error.message));
});

async function wait(expression, label) {
  const start = Date.now();
  while (!(await cdp.evaluate(expression))) {
    if (Date.now()-start>10000) throw new Error(`Failed: ${label}`);
    await delay(50);
  }
  checks.push(label);
}
function check(condition,label) { if (!condition) throw new Error(`Failed: ${label}`); checks.push(label); }
async function waitLocal(predicate,label) {
  const start=Date.now();
  while(!predicate()) { if(Date.now()-start>10000)throw new Error(`Failed: ${label}`); await delay(50); }
  checks.push(label);
}
const emit = event => activeStream.write(`data: ${JSON.stringify(event)}\n\n`);
async function fresh(width = 1440, reduced = false) {
  activeStream=undefined;
  createRequest=undefined;
  creates=0;
  streams=0;
  await cdp.send('Emulation.setDeviceMetricsOverride',{width,height:900,deviceScaleFactor:1,mobile:width<640});
  await cdp.send('Emulation.setEmulatedMedia',{features:reduced?[{name:'prefers-reduced-motion',value:'reduce'}]:[]});
  await cdp.send('Page.navigate',{url:'http://127.0.0.1:4173/'});
  await wait(`!!document.querySelector('.hero-main-title')`,'Landing renders');
  await cdp.evaluate(`localStorage.setItem('sap_assistant_token','browser-test-token');localStorage.removeItem('clyptus_demo_user')`);
  await cdp.send('Page.navigate',{url:'http://127.0.0.1:4173/app'});
  await wait(`!!document.querySelector('textarea') && !document.querySelector('textarea').disabled`,'Chat ready');
  check(await cdp.evaluate(`!document.querySelector('.clyptus-thinking-indicator')`),'Indicator absent when idle');
}
async function submit() {
  await cdp.evaluate(`(()=>{const input=document.querySelector('textarea');Object.getOwnPropertyDescriptor(HTMLTextAreaElement.prototype,'value').set.call(input,'Explain SAP BRIM billing.');input.dispatchEvent(new Event('input',{bubbles:true}));input.dispatchEvent(new KeyboardEvent('keydown',{key:'Enter',code:'Enter',bubbles:true}));})()`);
  await wait(`document.querySelectorAll('.clyptus-thinking-indicator').length===1`,'One branded indicator appears while chat creation waits');
  await waitLocal(()=>!!createRequest,'Exactly one chat creation request is pending');
}
async function releaseChat() {
  await fulfill(createRequest,{id:'thinking-test-chat',title:'Browser fixture',created_at:new Date().toISOString(),updated_at:new Date().toISOString()});
  await waitLocal(()=>!!activeStream,'Existing streaming endpoint connected');
}

try {
  await fresh();
  const inputBefore=await cdp.evaluate(`(()=>{const r=document.querySelector('textarea').getBoundingClientRect();return{top:r.top,height:r.height}})()`);
  await submit();
  await wait(`document.querySelector('.thinking-title').textContent==='Clyptus is thinking…'`,'Correct thinking label');
  await wait(`document.querySelector('.thinking-logo-badge img').complete && document.querySelector('.thinking-logo-badge img').naturalWidth>0`,'Existing logo asset renders');
  await wait(`document.querySelector('.clyptus-thinking-indicator').getAttribute('role')==='status' && document.querySelector('.clyptus-thinking-indicator').getAttribute('aria-live')==='polite'`,'Accessible live status');
  await wait(`getComputedStyle(document.querySelector('.thinking-sweep-ring')).animationName==='clyptus-thinking-orbit'`,'Gentle rotating orange arc is active');
  const inputDuring=await cdp.evaluate(`(()=>{const r=document.querySelector('textarea').getBoundingClientRect();return{top:r.top,height:r.height}})()`);
  check(Math.abs(inputBefore.top-inputDuring.top)<1&&Math.abs(inputBefore.height-inputDuring.height)<1,'Composer position and size unchanged');
  await wait(`getComputedStyle(document.querySelector('.clyptus-thinking-indicator')).pointerEvents==='none' && !!document.querySelector('[title="Stop generating"]')`,'Indicator does not overlay or intercept the existing input/stop controls');
  await mkdir('performance/results',{recursive:true});
  await writeFile('performance/results/thinking-desktop.png',Buffer.from((await cdp.send('Page.captureScreenshot',{format:'png'})).data,'base64'));
  await releaseChat();
  emit({type:'status',message:'Retrieving indexed references…'});
  await wait(`document.querySelector('.thinking-subtext')?.textContent==='Retrieving indexed references…'`,'Existing administrator pipeline status retained');
  emit({type:'token',content:'## BRIM response\n\n'});
  await wait(`!document.querySelector('.clyptus-thinking-indicator') && !!document.querySelector('[title="Stop generating"]')`,'Indicator hides on first response content while stream remains open');
  emit({type:'token',content:'Fixture answer.\n\n| Stage | Purpose |\n| --- | --- |\n| CI | Billing |'});
  emit({type:'done',message_id:'thinking-test-answer',source_type:'knowledge_base',grounding_score:0.98,citations:[{document:'Browser fixture manual',page:2,score:0.98,snippet:'Fixture citation.'}],web_sources:[]});
  activeStream.end();
  await wait(`!document.querySelector('textarea').disabled && !document.querySelector('.clyptus-thinking-indicator')`,'Completion removes indicator and restores existing composer state');
  await wait(`!!document.querySelector('.prose-sap h2') && !!document.querySelector('.prose-sap table')`,'Existing Markdown heading and table formatting preserved');
  await wait(`document.querySelector('[title="Admin Only: View internal sources & citations"]')?.textContent.includes('Sources (1)')`,'Existing source/citation controls preserved');
  check(creates===1&&streams===1,'No duplicate create or stream requests');

  await fresh();
  await submit();
  await releaseChat();
  emit({type:'error',message:'Fixture response unavailable.'});
  activeStream.end();
  await wait(`!document.querySelector('.clyptus-thinking-indicator') && !document.querySelector('textarea').disabled && document.body.textContent.includes('Fixture response unavailable.')`,'Stream error removes indicator and displays existing error UI');

  await fresh();
  await submit();
  await fulfill(createRequest,{detail:'Fixture create failure'},503);
  await wait(`!document.querySelector('.clyptus-thinking-indicator') && !document.querySelector('textarea').disabled`,'Chat creation failure removes indicator');
  check(creates===1&&streams===0,'Creation failure does not make a stream request');

  await fresh();
  await submit();
  await releaseChat();
  await cdp.evaluate(`document.querySelector('[title="Stop generating"]').click()`);
  await wait(`!document.querySelector('.clyptus-thinking-indicator') && !document.querySelector('textarea').disabled`,'Stop generating immediately removes indicator');

  await fresh(390,true);
  await submit();
  await wait(`['.thinking-sweep-ring','.thinking-ambient-glow'].every(selector=>getComputedStyle(document.querySelector(selector)).animationName==='none')`,'Reduced-motion preference disables both animations');
  await wait(`document.documentElement.scrollWidth<=innerWidth`,'Mobile indicator has no horizontal overflow');
  await writeFile('performance/results/thinking-mobile-reduced.png',Buffer.from((await cdp.send('Page.captureScreenshot',{format:'png'})).data,'base64'));
  await releaseChat();
  emit({type:'done',message_id:'done-only-test',answer:'Fixture final answer without streamed tokens.',citations:[],web_sources:[]});
  activeStream.end();
  await wait(`!document.querySelector('.clyptus-thinking-indicator') && !document.querySelector('textarea').disabled && document.body.textContent.includes('Fixture final answer without streamed tokens.')`,'Final-answer-only response removes indicator');
  check(errors.length===0,'No browser runtime exceptions');
  const result={passed:checks.length,checks,errors,api:'Controlled browser fixtures with a real held-open SSE stream; no live backend calls'};
  await writeFile('performance/results/thinking-indicator-checks.json',JSON.stringify(result,null,2));
  console.log(JSON.stringify(result,null,2));
} finally {
  await cdp.evaluate(`localStorage.removeItem('sap_assistant_token');localStorage.removeItem('clyptus_demo_user')`).catch(()=>{});
  await cdp.close();
  for(const response of responses)response.destroy();
  server.closeAllConnections();
  await new Promise(resolve=>server.close(resolve));
}
