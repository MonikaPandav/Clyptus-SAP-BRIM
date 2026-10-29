import { mkdir, writeFile } from 'node:fs/promises';
import { connect, delay } from './cdp.mjs';

const cdp = await connect();
const results = [];
const errors = [];
cdp.on('Runtime.exceptionThrown', e => errors.push(e.exceptionDetails.text));
await cdp.send('Page.enable');
await cdp.send('Runtime.enable');
await cdp.send('Emulation.setFocusEmulationEnabled', { enabled: true });
await mkdir('performance/results', { recursive: true });
try {
  for (const width of [1440, 1280, 1024, 390, 320]) {
    const pair = {};
    await cdp.send('Emulation.setDeviceMetricsOverride', { width, height: 900, deviceScaleFactor: 1, mobile: width < 640 });
    for (const [label, port] of [['before', 4174], ['after', 4173]]) {
      await cdp.send('Page.navigate', { url: `http://127.0.0.1:${port}/#features` });
      const started = Date.now();
      while (!(await cdp.evaluate(`!!document.querySelector('.brim-hub-map')`))) {
        if (Date.now() - started > 10000) throw new Error('Hub did not render');
        await delay(80);
      }
      await cdp.evaluate(`document.querySelector('.card-brim-conversation').scrollIntoView({behavior:'instant',block:'center'})`);
      await delay(900);
      pair[label] = await cdp.evaluate(`(()=>{
        const rect = selector => {const e=document.querySelector(selector),r=e.getBoundingClientRect();return {x:r.x,y:r.y+scrollY,width:r.width,height:r.height}};
        const text = selector => document.querySelector(selector).textContent.replace(/\s/g,'');
        return {left:rect('.card-multi-user'),right:rect('.card-brim-conversation'),map:rect('.brim-hub-map'),leftContent:text('.card-multi-user'),rightContent:text('.card-brim-conversation'),overflow:document.documentElement.scrollWidth>innerWidth,stages:[...document.querySelectorAll('[data-brim-topic]')].map(e=>({id:e.dataset.brimTopic,question:e.dataset.sampleQuestion,text:e.textContent.replace(/\s/g,''),overflow:e.scrollWidth>e.clientWidth+1||e.scrollHeight>e.clientHeight+1})),iconSize:document.querySelector('.brim-conversation-icon').offsetWidth,connectorHeight:document.querySelector('.brim-hub-connector').offsetHeight};
      })()`);
      if (label === 'after' && (width === 1440 || width === 390)) {
        const clip = await cdp.evaluate(`(()=>{const hub=document.querySelector('.card-brim-conversation'),left=document.querySelector('.card-multi-user');const r=(innerWidth>1024?document.querySelector('.possibilities-grid'):hub).getBoundingClientRect();return{x:r.x,y:(innerWidth>1024?left:hub).getBoundingClientRect().top+scrollY,width:r.width,height:hub.offsetHeight,scale:1}})()`);
        await writeFile(`performance/results/balanced-cards-${width}.png`, Buffer.from((await cdp.send('Page.captureScreenshot', { format: 'png', captureBeyondViewport: true, clip })).data, 'base64'));
      }
    }
    const { before, after } = pair;
    if (before.leftContent !== after.leftContent || before.rightContent !== after.rightContent) throw new Error(`Content changed at ${width}px`);
    if (after.stages.length !== 4 || after.stages.some(stage => stage.overflow) || after.overflow) throw new Error(`Overflow or missing stage at ${width}px`);
    if (JSON.stringify(before.stages.map(({overflow,...stage})=>stage)) !== JSON.stringify(after.stages.map(({overflow,...stage})=>stage))) throw new Error('Stage content or question changed');
    if (after.right.height > before.right.height * 0.85) throw new Error(`Insufficient size reduction at ${width}px`);
    if (width > 1024 && (Math.abs(after.left.height-after.right.height)>1 || Math.abs(after.left.y-after.right.y)>1 || Math.abs(after.left.width-after.right.width)>1)) throw new Error('Desktop cards are not aligned');
    const result = { width, beforeHeight: before.right.height, afterHeight: after.right.height, reductionPercent: Math.round((1-after.right.height/before.right.height)*100), equalDesktopCards: width>1024, noOverflow:true, contentUnchanged:true, iconSize:after.iconSize, connectorHeight:after.connectorHeight };
    results.push(result);
    console.log(JSON.stringify(result));
  }
  if (errors.length) throw new Error(errors.join('; '));
  await writeFile('performance/results/card-balance-checks.json', JSON.stringify({results,errors},null,2));
} finally {
  await cdp.close();
}
