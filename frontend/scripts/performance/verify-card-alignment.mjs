import { mkdir, writeFile } from 'node:fs/promises';
import { connect, delay } from './cdp.mjs';

const cdp = await connect();
const checks = [];
const measurements = [];
await cdp.send('Page.enable');
await cdp.send('Runtime.enable');
await cdp.send('Emulation.setFocusEmulationEnabled', { enabled: true });
await mkdir('performance/results', { recursive: true });
function check(condition, label) {
  if (!condition) throw new Error(`Failed: ${label}`);
  checks.push(label);
}
async function wait(expression, label) {
  const start = Date.now();
  while (!(await cdp.evaluate(expression))) {
    if (Date.now()-start>10000) throw new Error(`Failed: ${label}`);
    await delay(80);
  }
  checks.push(label);
}
async function home() {
  await cdp.send('Page.navigate', { url: 'http://127.0.0.1:4173/#features' });
  await wait(`!!document.querySelector('.brim-hub-map')`, 'Hub loads');
  await cdp.evaluate(`document.querySelector('.card-brim-conversation').scrollIntoView({behavior:'instant',block:'center'})`);
  await delay(800);
}

try {
  for (const width of [1440,1280,1024,768,390,320]) {
    await cdp.send('Emulation.setDeviceMetricsOverride', { width, height:900,deviceScaleFactor:1,mobile:width<640 });
    await home();
    const layout=await cdp.evaluate(`(()=>{
      const rect=e=>{const r=e.getBoundingClientRect();return{x:r.x,y:r.y,width:r.width,height:r.height,right:r.right,bottom:r.bottom}};
      const left=document.querySelector('.card-multi-user'),right=document.querySelector('.card-brim-conversation'),header=left.querySelector('.card-top-content'),details=left.querySelector('.card-multi-user-visual');
      const stages=[...document.querySelectorAll('[data-brim-topic]')];
      return {width:innerWidth,left:rect(left),right:rect(right),gap:rect(details).y-rect(header).bottom,leftBottomGap:rect(left).bottom-rect(details).bottom,leftPadding:parseFloat(getComputedStyle(left).paddingBottom),overflow:document.documentElement.scrollWidth>innerWidth,stages:stages.map(e=>({id:e.dataset.brimTopic,height:e.offsetHeight,question:e.dataset.sampleQuestion,overflow:e.scrollWidth>e.clientWidth+1||e.scrollHeight>e.clientHeight+1,iconX:rect(e.querySelector('.brim-conversation-icon')).x+rect(e.querySelector('.brim-conversation-icon')).width/2,codeOverlaps:rect(e.querySelector('.brim-hub-code')).x<rect(e.querySelector('.brim-hub-node-meta > span:first-child')).right})),connectors:[...document.querySelectorAll('.brim-hub-connector')].map(e=>({gap:rect(e).y-rect(e.previousElementSibling).bottom,height:rect(e).height,iconX:rect(e.querySelector('svg')).x+rect(e.querySelector('svg')).width/2})),nodeOverlap:stages.some((e,i)=>i>0&&rect(e).y<rect(stages[i-1]).bottom)};
    })()`);
    check(Math.abs(layout.gap-16)<1, `Team details follow description with a 16px gap at ${width}px`);
    check(Math.abs(layout.leftBottomGap-layout.leftPadding-1)<1, `Access card has no forced empty height at ${width}px`);
    check(!layout.overflow && !layout.nodeOverlap, `No page overflow or overlapping nodes at ${width}px`);
    check(layout.stages.length===4 && layout.stages.every(s=>!s.overflow&&!s.codeOverlaps), `Four stages retain unclipped text and aligned labels at ${width}px`);
    check(Math.max(...layout.stages.map(s=>s.height))-Math.min(...layout.stages.map(s=>s.height))<=1, `Stage boxes use equal intrinsic row heights at ${width}px`);
    check(layout.connectors.every((c,i)=>Math.abs(c.gap)<1&&Math.abs(c.iconX-layout.stages[i].iconX)<1&&Math.abs(c.height-20)<1), `Connectors align with icons and fill the 20px row gap at ${width}px`);
    if(width>1024)check(Math.abs(layout.left.y-layout.right.y)<1&&Math.abs(layout.left.width-layout.right.width)<1, `Desktop cards align at the top with equal column widths at ${width}px`);
    if(width===1440||width===390){
      const clip=await cdp.evaluate(`(()=>{const r=document.querySelector(innerWidth>1024?'.possibilities-grid':'.card-brim-conversation').getBoundingClientRect();return{x:r.x,y:r.y+scrollY,width:r.width,height:document.querySelector('.card-brim-conversation').offsetHeight,scale:1}})()`);
      await writeFile(`performance/results/refined-cards-${width}.png`,Buffer.from((await cdp.send('Page.captureScreenshot',{format:'png',captureBeyondViewport:true,clip})).data,'base64'));
    }
    measurements.push(layout);
    console.log(JSON.stringify({width,leftHeight:layout.left.height,rightHeight:layout.right.height,detailsGap:layout.gap,stageHeight:layout.stages[0].height}));
  }
  // Verify actual node navigation and the existing prompt handoff, without calling a backend.
  for (const topic of ['som','cc','ci','fica']) {
    await home();
    await cdp.evaluate(`localStorage.removeItem('sap_assistant_token');localStorage.removeItem('clyptus_demo_user')`);
    const question=await cdp.evaluate(`document.querySelector('[data-brim-topic="${topic}"]').dataset.sampleQuestion`);
    await cdp.evaluate(`document.querySelector('[data-brim-topic="${topic}"]').focus({preventScroll:true})`);
    await wait(`document.querySelector('.brim-conversation-question').textContent===${JSON.stringify(question)}`, `${topic} focus previews correct question`);
    await cdp.evaluate(`document.querySelector('[data-brim-topic="${topic}"]').click()`);
    await wait(`location.pathname==='/login' && history.state?.usr?.chatPromptState?.submitPrompt===${JSON.stringify(question)}`, `${topic} click preserves existing chatbot prompt handoff`);
  }
  await writeFile('performance/results/card-alignment-checks.json', JSON.stringify({passed:checks.length,checks,measurements},null,2));
  console.log(JSON.stringify({passed:checks.length}));
} finally { await cdp.close(); }
