/* X2: shared full-document editing, revision arbitration and local recovery.
   Engine validation is the authority; these are explicit authoring transforms. */
(function (root) {
  "use strict";
  const FORMAT = "mecha_workshop_document_v1";
  const clone = value => value === undefined ? undefined : JSON.parse(JSON.stringify(value));
  const equal = (a, b) => JSON.stringify(a) === JSON.stringify(b);
  const object = value => value !== null && typeof value === "object" && !Array.isArray(value);
  const TOKENS = {
    B: ["body", "hard", "core", 1], A: ["body", "hard", "core", 1],
    S: ["shell", "hard", "carapace", 1], J: ["joint", "joint", "joints", 1],
    L: ["limb", "hard", "limbs", 1], E: ["eye", "glass", "sensors", 2],
    M: ["mouth", "soft", "expression", 2], N: ["antenna", "signal", "antennae", 2],
    P: ["sensor", "signal", "antennae", 2], D: ["decoration", "light", "trim", 2],
    F: ["effect", "signal", "aura", 2],
  };
  const ORGAN_ROLES = {core:"body_core", carapace:"body_core", joints:"locomotion", limbs:"locomotion", sensors:"sensor", antennae:"sensor", expression:"expression", trim:"ornament", aura:"effect"};
  const roleToken = role => role === "anchor" ? "A" : Object.keys(TOKENS).find(t => t !== "A" && TOKENS[t][0] === role) || ".";
  const token = cell => cell.animation_anchor ? "A" : roleToken(cell.role);
  function project(grid) {
    const [width, height] = grid.grid_size;
    const matrix = Array.from({length:height}, () => Array(width).fill("."));
    for (const cell of grid.cells || []) if (matrix[cell.y] && cell.x >= 0 && cell.x < width) matrix[cell.y][cell.x] = token(cell);
    return matrix;
  }
  function repairMembership(grid, oldCells) {
    const affected = new Set();
    const before = new Map(oldCells.map(c => [`${c.x},${c.y}`, c]));
    const after = new Map(grid.cells.map(c => [`${c.x},${c.y}`, c]));
    for (const key of new Set([...before.keys(), ...after.keys()])) {
      if (before.get(key)?.organ !== after.get(key)?.organ) {
        if (before.get(key)?.organ) affected.add(before.get(key).organ);
        if (after.get(key)?.organ) affected.add(after.get(key).organ);
      }
    }
    for (const id of affected) {
      const cells = grid.cells.filter(c => c.organ === id);
      const entry = grid.organs[id] || {role:ORGAN_ROLES[id], required:id === "core" || id === "sensors", cells:[]};
      const points = new Set(cells.map(c => `${c.x},${c.y}`));
      entry.cells = (entry.cells || []).filter(([x,y]) => points.has(`${x},${y}`));
      const retained = new Set(entry.cells.map(([x,y]) => `${x},${y}`));
      for (const cell of cells) if (!retained.has(`${cell.x},${cell.y}`)) entry.cells.push([cell.x,cell.y]);
      grid.organs[id] = entry;
    }
  }
  function editMatrix(document, matrix) {
    const next = clone(document), grid = next.grid, oldCells = clone(grid.cells);
    const width = matrix[0].length, height = matrix.length;
    const cells = new Map(grid.cells.map(c => [`${c.x},${c.y}`, c]));
    const oldProjection = project(grid);
    for (const cell of grid.cells) if (cell.x >= width || cell.y >= height) {
      if (cell.locked) throw new Error(`Cell ${cell.x},${cell.y} is locked; resize would remove it.`);
      cells.delete(`${cell.x},${cell.y}`);
    }
    for (let y=0; y<height; y++) for (let x=0; x<width; x++) {
      const chosen = matrix[y][x], prior = oldProjection[y]?.[x] || ".";
      if (chosen === prior) continue;
      const key = `${x},${y}`, old = cells.get(key);
      if (old?.locked) throw new Error(`Cell ${x},${y} is locked; its traits and pixels are preserved.`);
      if (chosen === ".") { cells.delete(key); continue; }
      if (!TOKENS[chosen]) throw new Error(`Unsupported paint token ${chosen}; the document was preserved.`);
      if (old && (chosen === "A" || (old.animation_anchor && chosen === roleToken(old.role)))) {
        old.animation_anchor = chosen === "A";
        continue;
      }
      const [role, material, organ, index] = TOKENS[chosen];
      cells.set(key, {...(old || {x,y,mutation_weight:0.1,stress:0,damage:0,locked:false}), role,material,organ,
        visual:grid.palette.colors[Math.min(index,grid.palette.colors.length-1)], animation_anchor:chosen === "A"});
    }
    grid.cells = [...cells.values()]; grid.grid_size = [width,height];
    repairMembership(grid,oldCells);
    return next;
  }
  function patchCell(document,x,y,patch) {
    const next=clone(document), grid=next.grid, oldCells=clone(grid.cells);
    const cell=grid.cells.find(c=>c.x===x&&c.y===y);
    if (!cell) throw new Error(`No cell at ${x},${y}. Draw a cell first.`);
    if (cell.locked) throw new Error(`Cell ${x},${y} is locked; its traits are preserved.`);
    Object.assign(cell,patch);
    if (patch.role !== undefined) {
      const definition=TOKENS[roleToken(patch.role)];
      if (!definition) throw new Error("This role cannot be painted. The complete document is preserved.");
      cell.organ=definition[2];
      if (patch.role === "anchor") cell.animation_anchor=true;
    }
    repairMembership(grid,oldCells);return next;
  }
  function recolor(document,paletteId,colors) {
    const next=clone(document), old=next.grid.palette.colors;
    for (const cell of next.grid.cells) {
      const index=old.indexOf(cell.visual);
      if (index>=0 && !cell.locked) cell.visual=colors[Math.min(index,colors.length-1)];
    }
    next.grid.palette={...next.grid.palette,palette_id:paletteId,colors:clone(colors)};
    return next;
  }
  // Apply only differences in the form projection, preserving all unseen siblings.
  function overlay(original,before,after) {
    if (equal(before,after)) return clone(original);
    if (!object(before) && !object(after)) return clone(after);
    const result=object(original)?clone(original):{};
    for (const key of new Set([...Object.keys(before||{}),...Object.keys(after||{})])) {
      if (equal(before?.[key],after?.[key])) continue;
      const value=overlay(result[key],before?.[key],after?.[key]);
      if (value===undefined || (object(value)&&!Object.keys(value).length&&after?.[key]===undefined)) delete result[key];
      else result[key]=value;
    }
    return Object.keys(result).length?result:(after===undefined?undefined:result);
  }
  class History {
    constructor(key,initial,storage) {
      this.key=key;this.history=[clone(initial)];this.index=0;this.revision=0;this.saved=null;
      this.storageError="";this.group=null;this.recovery=null;this.seen=null;
      try {
        this.storage=storage===undefined?root.localStorage:storage;
        this.seen=this.storage.getItem(key);
        if (this.seen) {
          const found=JSON.parse(this.seen);
          if (found.version!==1 || !Array.isArray(found.history) || !found.history.length || !Number.isInteger(found.index) || !found.history[found.index]) throw new Error("unreadable recovery record");
          this.recovery=found;
        }
      } catch { this.storageError="Browser recovery is unavailable. Download a draft copy before leaving."; }
    }
    offerLegacy(key){
      if(this.recovery)return;
      try{const raw=this.storage?.getItem(key);if(!raw)return;const prior=JSON.parse(raw);if(prior.version!==1||!Array.isArray(prior.history)||!prior.history[prior.index])throw new Error("unreadable legacy draft");this.recovery=prior;this.recoverySource="legacy browser lab";}
      catch(error){this.storageError="The earlier browser draft could not be read; its original bytes remain stored. "+error.message;}
    }
    get hasRecovery(){return !!this.recovery;}
    get current(){return clone(this.history[this.index]);}
    get canUndo(){return this.index>0;}
    get canRedo(){return this.index<this.history.length-1;}
    record(state,group=null) {
      if (equal(this.history[this.index],state)) return false;
      if (group && group===this.group && this.index>0) this.history[this.index]=clone(state);
      else {this.history=this.history.slice(0,this.index+1);this.history.push(clone(state));this.index++;}
      this.group=group;this.revision++;this.persist();return true;
    }
    replace(state){this.history[this.index]=clone(state);this.persist("replace");}
    endGroup(){this.group=null;}
    undo(){if(this.canUndo){this.index--;this.revision++;this.group=null;this.persist();}return this.current;}
    redo(){if(this.canRedo){this.index++;this.revision++;this.group=null;this.persist();}return this.current;}
    restore(){
      if(this.recovery){this.history=clone(this.recovery.history);this.index=this.recovery.index;this.saved=this.recovery.saved;this.recovery=null;this.revision++;this.persist();}
      return this.current;
    }
    startFresh(state){if(this.hasRecovery)this.restore();this.record(state);return this.current;}
    markSaved(state){this.saved=clone(state);this.persist();}
    persist(reason="change"){
      if(this.hasRecovery)return;
      try {
        if(!this.storage)throw new Error("unavailable");
        if(this.storage.getItem(this.key)!==this.seen)throw new Error("another tab changed the recovery copy");
        while(this.history.length>40 && this.index>1){this.history.shift();this.index--;}
        let data={version:1,history:this.history,index:this.index,saved:this.saved};
        while(JSON.stringify(data).length>1800000 && this.history.length>2 && this.index>1){this.history.shift();this.index--;data.index=this.index;}
        const encoded=JSON.stringify(data);this.storage.setItem(this.key,encoded);this.seen=encoded;this.storageError="";
      }catch(error){this.storageError="Browser recovery could not update ("+error.message+"). Download a draft copy before leaving.";}
      this.onPersist?.(reason);
    }
  }
  class RequestGate {
    constructor(){this.requests=new Map();this.sequence=0;}
    begin(key,revision){this.requests.get(key)?.controller.abort();const request={key,revision,sequence:++this.sequence,controller:new AbortController()};this.requests.set(key,request);return request;}
    accept(request,revision,echo){return this.requests.get(request.key)===request && request.revision===revision && String(echo)===String(revision);}
    cancel(key){this.requests.get(key)?.controller.abort();this.requests.delete(key);}
  }
  class ApiError extends Error {constructor(message,status,data){super(message);this.status=status;this.data=data;}}
  async function request(url,payload,options={}) {
    const controller=new AbortController(), relay=()=>controller.abort();
    if(options.signal?.aborted)controller.abort();else options.signal?.addEventListener("abort",relay,{once:true});
    const timer=setTimeout(()=>controller.abort(new Error("Request timed out")),options.timeoutMs||20000);
    try {
      const response=await fetch(url,{method:payload===undefined?"GET":"POST",headers:payload===undefined?{}:{"Content-Type":options.contentType||"application/json"},
        body:payload===undefined?undefined:options.raw?payload:JSON.stringify(payload),signal:controller.signal});
      if(!response.ok){const data=await response.json();throw new ApiError([data.error,...(data.errors||[])].filter(Boolean).join("; ")||"Request refused",response.status,data);}
      return options.binary?response:await response.json();
    }finally{clearTimeout(timer);options.signal?.removeEventListener("abort",relay);}
  }
  function notice(element,message,tone=""){element.textContent=message;element.className="notice"+(tone?" "+tone:"");element.setAttribute("role","status");}
  function download(blob,filename){const link=document.createElement("a");const url=URL.createObjectURL(blob);link.href=url;link.download=filename;link.click();setTimeout(()=>URL.revokeObjectURL(url),1000);}
  function choice(title,message,action="Replace with this draft") {
    return new Promise(resolve=>{
      const trigger=document.activeElement,dialog=document.createElement("dialog");dialog.className="authoring-dialog";
      const heading=document.createElement("h2");heading.id="authoring-dialog-title";heading.textContent=title;
      const body=document.createElement("p");body.id="authoring-dialog-description";body.textContent=message;
      const cancel=document.createElement("button");cancel.type="button";cancel.className="action";cancel.textContent="Keep editing";
      const proceed=document.createElement("button");proceed.type="button";proceed.className="action";proceed.textContent=action;
      const actions=document.createElement("div");actions.className="filebar";actions.append(cancel,proceed);dialog.append(heading,body,actions);
      dialog.setAttribute("aria-labelledby",heading.id);dialog.setAttribute("aria-describedby",body.id);document.body.append(dialog);
      cancel.addEventListener("click",()=>dialog.close("cancel"));proceed.addEventListener("click",()=>dialog.close("proceed"));
      dialog.addEventListener("close",()=>{const accepted=dialog.returnValue==="proceed";dialog.remove();trigger?.focus();resolve(accepted);},{once:true});
      dialog.showModal();cancel.focus();
    });
  }
  async function writeWithConflict(url,payload,revisionKey) {
    try{return await request(url,payload);}catch(error){
      if(error.status!==409 || !Object.prototype.hasOwnProperty.call(error.data,"current_revision"))throw error;
      const accepted=await choice("A different revision is on disk", "This target changed or already exists. Keep editing to load and compare it, or replace it with the selected draft. Its current files will be backed up.");
      if(!accepted)return null;
      return request(url,{...payload,[revisionKey]:error.data.current_revision});
    }
  }
  const STRATA=["body","organs","decoration","effects"];
  function supportedLayers(layers){return layers==null || (Array.isArray(layers)&&layers.length===4&&layers.every((l,index)=>l.name===STRATA[index]));}
  function patchLayers(original,matrices,visibility){
    const source=Array.isArray(original)?original:STRATA.map(name=>({name}));
    return source.map(layer=>{const result=clone(layer);if(Object.hasOwn(matrices,layer.name))result.matrix=clone(matrices[layer.name]);if(Object.hasOwn(visibility,layer.name)&&visibility[layer.name]!== (layer.visible!==false))result.visible=visibility[layer.name];return result;});
  }
  function historyRecord(history){return {version:1,history:clone(history.history),index:history.index,saved:clone(history.saved)};}
  function draftEnvelope(history){const current=history.current,{document,...editor_state}=current;return {format:"mecha_workshop_draft_v1",draft_revision:history.revision,document,editor_state,history:historyRecord(history)};}
  class ServerDraft {
    constructor(history,context,kind,transport=request){
      Object.assign(this,{history,context,kind,transport,loaded:false,loading:false,diskRevision:null,error:"",timer:null,inFlight:null,dirty:false,archiveNext:false,browserRecovery:null,conflict:null,previousAvailable:false,status:"Checking server recovery…"});
      history.remote=this;history.onPersist=reason=>{if(reason!=="replace"){this.dirty=true;this.queue();}this.changed?.();};
    }
    async load(){
      this.loading=true;this.error="";this.changed?.();
      try{
        const result=await this.transport("/api/drafts/"+this.kind);
        this.diskRevision=result.draft_disk_revision;this.loaded=true;this.conflict=null;
        const browser=this.history.recovery||((this.dirty||this.history.revision>0)?historyRecord(this.history):null);
        if(result.exists){
          if(browser&&!equal(browser,result.snapshot.history)){this.browserRecovery=clone(browser);this.preserveBrowser(browser);}
          this.history.recovery=clone(result.snapshot.history);this.history.recoverySource="server";
        }
        this.status=result.exists?"A server draft is available for this selected context.":"Server recovery is ready. Work is saved after your next edit.";
      }catch(error){this.error=error.message;this.conflict=error.data;this.previousAvailable=!!error.data?.recovery_available;if(Object.hasOwn(error.data||{},"current_revision"))this.diskRevision=error.data.current_revision;}
      finally{this.loading=false;this.changed?.();}
    }
    preserveBrowser(record){try{this.history.storage?.setItem(this.history.key+":previous",JSON.stringify(record));}catch{this.error="The alternative browser copy could not be archived. Download it before choosing another draft.";}}
    async previous(){
      try{const result=await this.transport("/api/drafts/"+this.kind+"?slot=previous");if(!result.exists)throw new Error("No previous valid server draft is available.");this.diskRevision=result.draft_disk_revision;this.history.recovery=clone(result.snapshot.history);this.history.recoverySource="previous server";this.loaded=true;this.error="";this.archiveNext=true;this.status="Previous server draft selected. Restore explicitly to replace the primary; its bytes will be archived.";}
      catch(error){this.error=error.message;}this.changed?.();
    }
    queue(){clearTimeout(this.timer);if(!this.loaded||this.loading||this.error||this.history.hasRecovery)return;this.timer=setTimeout(()=>this.flush(),350);}
    async flush(){
      clearTimeout(this.timer);if(this.inFlight)return this.inFlight;
      if(!this.dirty||!this.loaded||this.loading||this.error||this.history.hasRecovery||!this.history.current.document)return;
      const snapshot=draftEnvelope(this.history),archive=this.archiveNext;this.dirty=false;this.status="Saving recoverable draft…";this.changed?.();
      this.inFlight=(async()=>{try{
        const result=await this.transport("/api/drafts/"+this.kind,{...this.context.pins(),expected_draft_revision:this.diskRevision,snapshot,...(archive?{archive_previous:true}:{})});
        this.diskRevision=result.draft_disk_revision;this.archiveNext=false;this.status="Server recovery saved draft revision "+snapshot.draft_revision+". Project outputs are separate.";
      }catch(error){this.dirty=true;this.error=error.message;this.conflict=error.data;this.status="Server draft could not update. Browser work is retained; download a copy or retry.";}
      finally{this.inFlight=null;this.changed?.();if(this.dirty&&!this.error)this.queue();}})();return this.inFlight;
    }
    async replaceConflict(){
      if(this.conflict?.error_code!=="draft_conflict")return;
      if(!await choice("Replace the other server draft?","Your current draft will replace the other writer's version. Its exact prior bytes will be archived. Download or load the other copy first if you need to compare it.","Replace server draft"))return;
      this.diskRevision=this.conflict.current_revision;this.archiveNext=true;this.error="";this.conflict=null;this.dirty=true;return this.flush();
    }
    dispose(){clearTimeout(this.timer);this.history.onPersist=null;}
  }
  function element(tag,text,className){const node=document.createElement(tag);if(text!==undefined)node.textContent=String(text);if(className)node.className=className;return node;}
  class Context {
    constructor(){this.data=null;this.panel=null;this.onChange=null;}
    pins(){if(!this.data?.available)throw new Error(this.data?.reason||"Selected context is unavailable. Refresh the context before writing.");return {context_id:this.data.context_id,expected_context_revision:this.data.context_revision};}
    async refresh(){this.data=await request("/api/context");this.render();this.onChange?.(this.data);return this.data;}
    async inventory(){const result=await request("/api/context/creatures");return result.creatures||[];}
    async resolve(ref){return request("/api/context/document",{...this.pins(),ref});}
    mount(){
      this.panel=element("section",undefined,"panel context-panel");this.panel.setAttribute("aria-label","Selected Workshop context");
      document.querySelector("header.top").after(this.panel);this.render();return this;
    }
    render(){
      if(!this.panel)return;const retained=Array.from(this.panel.querySelectorAll(":scope > .context-sources, :scope > #context-covenant"));this.panel.replaceChildren();const data=this.data;
      this.panel.append(element("h2",data?.kind==="native_keeper"?"Selected native Keeper":data?.kind==="browser_lab"?"Browser lab project":"Workshop context"));
      const status=element("p",data?(data.available?`${data.keeper_id||data.context_id} · campaign ${data.campaign_id||"not available"}`:data.reason||"Selected context unavailable") : "Reading the selected context…","notice");status.id="context-status";status.setAttribute("role","status");this.panel.append(status);
      if(data?.available&&data.reason)this.panel.append(element("p",data.reason,"notice"));
      if(data?.keeper_dir)this.panel.append(element("p",data.keeper_dir,"notice context-path"));
      const refresh=element("button","Refresh selected context","action");refresh.id="context-refresh";refresh.type="button";refresh.addEventListener("click",async()=>{refresh.disabled=true;try{await this.refresh();}catch(error){notice(status,error.message,"err");}finally{refresh.disabled=false;}});this.panel.append(refresh);
      if(data){const detail=element("details");detail.append(element("summary","Active covenant and earned budget"));detail.append(element("pre",JSON.stringify({covenant:data.covenant??null,budget:data.budget??null},null,2),"context-facts"));this.panel.append(detail);
        for(const link of document.querySelectorAll('a[href="/companion"],a[href="/session"]'))if(data.kind!=="browser_lab"){link.removeAttribute("href");link.setAttribute("aria-disabled","true");link.textContent+=" (browser lab only)";}
      }
      this.panel.append(...retained);
    }
  }
  async function mountSourcePicker(context,host,onSelect,captureRevision){
    const label=element("label","Selected context creature");label.htmlFor="context-creature";
    const select=element("select");select.id="context-creature";select.add(new Option("Choose saved companion, release or elite…",""));
    const entries=await context.inventory();entries.forEach((entry,index)=>select.add(new Option(entry.label||entry.grid_id||entry.name,String(index))));
    const button=element("button","Open selected creature","action");button.type="button";button.disabled=true;select.addEventListener("change",()=>button.disabled=select.value==="");
    const status=element("p","Opening a source is undoable. Release stages it for later engine admission.","notice");
    button.addEventListener("click",async()=>{button.disabled=true;try{const selected=entries[Number(select.value)],revision=captureRevision?.();const result=await context.resolve(selected.ref);if(captureRevision&&revision!==captureRevision())throw new Error("The draft changed during loading. Open the source again to replace it.");await onSelect(result,selected);notice(status,"Opened "+(selected.label||selected.grid_id)+". The source remains unchanged.","ok");}catch(error){notice(status,error.message+". Current work is retained.","err");}finally{button.disabled=select.value==="";}});
    const wrap=element("div",undefined,"context-sources");wrap.append(label,select,button,status);host.append(wrap);return {select,entries};
  }
  function mountHistory(history,{capture,apply,retry,kind}) {
    const panel=element("section",undefined,"panel authoring-history");panel.setAttribute("aria-label","Draft history and recovery");
    const bar=element("div",undefined,"filebar"),buttons={};
    for(const [id,label] of [["undo","Undo"],["redo","Redo"],["restore","Restore saved draft"],["fresh","Start new draft"],["browser","Restore alternative browser draft"],["previous","Review previous server draft"],["replace","Resolve server draft conflict"],["download","Download draft JSON"],["open","Open draft JSON"],["retry","Retry connection"]]){const button=element("button",label,"action");button.type="button";button.id="draft-"+id;buttons[id]=button;bar.append(button);}
    const status=element("p",undefined,"notice");status.id="draft-status";status.setAttribute("role","status");
    const hint=element("p","Draft history and recovery are separate from Save to project. Draft JSON can include work the engine has not accepted.","notice");panel.append(bar,status,hint);(document.querySelector(".context-panel")||document.querySelector("header.top")).after(panel);
    const stage=document.querySelector(".stage");
    function refresh(){
      const remote=history.remote,blocked=!!remote&&(remote.loading||!remote.loaded),pending=history.hasRecovery;
      buttons.undo.disabled=!history.canUndo||pending||blocked;buttons.redo.disabled=!history.canRedo||pending||blocked;
      buttons.restore.hidden=buttons.fresh.hidden=!pending;buttons.browser.hidden=!remote?.browserRecovery;buttons.previous.hidden=!remote?.previousAvailable;buttons.replace.hidden=remote?.conflict?.error_code!=="draft_conflict";
      buttons.open.disabled=pending||blocked;buttons.download.disabled=!capture()?.document&&!history.recovery;stage.inert=pending||blocked;
      notice(status,pending?`A ${history.recoverySource||"browser"} draft is available. Restore it, or start new and keep it in Undo.`:remote?.error||history.storageError||remote?.status||`Draft revision ${history.revision} · browser recovery updated · Ctrl+Z / Ctrl+Shift+Z`,remote?.error||history.storageError?"err":"");
    }
    buttons.undo.addEventListener("click",()=>{apply(history.undo());refresh();});buttons.redo.addEventListener("click",()=>{apply(history.redo());refresh();});
    buttons.restore.addEventListener("click",()=>{apply(history.restore());refresh();});buttons.fresh.addEventListener("click",()=>{history.startFresh(capture());apply(history.current);refresh();});
    buttons.browser.addEventListener("click",()=>{const remote=history.remote;history.recovery=clone(remote.browserRecovery);remote.browserRecovery=null;remote.archiveNext=true;apply(history.restore());refresh();});
    buttons.previous.addEventListener("click",()=>history.remote.previous());buttons.replace.addEventListener("click",()=>history.remote.replaceConflict());
    buttons.download.addEventListener("click",()=>{const selected=history.hasRecovery?history.recovery.history[history.recovery.index]:capture();download(new Blob([JSON.stringify({format:"mecha_workshop_recovery_v1",kind,snapshot:selected},null,2)],{type:"application/json"}),kind+".workshop.json");});
    const file=element("input");file.type="file";file.accept=".json";file.hidden=true;panel.append(file);buttons.open.addEventListener("click",()=>file.click());
    file.addEventListener("change",async()=>{const revision=history.revision;try{const incoming=JSON.parse(await file.files[0].text());if(revision!==history.revision)throw new Error("The draft changed while opening the file. Open it again to replace the current draft.");if(incoming.format!=="mecha_workshop_recovery_v1"||incoming.kind!==kind||!incoming.snapshot?.document||incoming.snapshot.document.format!==FORMAT)throw new Error("Choose a draft JSON from this editor.");apply(incoming.snapshot);history.record(capture());refresh();}catch(error){notice(status,error.message,"err");}finally{file.value="";}});
    buttons.retry.addEventListener("click",retry);
    document.addEventListener("keydown",event=>{if(event.isComposing||event.target.isContentEditable||/INPUT|TEXTAREA|SELECT/.test(event.target.tagName))return;if((event.ctrlKey||event.metaKey)&&event.key.toLowerCase()==="z"&&!history.hasRecovery&&!stage.inert){event.preventDefault();apply(event.shiftKey?history.redo():history.undo());refresh();}});
    const unsafe=()=>history.storageError||history.remote?.dirty||history.remote?.inFlight;
    root.addEventListener("beforeunload",event=>{if(unsafe()){event.preventDefault();event.returnValue="";}});
    for(const link of document.querySelectorAll("nav a"))link.addEventListener("click",async event=>{if(unsafe()){event.preventDefault();if(await choice("Draft recovery has not finished","Download a draft copy before leaving to avoid losing this work.","Leave this editor"))root.location.href=link.href;}});
    refresh();return {refresh,status};
  }
  const api={patchLayers,supportedLayers,draftEnvelope,ServerDraft,Context,mountSourcePicker,element,FORMAT,clone,equal,project,token,roleToken,editMatrix,patchCell,recolor,overlay,History,RequestGate,request,notice,download,choice,writeWithConflict,mountHistory};
  if(typeof module!=="undefined"&&module.exports)module.exports=api;
  else root.WorkshopAuthoring=api;
})(typeof window!=="undefined"?window:globalThis);
