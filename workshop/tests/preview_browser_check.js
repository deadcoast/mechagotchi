"use strict";
// Bounded foreground Chromium acceptance with real HTTP and engine results.
// Only explicitly armed delivery hooks ignore cancellation, hold actual responses,
// or simulate a network outage. They do not replace successful response bodies.
const fs=require("node:fs/promises"),path=require("node:path"),os=require("node:os"),assert=require("node:assert/strict"),{spawn}=require("node:child_process");
const root=path.resolve(__dirname,"../..");
const output=path.resolve(process.argv[2]||path.join(root,".development/preview-consistency/browser-"+Date.now()));
const browserPath=process.env.MECHA_BROWSER||"C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe";
const checks=[],exceptions=[],httpEvidence=[];let browser,host,ws,timer,diagnostics,screenshotFailure;
let hostOutput="",hostError="",browserError="",scratch;
const wait=ms=>new Promise(r=>setTimeout(r,ms));
async function until(fn,label,timeout=15000){const end=Date.now()+timeout;while(Date.now()<end){try{const value=await fn();if(value)return value;}catch{}await wait(40);}throw new Error("Timed out: "+label);}
const probeSource=`(()=>{
 const original=window.fetch.bind(window), probe=window.__probe={records:[],rules:[],held:{},counter:0};
 probe.release=id=>{const release=probe.held[id];delete probe.held[id];release();};
 window.fetch=async(input,options={})=>{
  const url=typeof input==='string'?input:input.url, i=probe.rules.findIndex(rule=>url===rule.url), rule=i<0?null:probe.rules.splice(i,1)[0];
  if(rule?.reject)throw new Error('Instrumented temporary connection failure');
  const actual={...options};if(rule?.hold)delete actual.signal;
  if(rule?.bodyPatch)actual.body=JSON.stringify({...JSON.parse(actual.body),...rule.bodyPatch});
  const row={id:++probe.counter,url,payload:actual.body?JSON.parse(actual.body):null,held:!!rule?.hold};probe.records.push(row);
  const response=await original(input,actual);row.status=response.status;
  try{row.result=await response.clone().json();}catch{}
  if(rule?.hold)await new Promise(resolve=>{probe.held[rule.tag||String(row.id)]=resolve;});
  row.delivered=true;return response;
 };
 if(new URLSearchParams(location.search).has('probe_fail_context'))probe.rules.push({url:'/api/context',reject:true});
})();`;
async function run(){
 await fs.mkdir(output,{recursive:true});console.log("Evidence: "+output);scratch=await fs.mkdtemp(path.join(os.tmpdir(),"mecha-preview-browser-"));
 host=spawn(path.join(root,".venv/Scripts/python.exe"),["-B",path.join(__dirname,"preview_browser_server.py"),path.join(scratch,"data")],{cwd:root,windowsHide:true,stdio:["pipe","pipe","pipe"]});
 host.stdout.on("data",data=>hostOutput+=data);host.stderr.on("data",data=>hostError+=data);
 const rows=()=>hostOutput.split(/\r?\n/).filter(line=>line.startsWith('{"port"')).map(line=>JSON.parse(line));
 const ready=await until(()=>rows().find(row=>row.event==="ready"),"fixture host",60000);
 let commandSequence=0;
 const fixture=async(op,params={})=>{const sequence=++commandSequence;host.stdin.write(JSON.stringify({op,sequence,...params})+"\n");return until(()=>rows().find(row=>row.sequence===sequence),"fixture "+op);};
 const profile=path.join(scratch,"browser-profile");
 browser=spawn(browserPath,["--headless=new","--remote-debugging-address=127.0.0.1","--remote-debugging-port=0","--user-data-dir="+profile,"--no-first-run","--no-default-browser-check","about:blank"],{windowsHide:true,stdio:["ignore","ignore","pipe"]});
 browser.stderr.on("data",data=>browserError+=data);
 const port=await until(async()=>Number((await fs.readFile(path.join(profile,"DevToolsActivePort"),"utf8")).split("\n")[0]),"isolated Chromium endpoint");
 const targets=await(await fetch(`http://127.0.0.1:${port}/json/list`)).json();ws=new WebSocket(targets.find(target=>target.type==="page").webSocketDebuggerUrl);
 await new Promise((resolve,reject)=>{ws.onopen=resolve;ws.onerror=reject;});
 let sequence=0;const pending=new Map();
 ws.onmessage=event=>{const msg=JSON.parse(event.data);if(msg.id){const item=pending.get(msg.id);pending.delete(msg.id);if(!item)return;clearTimeout(item.timer);if(msg.error)item.reject(new Error(JSON.stringify(msg.error)));else item.resolve(msg.result);}else if(msg.method==="Runtime.exceptionThrown")exceptions.push(msg.params.exceptionDetails);};
 ws.onclose=()=>{for(const item of pending.values()){clearTimeout(item.timer);item.reject(new Error("Browser closed"));}pending.clear();};
 const send=(method,params={})=>new Promise((resolve,reject)=>{if(ws.readyState!==1)return reject(new Error("Browser closed"));const id=++sequence,timer=setTimeout(()=>{pending.delete(id);reject(new Error("CDP timed out: "+method));},20000);pending.set(id,{resolve,reject,timer});ws.send(JSON.stringify({id,method,params}));});
 const evaluate=async expression=>{const result=await send("Runtime.evaluate",{expression,returnByValue:true,awaitPromise:true});if(result.exceptionDetails)throw new Error(result.exceptionDetails.exception?.description||result.exceptionDetails.text);return result.result.value;};
 const waitFor=(expression,label,timeout)=>until(()=>evaluate(expression),label,timeout);
 diagnostics=()=>evaluate("({url:location.href,text:document.body.innerText,context:typeof selectedContext!=='undefined'?selectedContext.data:null,revision:typeof pickRevision!=='undefined'?pickRevision:null,requests:window.__probe?.records})");
 const check=async(name,fn)=>{await fn();checks.push(name);console.log("PASS "+name);};
 const key=async(key,code=key,modifiers=0)=>{await send("Input.dispatchKeyEvent",{type:"keyDown",key,code,modifiers,windowsVirtualKeyCode:({Enter:13," ":32,Escape:27,Tab:9,Home:36,End:35,ArrowLeft:37,ArrowUp:38,ArrowRight:39,ArrowDown:40}[key]||(key.length===1?key.toUpperCase().charCodeAt(0):0))});await send("Input.dispatchKeyEvent",{type:"keyUp",key,code,modifiers});};
 const click=async selector=>{const point=await evaluate(`(()=>{const el=document.querySelector(${JSON.stringify(selector)});el.scrollIntoView({block:'center'});const r=el.getBoundingClientRect();return {x:r.x+r.width/2,y:r.y+r.height/2}})()`);await send("Input.dispatchMouseEvent",{type:"mousePressed",button:"left",clickCount:1,...point});await send("Input.dispatchMouseEvent",{type:"mouseReleased",button:"left",clickCount:1,...point});};
 const select=async(selector,value)=>{const index=await evaluate(`(()=>{const el=document.querySelector(${JSON.stringify(selector)});el.focus();return [...el.options].findIndex(o=>o.value===${JSON.stringify(value)})})()`);assert.ok(index>=0);await key("ArrowDown","ArrowDown",1);await key("Home");for(let i=0;i<index;i++)await key("ArrowDown");await key("Enter");};
 const fill=async(selector,value)=>{await evaluate(`document.querySelector(${JSON.stringify(selector)}).focus()`);await key("a","KeyA",2);await send("Input.insertText",{text:value});};
 const screenshot=async(name,selector)=>{if(selector)await evaluate(`document.querySelector(${JSON.stringify(selector)}).scrollIntoView({block:'center'})`);const data=await send("Page.captureScreenshot",{format:"png",captureBeyondViewport:false});await fs.writeFile(path.join(output,name+".png"),Buffer.from(data.data,"base64"));};
 screenshotFailure=()=>screenshot("failure");
 const base=`http://127.0.0.1:${ready.port}`;
 const readyExpression="typeof selectedDocument!=='undefined'&&selectedDocument&&document.querySelector('#portrait-tag').textContent.includes(selectedDocument.grid.grid_id)&&!document.querySelector('#live-btn').disabled";
 const settled=()=>waitFor(readyExpression,"usable exact preview document",120000);
 const navigate=async url=>{await send("Page.navigate",{url});await settled();};
 const arm=rule=>evaluate(`__probe.rules.push(${JSON.stringify(rule)})`);
 const held=tag=>waitFor(`!!__probe.held[${JSON.stringify(tag)}]`,"held real response "+tag,120000);
 const release=tag=>evaluate(`__probe.release(${JSON.stringify(tag)})`);
 const last=route=>evaluate(`__probe.records.findLast(row=>row.url===${JSON.stringify(route)}&&row.result)`);
 const cleared=async()=>{assert.equal(await evaluate("!!document.querySelector('#kids-body .gallery canvas')"),false);assert.equal(await evaluate("!!document.querySelector('#live-body .cycle-card')"),false);assert.equal(await evaluate("!!document.querySelector('#replay-body input[type=range]')"),false);};
 const setBounds=async()=>{for(const kind of ["live","replay"]){await fill("#"+kind+"-cycles","1");await fill("#"+kind+"-ticks","8");}};
 const runLive=async()=>{await click("#live-btn");await waitFor("document.querySelector('#live-body .cycle-card')&&!document.querySelector('#live-btn').disabled","real live result",120000);return last("/api/preview/live");};
 const runReplay=async()=>{await click("#replay-btn");await waitFor("document.querySelector('#replay-body input[type=range]')&&!document.querySelector('#replay-btn').disabled","real replay result",120000);return last("/api/preview/replay");};
 const saveHttp=async label=>httpEvidence.push({label,records:await evaluate("__probe.records")});
 await send("Page.enable");await send("Runtime.enable");await send("Page.addScriptToEvaluateOnNewDocument",{source:probeSource});await send("Emulation.setDeviceMetricsOverride",{width:1100,height:900,deviceScaleFactor:1,mobile:false});
 await navigate(base+"/preview");await setBounds();let workloadLive,workloadReplay,legacyReplay;
 await check("native model is visible and real live/replay requests bind authoritative workload context",async()=>{
  assert.equal(await evaluate("selectedContext.data.body_response"),"workload-v1");assert.ok(await evaluate("document.querySelector('.context-panel').textContent.includes('workload-v1')"));
  await select("#profile-select","__embedded__");await settled();await select("#profile-select","__active__");await settled();
  workloadLive=await runLive();workloadReplay=await runReplay();
  for(const row of [workloadLive,workloadReplay]){assert.equal(row.result.body_response,"workload-v1");assert.equal(row.result.preview_identity.body_response,"workload-v1");assert.equal(row.payload.context_id,row.result.context_id);assert.equal(row.payload.expected_context_revision,row.result.context_revision);}
  assert.deepEqual(workloadReplay.result.replay.live.final_state,workloadLive.result.report.final_state);assert.deepEqual(workloadReplay.result.replay.live.cycles,workloadLive.result.report.cycles);
  assert.ok(await evaluate("document.querySelector('#replay-body').textContent.includes('workload-v1')"));assert.ok(await evaluate("document.querySelector('#replay-body').textContent.includes('not original Keeper footage')"));
  await screenshot("workload-context",".context-panel");await screenshot("workload-live","#live-body");await screenshot("workload-replay","#replay-body");await fill("#kids-count","1");await click("#kids-btn");await waitFor("document.querySelector('#kids-body .gallery canvas')","actual offspring result",120000);
 });
 await check("keyboard scrub and repeated Record stop obsolete playback and retain deterministic identity",async()=>{
  await evaluate("document.querySelector('#replay-body input[type=range]').focus()");await key("ArrowRight");assert.equal(await evaluate("document.querySelector('#replay-body input[type=range]').value"),"1");
  await click("#replay-body button");assert.equal(await evaluate("!!replayState.timer"),true);await evaluate("window.__oldReplayState=replayState");
  await arm({url:"/api/preview/replay",hold:true,tag:"repeat"});await click("#replay-btn");await held("repeat");assert.equal(await evaluate("__oldReplayState.timer"),null);await release("repeat");await waitFor("document.querySelector('#replay-body input[type=range]')","repeat replay");
  const repeated=await last("/api/preview/replay");assert.equal(repeated.result.replay.replay_id,workloadReplay.result.replay.replay_id);assert.deepEqual(repeated.result.replay.frames,workloadReplay.result.replay.frames);
 });
 await check("changing replay inputs invalidates a delayed result and versions the replacement identity",async()=>{
  await arm({url:"/api/preview/replay",hold:true,tag:"changed-input"});await click("#replay-btn");await held("changed-input");await fill("#replay-ticks","9");await release("changed-input");await wait(150);assert.equal(await evaluate("!!document.querySelector('#replay-body input[type=range]')"),false);
  const changed=await runReplay();assert.equal(changed.result.replay.parameters.ticks,9);assert.notEqual(changed.result.replay.replay_id,workloadReplay.result.replay.replay_id);await fill("#replay-ticks","8");await runReplay();
 });
 await check("refresh immediately removes all displayed results and portrait while authority is pending",async()=>{
  await arm({url:"/api/context",hold:true,tag:"refresh"});await click("#context-refresh");await held("refresh");await cleared();assert.equal(await evaluate("selectedDocument"),null);
  assert.equal(await evaluate("[...document.querySelector('#portrait').getContext('2d').getImageData(0,0,256,256).data].every(value=>value===0)"),true);await screenshot("refresh-pending",".context-panel");await release("refresh");await settled();
 });
 await check("completed workload result delayed until after an external model switch cannot display as current",async()=>{
  await arm({url:"/api/preview/live",hold:true,tag:"external-switch"});await click("#live-btn");await held("external-switch");await fixture("switch",{body_response:"legacy"});await release("external-switch");
  await waitFor("!document.querySelector('#live-btn').disabled || !selectedDocument","delayed result disposition",30000);await cleared();
  await click("#context-refresh");await settled();assert.equal(await evaluate("selectedContext.data.body_response"),"legacy");assert.ok(await evaluate("document.querySelector('.context-panel').textContent.includes('legacy')"));
  const live=await runLive();legacyReplay=await runReplay();assert.equal(live.result.body_response,"legacy");assert.deepEqual(legacyReplay.result.replay.live.final_state,live.result.report.final_state);
  assert.notEqual(legacyReplay.result.replay.replay_id,workloadReplay.result.replay.replay_id);assert.notDeepEqual(live.result.preview_identity,workloadLive.result.preview_identity);
  assert.notEqual(live.result.report.cycles[0].episode.need_balance,workloadLive.result.report.cycles[0].episode.need_balance);await screenshot("legacy-switched-replay","#replay-body");
 });
 await check("latest overlapping context refresh wins after actual new-life model transition",async()=>{
  await arm({url:"/api/context",hold:true,tag:"older-context"});await evaluate("void selectedContext.refresh().catch(()=>{})");await held("older-context");await fixture("switch",{body_response:"workload-v1"});
  await evaluate("void selectedContext.refresh().catch(()=>{})");await settled();assert.equal(await evaluate("selectedContext.data.body_response"),"workload-v1");await release("older-context");await wait(150);assert.equal(await evaluate("selectedContext.data.body_response"),"workload-v1");await cleared();
 });
 await check("obsolete real HTTP error cannot replace fresh context status or results",async()=>{
  await arm({url:"/api/preview/replay",bodyPatch:{body_response:"malformed-browser-assertion"},hold:true,tag:"obsolete-error"});await click("#replay-btn");await held("obsolete-error");const error=await last("/api/preview/replay");assert.ok(error.status>=400);
  await fixture("advance");await click("#context-refresh");await settled();await release("obsolete-error");await wait(150);await cleared();assert.equal(await evaluate("document.querySelector('#replay-body .err')!==null"),false);await runReplay();
 });
 await check("malformed request assertion produces visible refusal and normal retry succeeds",async()=>{
  await arm({url:"/api/preview/live",bodyPatch:{body_response:{malformed:true}}});await click("#live-btn");await waitFor("document.querySelector('#live-body .err')&&!document.querySelector('#live-btn').disabled","malformed assertion refusal");assert.ok((await last("/api/preview/live")).status>=400);await runLive();
 });
 await check("native profile selection displays actual engine incompatibility refusal for live and replay",async()=>{
  await select("#profile-select","preview_incompatible_palette");await settled();
  for(const kind of ["live","replay"]){await click("#"+kind+"-btn");await waitFor(`document.querySelector('#${kind}-body').textContent.includes('engine will not run')&&!document.querySelector('#${kind}-btn').disabled`,"actual "+kind+" alignment refusal");const row=await last("/api/preview/"+kind);assert.equal(row.status,200);assert.equal(row.result.ok,false);assert.equal(await evaluate(`document.querySelector('#${kind}-body').textContent.includes('model identity')`),false);}
  await screenshot("engine-profile-refusal","#replay-body");await select("#profile-select","__active__");await settled();await runLive();
 });
 await check("connection failure clears context/results and visible refresh restores normal operation",async()=>{
  await arm({url:"/api/context",reject:true});await click("#context-refresh");await waitFor("!selectedContext.data?.available&&!selectedContext.loading","failed context");assert.ok(await evaluate("document.querySelector('#context-status').textContent.includes('Instrumented temporary connection failure')"));await cleared();assert.equal(await evaluate("selectedDocument"),null);assert.equal(await evaluate("document.querySelector('#live-btn').disabled"),true);
  await screenshot("refresh-failed",".context-panel");await click("#context-refresh");await settled();await runLive();
 });
 await check("actual unavailable Keeper clears results and restoration remains usable",async()=>{
  await fixture("missing");await click("#context-refresh");await waitFor("selectedContext.data?.available===false","missing Keeper context");await cleared();assert.equal(await evaluate("selectedDocument"),null);await screenshot("keeper-unavailable",".context-panel");
  await fixture("restore");await click("#context-refresh");await settled();await runReplay();
 });
 await check("narrow native preview keeps controls reachable and result provenance readable",async()=>{
  await send("Emulation.setDeviceMetricsOverride",{width:390,height:844,deviceScaleFactor:1,mobile:false});assert.ok(await evaluate("document.documentElement.scrollWidth<=innerWidth"));await screenshot("native-narrow-context",".context-panel");await screenshot("native-narrow-replay","#replay-body");
  await evaluate("document.querySelector('#replay-body input[type=range]').focus()");await key("ArrowRight");assert.equal(await evaluate("document.querySelector('#replay-body input[type=range]').value"),"1");
  await send("Emulation.setDeviceMetricsOverride",{width:1100,height:900,deviceScaleFactor:1,mobile:false});
 });
 await saveHttp("native-workload-model-switches");
 await check("separate legacy Keeper uses its own context identity and previews leave its files exact",async()=>{
  await navigate(`http://127.0.0.1:${ready.legacy_port}/preview`);await setBounds();const live=await runLive(),replay=await runReplay();assert.equal(live.result.body_response,"legacy");assert.notEqual(live.result.context_id,workloadLive.result.context_id);assert.deepEqual(replay.result.replay.live.final_state,live.result.report.final_state);const inspected=await fixture("inspect");assert.deepEqual(inspected.legacy_hashes,ready.legacy_hashes);await saveHttp("independent-legacy-native");
 });
 await check("standalone browser lab retains documented legacy model for actual live and replay",async()=>{
  await navigate(`http://127.0.0.1:${ready.lab_port}/preview`);await select("#profile-select","preview_standalone_profile");await settled();await setBounds();assert.equal(await evaluate("selectedContext.data.kind"),"browser_lab");assert.equal(await evaluate("selectedContext.data.body_response"),"legacy");
  const live=await runLive(),replay=await runReplay();assert.equal(live.result.body_response,"legacy");assert.equal(replay.result.body_response,"legacy");assert.deepEqual(replay.result.replay.live.final_state,live.result.report.final_state);await screenshot("standalone-legacy",".context-panel");await saveHttp("standalone-legacy");
 });
 await check("initial context outage recovers with visible refresh and no stale document",async()=>{
  await send("Page.navigate",{url:base+"/preview?probe_fail_context=1"});await waitFor("typeof selectedContext!=='undefined'&&!selectedContext.data?.available&&document.body.textContent.includes('Instrumented')","initial context error");assert.equal(await evaluate("selectedDocument"),null);await click("#context-refresh");await settled();await saveHttp("initial-context-recovery");
 });
 assert.equal(exceptions.length,0,JSON.stringify(exceptions));
 await fs.writeFile(path.join(output,"http-evidence.json"),JSON.stringify(httpEvidence,null,2));
 await fs.writeFile(path.join(output,"result.json"),JSON.stringify({status:"passed",checks,exceptions,browser:browserPath,scratch,scope:"Real HTTP/engine previews and isolated Chromium DOM, mouse and keyboard. Synthetic response-delivery delays and two context refresh calls exercise races; no successful result bodies substituted. No native game OS-keyboard, scientific cohort or historical regeneration claim.",workload_replay_id:workloadReplay.result.replay.replay_id,legacy_replay_id:legacyReplay.result.replay.replay_id},null,2));
 await send("Browser.close");
}
timer=setTimeout(()=>{console.error("Browser check exceeded bounded 600 seconds");process.exitCode=1;ws?.close();browser?.kill();host?.stdin.end('{"op":"stop"}\n');},600000);
run().catch(async error=>{console.error(error.stack);process.exitCode=1;await fs.mkdir(output,{recursive:true});await screenshotFailure?.().catch(()=>{});await fs.writeFile(path.join(output,"result.json"),JSON.stringify({status:"failed",checks,exceptions,error:error.stack,scratch,diagnostics:diagnostics?await diagnostics().catch(e=>String(e)):null},null,2));}).finally(async()=>{clearTimeout(timer);ws?.close();browser?.kill();host?.stdin.end('{"op":"stop"}\n');await fs.writeFile(path.join(output,"server.stdout.log"),hostOutput);await fs.writeFile(path.join(output,"server.stderr.log"),hostError);await fs.writeFile(path.join(output,"browser.stderr.log"),browserError);});



