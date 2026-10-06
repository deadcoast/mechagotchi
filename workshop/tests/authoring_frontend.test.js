"use strict";
const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const A = require("../shared/authoring.js");
const seed = JSON.parse(fs.readFileSync(path.join(__dirname, "../../data/seed_grids/mg_seed_001.json"), "utf8"));
const doc = () => ({format: A.FORMAT, grid: A.clone(seed), profile: {slip_version: "0.2.0", mechanics: {cleanliness:true}}});
const memory = () => {const data = new Map(); return {getItem:k=>data.get(k)??null, setItem:(k,v)=>data.set(k,v)};};

test("unchanged rich grid projection preserves complete document", () => {
  const before = doc();
  Object.assign(before.grid.cells.find(c=>!c.animation_anchor), {role:"antenna", material:"signal", mutation_weight:0.91, damage:0.2});
  before.grid.metadata.extra = "preserve provenance";
  const after = A.editMatrix(before, A.project(before.grid));
  assert.deepEqual(after, before);
});
test("explicit cell edit retains unedited rich fields and organ metadata", () => {
  const before = doc(); const cell = before.grid.cells.find(c=>!c.animation_anchor);
  cell.mutation_weight = 0.91; before.grid.organs[cell.organ].required = true;
  const after = A.patchCell(before, cell.x, cell.y, {material:"soft"});
  assert.equal(after.grid.cells.find(c=>c.x===cell.x&&c.y===cell.y).mutation_weight,0.91);
  assert.equal(after.grid.cells.find(c=>c.x===cell.x&&c.y===cell.y).material,"soft");
  assert.deepEqual(after.grid.organs,before.grid.organs);
  assert.deepEqual(before.grid.cells.find(c=>c.x===cell.x&&c.y===cell.y),cell);
});
test("only changed known profile fields replace their original values", () => {
  const profile = {slip_version:"0.2.0", name:"old", mechanics:{cleanliness:true}, learning_switches:{recent_interaction_ewma:true}, deliberation:{max_ticks:4, confidence_threshold:0.723}};
  const projection = {slip_version:"0.1.0", name:"old", deliberation:{max_ticks:4, confidence_threshold:0.72}};
  assert.deepEqual(A.overlay(profile,projection,projection),profile);
  const result = A.overlay(profile,projection,{...projection,name:"new"});
  assert.deepEqual(result,{...profile,name:"new"});
});
test("optional known-field deletion preserves unseen siblings",()=>{
  assert.deepEqual(A.overlay({block:{known:1,unseen:2}},{block:{known:1}},{}),{block:{unseen:2}});
});
test("history reverses replacement, redo and storage restart",()=>{
  const storage=memory(); const h=new A.History("draft",{value:1},storage);
  h.record({value:2}); h.record({value:3});
  assert.deepEqual(h.undo(),{value:2}); assert.deepEqual(h.redo(),{value:3});
  const resumed=new A.History("draft",{value:0},storage);
  assert.equal(resumed.hasRecovery,true);
  assert.deepEqual(resumed.restore(),{value:3});
  assert.deepEqual(resumed.undo(),{value:2});
});
test("new draft keeps interrupted work recoverable through undo",()=>{
  const storage=memory();const h=new A.History("draft",{value:1},storage);h.record({value:2});
  const restarted=new A.History("draft",{value:0},storage);restarted.startFresh({value:0});
  assert.deepEqual(restarted.undo(),{value:2});
});
test("old revision and superseded request cannot certify current work",()=>{
  const g=new A.RequestGate();const first=g.begin("validate",1);const second=g.begin("validate",1);
  assert.equal(g.accept(first,1,1),false);assert.equal(g.accept(second,2,1),false);
  assert.equal(g.accept(second,1,1),true);assert.equal(g.accept(second,1,undefined),false);
});
test("storage failure preserves live history and makes durability failure explicit",()=>{
  const h=new A.History("draft",{value:1},{getItem(){return null},setItem(){throw new Error("quota")}});
  h.record({value:2});assert.ok(h.storageError);assert.deepEqual(h.undo(),{value:1});
});
test("later tab cannot silently replace another tab recovery copy",()=>{
  const storage=memory();const one=new A.History("draft",{value:1},storage);one.record({value:2});
  const two=new A.History("draft",{value:0},storage);two.restore();two.record({value:3});one.record({value:4});
  assert.ok(one.storageError);const reader=new A.History("draft",{value:0},storage);
  assert.deepEqual(reader.restore(),{value:3});
});
test("crop is explicit, reversible and cannot alter source document",()=>{
  const before=doc();const larger=A.editMatrix(before,Array.from({length:16},(_,y)=>Array.from({length:16},(_,x)=>A.project(before.grid)[y]?.[x]||".")));
  const h=new A.History("crop",{document:larger},memory());
  h.record({document:A.editMatrix(larger,Array.from({length:8},()=>Array(8).fill(".")))});
  assert.deepEqual(h.undo().document,larger);assert.deepEqual(before.grid,seed);
});


test("layer visibility and paint retain accepted siblings and source order",()=>{
  const layers=[{name:"effects",matrix:[["."]],visible:true,blend:{mode:"screen"}},{name:"body",matrix:[["B"]],visible:true,creator:"original"}];
  const result=A.patchLayers(layers,{body:[["A"]],effects:[["."]]},{body:false,effects:true});
  assert.deepEqual(result,[{...layers[0]},{...layers[1],matrix:[["A"]],visible:false}]);
  assert.equal(layers[1].matrix[0][0],"B");
});
test("unrecognized layer semantics stay intact and are not spatially editable",()=>{
  const layers=[{name:"future",matrix:[["B"]],operation:"custom"}];
  assert.deepEqual(A.patchLayers(layers,{},{}),layers);
  assert.equal(A.supportedLayers(layers),false);
});
test("server draft envelope preserves active undo position and unsaved full history",()=>{
  const h=new A.History("draft",{document:doc(),name:"first"},memory());
  h.record({document:doc(),name:"second"});h.undo();
  const envelope=A.draftEnvelope(h);
  assert.deepEqual(envelope.document,h.current.document);
  assert.deepEqual(envelope.editor_state,{name:"first"});
  assert.equal(envelope.history.index,0);assert.equal(envelope.history.history[1].name,"second");
});
test("server recovery gates initial blank and survives a new browser origin",async()=>{
  const prior=new A.History("old",{document:doc(),name:"saved draft"},memory());
  prior.record({...prior.current,name:"unsaved precise draft"});
  const calls=[],ctx={pins:()=>({context_id:"keeper1",expected_context_revision:"c1"})};
  const fresh=new A.History("new-origin",{document:null,name:""},memory());
  const sync=new A.ServerDraft(fresh,ctx,"grid",async(url,payload)=>{calls.push(payload);return {exists:true,draft_disk_revision:"disk1",snapshot:A.draftEnvelope(prior)};});
  await sync.load();
  assert.equal(fresh.hasRecovery,true);assert.equal(calls.length,1);assert.equal(calls[0],undefined);
  assert.equal(fresh.restore().name,"unsaved precise draft");sync.dispose();
});
test("stale draft write leaves later work queued and disk conflicts never auto-overwrite",async()=>{
  const h=new A.History("k",{document:doc(),name:"a"},memory());
  let rejectWrite;const ctx={pins:()=>({context_id:"k",expected_context_revision:"c"})};
  const sync=new A.ServerDraft(h,ctx,"grid",async(url,payload)=>{if(!payload)return {exists:false,draft_disk_revision:null};return new Promise((resolve,reject)=>{rejectWrite=reject;});});
  await sync.load();h.record({...h.current,name:"b"});const saving=sync.flush();
  h.record({...h.current,name:"c"});rejectWrite(Object.assign(new Error("conflict"),{status:409,data:{error_code:"draft_conflict",current_revision:"other"}}));
  await saving;assert.equal(h.current.name,"c");assert.ok(sync.error);assert.equal(sync.diskRevision,null);sync.dispose();
});


test("unrelated layer edits preserve omitted/default visibility exactly",()=>{
  const original=[{name:"body",matrix:[["B"]],metadata:{note:"keep"}},{name:"effects",matrix:[["."]],visible:null}];
  assert.deepEqual(A.patchLayers(original,{body:[["A"]],effects:[["."]]},{body:true,effects:true}),[{...original[0],matrix:[["A"]]},original[1]]);
});
test("corrupt primary draft cannot cause blank autosave and previous recovery is explicit",async()=>{
  const prior=new A.History("old",{document:doc(),name:"previous"},memory()),h=new A.History("new",{document:doc(),name:"blank"},memory()),writes=[];
  const ctx={pins:()=>({context_id:"native",expected_context_revision:"c"})};
  const sync=new A.ServerDraft(h,ctx,"grid",async(url,payload)=>{
    if(payload){writes.push(payload);return {draft_disk_revision:"restored"};}
    if(url.includes("slot=previous"))return {exists:true,draft_disk_revision:"corrupt",snapshot:A.draftEnvelope(prior)};
    throw Object.assign(new Error("unreadable"),{status:409,data:{error_code:"draft_unreadable",current_revision:"corrupt",recovery_available:true}});
  });
  await sync.load();h.replace({...h.current,name:"bootstrap"});await sync.flush();assert.equal(writes.length,0);assert.equal(sync.previousAvailable,true);
  await sync.previous();assert.equal(h.hasRecovery,true);assert.equal(writes.length,0);h.restore();await sync.flush();assert.equal(writes.length,1);assert.equal(writes[0].archive_previous,true);assert.equal(writes[0].expected_draft_revision,"corrupt");assert.equal(writes[0].snapshot.editor_state.name,"previous");sync.dispose();
});


test("old browser-lab recovery is explicitly offered without overwriting its source",()=>{
  const storage=memory(),old=new A.History("legacy",{document:doc(),name:"old"},storage);old.record({...old.current,name:"interrupted"});const original=storage.getItem("legacy");
  const scoped=new A.History("context",{document:doc(),name:"blank"},storage);scoped.offerLegacy("legacy");assert.equal(scoped.hasRecovery,true);assert.equal(storage.getItem("context"),null);assert.equal(scoped.restore().name,"interrupted");assert.equal(storage.getItem("legacy"),original);
});
