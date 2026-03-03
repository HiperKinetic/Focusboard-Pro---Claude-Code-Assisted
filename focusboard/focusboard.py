#!/usr/bin/env python3
"""
Focusboard PRO - macOS Desktop App
Powered by pywebview + Python backend

Requirements:
    pip install pywebview

Run:
    python3 focusboard.py

Data is saved to: ~/Library/Application Support/FocusboardPRO/data.json
"""

import webview
import json
import os
import sys
import threading
from pathlib import Path

# ── Data directory ─────────────────────────────────────────
DATA_DIR = Path.home() / "Library" / "Application Support" / "FocusboardPRO"
DATA_FILE = DATA_DIR / "data.json"

DEFAULT_DATA = {
    "projects": [{"id": 1, "name": "Launch Website", "color": "#4D96FF"}],
    "members": [
        {"id": 1, "firstName": "Alex", "lastName": "Rivera", "email": "alex.rivera@co.com"},
        {"id": 2, "firstName": "Jamie", "lastName": "Chen", "email": "jamie.chen@co.com"},
        {"id": 3, "firstName": "Sam", "lastName": "Patel", "email": "sam.patel@co.com"},
    ],
    "tasks": [
        {"id":1,"text":"Define project scope","projectId":1,"status":"complete","priority":"high","plannedStart":"2026-03-01","plannedEnd":"2026-03-03","actualStart":"2026-03-01","actualEnd":"2026-03-04","deps":[],"subtasks":[],"ownerId":1,"notes":"","blockedReason":"","blockedSince":""},
        {"id":2,"text":"Design wireframes","projectId":1,"status":"in_progress","priority":"high","plannedStart":"2026-03-04","plannedEnd":"2026-03-08","actualStart":"2026-03-05","actualEnd":"","deps":[1],"subtasks":[{"id":21,"text":"Homepage layout","done":True,"status":"complete","plannedEnd":"2026-03-06","actualEnd":"2026-03-06"},{"id":22,"text":"Mobile breakpoints","done":False,"status":"in_progress","plannedEnd":"2026-03-08","actualEnd":""}],"ownerId":2,"notes":"","blockedReason":"","blockedSince":""},
        {"id":3,"text":"Write copy","projectId":1,"status":"blocked","priority":"medium","plannedStart":"2026-03-04","plannedEnd":"2026-03-07","actualStart":"2026-03-04","actualEnd":"","deps":[1],"subtasks":[],"ownerId":3,"notes":"","blockedReason":"Waiting on brand guidelines","blockedSince":"2026-03-05"},
        {"id":4,"text":"Build frontend","projectId":1,"status":"not_started","priority":"high","plannedStart":"2026-03-09","plannedEnd":"2026-03-18","actualStart":"","actualEnd":"","deps":[2],"subtasks":[{"id":41,"text":"Component library","done":False,"status":"not_started","plannedEnd":"2026-03-12","actualEnd":""},{"id":42,"text":"Page templates","done":False,"status":"not_started","plannedEnd":"2026-03-18","actualEnd":""}],"ownerId":1,"notes":"","blockedReason":"","blockedSince":""},
        {"id":5,"text":"Backend integration","projectId":1,"status":"not_started","priority":"high","plannedStart":"2026-03-09","plannedEnd":"2026-03-16","actualStart":"","actualEnd":"","deps":[2,3],"subtasks":[],"ownerId":2,"notes":"","blockedReason":"","blockedSince":""},
        {"id":6,"text":"QA and testing","projectId":1,"status":"not_started","priority":"medium","plannedStart":"2026-03-19","plannedEnd":"2026-03-22","actualStart":"","actualEnd":"","deps":[4,5],"subtasks":[],"ownerId":3,"notes":"","blockedReason":"","blockedSince":""},
        {"id":7,"text":"Launch","projectId":1,"status":"not_started","priority":"high","plannedStart":"2026-03-23","plannedEnd":"2026-03-23","actualStart":"","actualEnd":"","deps":[6],"subtasks":[],"ownerId":1,"notes":"","blockedReason":"","blockedSince":""},
    ],
    "milestones": [
        {"id":101,"text":"Design Complete","projectId":1,"targetDate":"2026-03-08","actualDate":"","deps":[1,2],"notes":""},
        {"id":102,"text":"Dev Complete","projectId":1,"targetDate":"2026-03-18","actualDate":"","deps":[4,5],"notes":""},
        {"id":103,"text":"Go Live","projectId":1,"targetDate":"2026-03-23","actualDate":"","deps":[6,7],"notes":""},
    ],
    "updates": [],
    "nextId": 200,
}

# ── Python API exposed to JavaScript ───────────────────────
class FocusboardAPI:
    def __init__(self):
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        if not DATA_FILE.exists():
            self._write(DEFAULT_DATA)

    def _read(self):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return dict(DEFAULT_DATA)

    def _write(self, data):
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def load_all(self):
        """Load entire app state from disk."""
        return json.dumps(self._read())

    def save_all(self, json_str):
        """Save entire app state to disk."""
        try:
            data = json.loads(json_str)
            self._write(data)
            return json.dumps({"ok": True})
        except Exception as e:
            return json.dumps({"ok": False, "error": str(e)})

    def get_data_path(self):
        """Return the path to the data file for display in UI."""
        return str(DATA_FILE)


# ── HTML / JS app ───────────────────────────────────────────
HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>Focusboard PRO</title>
<script src="https://unpkg.com/react@18/umd/react.development.js" crossorigin></script>
<script src="https://unpkg.com/react-dom@18/umd/react-dom.development.js" crossorigin></script>
<script src="https://unpkg.com/@babel/standalone/babel.min.js"></script>
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;700;800&family=DM+Sans:wght@300;400;500&display=swap');
*{box-sizing:border-box;margin:0;padding:0;}
html,body,#root{height:100%;width:100%;overflow:hidden;}
body{background:#0a0a0c;font-family:'DM Sans',sans-serif;}
@keyframes slideIn{from{opacity:0;transform:translateY(5px);}to{opacity:1;transform:none;}}
@keyframes pulse{0%,100%{opacity:1;}50%{opacity:0.5;}}
input[type=date]::-webkit-calendar-picker-indicator{filter:invert(0.4);cursor:pointer;}
button:hover{opacity:0.8;}textarea,input,select{outline:none;}
::-webkit-scrollbar{width:4px;height:4px;}
::-webkit-scrollbar-track{background:#0d0d0f;}
::-webkit-scrollbar-thumb{background:#2a2a38;border-radius:99px;}
</style>
</head>
<body>
<div id="root"></div>
<script type="text/babel">
const { useState, useEffect, useRef, useCallback } = React;

// ── pywebview bridge ──────────────────────────────────────
async function pyLoad() {
  try {
    const raw = await window.pywebview.api.load_all();
    return JSON.parse(raw);
  } catch(e) { return null; }
}
async function pySave(state) {
  try {
    await window.pywebview.api.save_all(JSON.stringify(state));
  } catch(e) {}
}
async function pyGetPath() {
  try { return await window.pywebview.api.get_data_path(); } catch(e) { return ""; }
}

// ── helpers ───────────────────────────────────────────────
const sx = (...objs) => Object.assign({}, ...objs);
const COLORS = ["#4D96FF","#6BCB77","#C77DFF","#FF9A3C","#FF6B6B","#FFD93D"];
const PRI_COLOR = {high:"#FF6B6B",medium:"#FFD93D",low:"#6BCB77"};
const STATUSES = ["not_started","in_progress","blocked","complete"];
const SCFG = {
  not_started:{label:"Not Started",color:"#666",bg:"#66666614",border:"#33333330"},
  in_progress:{label:"In Progress",color:"#4D96FF",bg:"#4D96FF14",border:"#4D96FF40"},
  blocked:{label:"Blocked",color:"#FF6B6B",bg:"#FF6B6B14",border:"#FF6B6B44"},
  complete:{label:"Complete",color:"#6BCB77",bg:"#6BCB7714",border:"#6BCB7740"},
};
const RSTATUSES = ["not_started","green","yellow","red","blocked"];
const RCFG = {
  not_started:{label:"Not Started",color:"#666",bg:"#66666614",border:"#33333330"},
  green:{label:"Green",color:"#6BCB77",bg:"#6BCB7714",border:"#6BCB7740"},
  yellow:{label:"Yellow",color:"#FFD93D",bg:"#FFD93D14",border:"#FFD93D44"},
  red:{label:"Red",color:"#FF6B6B",bg:"#FF6B6B14",border:"#FF6B6B44"},
  blocked:{label:"Blocked",color:"#FF9A3C",bg:"#FF9A3C14",border:"#FF9A3C44"},
};
const NEEDS_PTG = ["yellow","red","blocked"];
const MAX_UNDO = 40;

function fmtD(d){return d?new Date(d+"T00:00:00").toLocaleDateString("en-US",{month:"short",day:"numeric"}):"--";}
function toISO(d){const p=new Date(d);return p.getFullYear()+"-"+String(p.getMonth()+1).padStart(2,"0")+"-"+String(p.getDate()).padStart(2,"0");}
function addDays(iso,n){if(!iso)return"";const d=new Date(iso+"T00:00:00");d.setDate(d.getDate()+n);return toISO(d);}
function diffDays(a,b){if(!a||!b)return null;return Math.round((new Date(b+"T00:00:00")-new Date(a+"T00:00:00"))/86400000);}
function todayISO(){return toISO(new Date());}
function avBg(id){return COLORS[((id-1)%COLORS.length+COLORS.length)%COLORS.length];}
function inits(m){return m?(m.firstName[0]+m.lastName[0]).toUpperCase():"?";}

function computeCPM(tasks){
  const byId={};tasks.forEach(t=>{byId[t.id]=t;});
  const dur=id=>{const t=byId[id];if(!t)return 1;const{plannedStart:s,plannedEnd:e}=t;return(s&&e)?Math.max(1,diffDays(s,e)):1;};
  const visited={},order=[];
  const visit=id=>{if(visited[id])return;visited[id]=true;((byId[id]&&byId[id].deps)||[]).forEach(visit);order.push(id);};
  tasks.forEach(t=>visit(t.id));
  const ES={},EF={};
  order.forEach(id=>{
    const t=byId[id];if(!t)return;
    const deps=t.deps||[];
    if(!deps.length){ES[id]=t.plannedStart||"";}
    else{const mx=deps.map(d=>EF[d]||"").filter(Boolean).sort().pop()||"";ES[id]=mx?addDays(mx,1):t.plannedStart||"";}
    EF[id]=ES[id]?addDays(ES[id],dur(id)-1):"";
  });
  const projEnd=Object.values(EF).filter(Boolean).sort().pop()||"";
  const LS={},LF={};
  order.slice().reverse().forEach(id=>{
    const t=byId[id];if(!t)return;
    const succs=tasks.filter(x=>(x.deps||[]).includes(id));
    if(!succs.length){LF[id]=projEnd;}
    else{const mn=succs.map(s=>LS[s.id]||"").filter(Boolean).sort()[0]||"";LF[id]=mn?addDays(mn,-1):"";}
    LS[id]=LF[id]?addDays(LF[id],-(dur(id)-1)):"";
  });
  const slack={},critIds={};
  tasks.forEach(t=>{const sl=(ES[t.id]&&LS[t.id])?diffDays(ES[t.id],LS[t.id]):null;slack[t.id]=sl;if(sl===0)critIds[t.id]=true;});
  return{critIds,slack,ES,EF,LS,LF,projEnd};
}
const computeActualCPM=tasks=>computeCPM(tasks.map(t=>sx(t,{plannedStart:t.actualStart||t.plannedStart,plannedEnd:t.actualEnd||t.plannedEnd})));
function getBlockedImpact(task,cpm,tod){
  if(!task||task.status!=="blocked")return null;
  const s=cpm.slack[task.id];if(s===null||s===undefined)return null;
  const since=task.blockedSince||tod;
  const db=Math.max(0,diffDays(since,tod)||0);
  const du=Math.max(0,s-db);
  const isCrit=!!cpm.critIds[task.id];
  return{slack:s,daysBlocked:db,daysUntilImpact:du,isCritical:isCrit,alreadyImpacting:isCrit||du===0};
}

// ── Loading screen ────────────────────────────────────────
function LoadingScreen(){
  return (
    <div style={{display:"flex",alignItems:"center",justifyContent:"center",height:"100vh",background:"#0a0a0c",flexDirection:"column",gap:16}}>
      <div style={{fontSize:32,color:"#4D96FF"}}>&#9672;</div>
      <div style={{fontFamily:"'Syne',sans-serif",fontWeight:800,fontSize:20,color:"#fff"}}>Focusboard <span style={{color:"#4D96FF"}}>PRO</span></div>
      <div style={{fontSize:12,color:"#444"}}>Loading your data...</div>
    </div>
  );
}

// ── Main App ──────────────────────────────────────────────
function App(){
  const [loaded,setLoaded]=useState(false);
  const [projects,setProjects]=useState([]);
  const [tasks,setTasks]=useState([]);
  const [members,setMembers]=useState([]);
  const [milestones,setMilestones]=useState([]);
  const [updates,setUpdates]=useState([]);
  const [nextId,setNextId]=useState(200);
  const [activeProjId,setActiveProjId]=useState(null);
  const [view,setView]=useState("tasks");
  const [flash,setFlash]=useState(false);
  const [expanded,setExpanded]=useState(null);
  const [showAddMem,setShowAddMem]=useState(false);
  const [showAddProj,setShowAddProj]=useState(false);
  const [newProjName,setNewProjName]=useState("");
  const [newMem,setNewMem]=useState({firstName:"",lastName:"",email:""});
  const [memErr,setMemErr]=useState("");
  const [nf,setNf]=useState({text:"",priority:"medium",plannedStart:"",plannedEnd:"",ownerId:"",deps:[]});
  const [dataPath,setDataPath]=useState("");
  const undoRef=useRef([]);
  const [canUndo,setCanUndo]=useState(false);
  const saveTimer=useRef(null);

  // Load from Python on mount
  useEffect(()=>{
    async function init(){
      // Wait for pywebview to be ready
      let attempts=0;
      while(!window.pywebview && attempts<50){
        await new Promise(r=>setTimeout(r,100));
        attempts++;
      }
      const data=await pyLoad();
      if(data){
        setProjects(data.projects||[]);
        setTasks(data.tasks||[]);
        setMembers(data.members||[]);
        setMilestones(data.milestones||[]);
        setUpdates(data.updates||[]);
        setNextId(data.nextId||200);
      }
      const path=await pyGetPath();
      setDataPath(path);
      setLoaded(true);
    }
    init();
  },[]);

  // Debounced save to Python whenever state changes
  const stateRef=useRef({});
  useEffect(()=>{
    stateRef.current={projects,tasks,members,milestones,updates,nextId};
  },[projects,tasks,members,milestones,updates,nextId]);

  function triggerSave(){
    if(saveTimer.current)clearTimeout(saveTimer.current);
    setFlash(true);
    saveTimer.current=setTimeout(async()=>{
      await pySave(stateRef.current);
      setTimeout(()=>setFlash(false),1200);
    },400);
  }

  function pushUndo(snap){
    undoRef.current=[...undoRef.current,snap].slice(-MAX_UNDO);
    setCanUndo(true);
  }
  function undo(){
    if(!undoRef.current.length)return;
    const snap=undoRef.current[undoRef.current.length-1];
    undoRef.current=undoRef.current.slice(0,-1);
    if(snap.tasks!==undefined)setTasks(snap.tasks);
    if(snap.milestones!==undefined)setMilestones(snap.milestones);
    if(snap.updates!==undefined)setUpdates(snap.updates);
    setCanUndo(undoRef.current.length>0);
    triggerSave();
  }

  const vis=tasks.filter(t=>activeProjId?t.projectId===activeProjId:true);
  const visMS=milestones.filter(m=>activeProjId?m.projectId===activeProjId:true);
  const cpm=computeCPM(vis);
  const acpm=computeActualCPM(vis);
  const tod=todayISO();

  const getMem=id=>members.find(m=>m.id===id);
  const getProj=id=>projects.find(p=>p.id===id);
  const getImpact=task=>getBlockedImpact(task,cpm,tod);
  const dateShift=id=>{const t=tasks.find(x=>x.id===id);if(!t||!t.plannedEnd||!t.actualEnd)return null;return diffDays(t.plannedEnd,t.actualEnd);};

  function updateTask(id,patch){pushUndo({tasks});setTasks(p=>p.map(t=>t.id===id?sx(t,patch):t));triggerSave();}
  function deleteTask(id){
    pushUndo({tasks,milestones});
    setTasks(p=>p.filter(t=>t.id!==id).map(t=>sx(t,{deps:(t.deps||[]).filter(d=>d!==id)})));
    setMilestones(p=>p.map(m=>sx(m,{deps:(m.deps||[]).filter(d=>d!==id)})));
    if(expanded===id)setExpanded(null);
    triggerSave();
  }
  function addTask(){
    if(!nf.text.trim())return;
    const id=nextId;pushUndo({tasks});
    const newT={id,text:nf.text.trim(),projectId:activeProjId||projects[0]?.id||1,status:"not_started",done:false,priority:nf.priority,plannedStart:nf.plannedStart,plannedEnd:nf.plannedEnd,actualStart:"",actualEnd:"",deps:nf.deps.map(Number),subtasks:[],ownerId:nf.ownerId?parseInt(nf.ownerId):null,notes:"",blockedReason:"",blockedSince:""};
    setTasks(p=>[...p,newT]);setNextId(id+1);setNf({text:"",priority:"medium",plannedStart:"",plannedEnd:"",ownerId:"",deps:[]});
    triggerSave();
  }
  function addSubtask(taskId,text){
    if(!text.trim())return;const sid=nextId;pushUndo({tasks});
    const task=tasks.find(t=>t.id===taskId);if(!task)return;
    updateTask(taskId,{subtasks:[...task.subtasks,{id:sid,text:text.trim(),done:false,status:"not_started",plannedEnd:"",actualEnd:""}]});
    setNextId(sid+1);
  }
  function updateSub(taskId,subId,patch){const task=tasks.find(t=>t.id===taskId);if(!task)return;pushUndo({tasks});updateTask(taskId,{subtasks:task.subtasks.map(s=>s.id===subId?sx(s,patch):s)});}
  function deleteSub(taskId,subId){const task=tasks.find(t=>t.id===taskId);if(!task)return;pushUndo({tasks});updateTask(taskId,{subtasks:task.subtasks.filter(s=>s.id!==subId)});}
  function addMilestone(ms){pushUndo({milestones});setMilestones(p=>[...p,sx({id:nextId,actualDate:"",notes:""},ms)]);setNextId(n=>n+1);triggerSave();}
  function updateMilestone(id,patch){pushUndo({milestones});setMilestones(p=>p.map(m=>m.id===id?sx(m,patch):m));triggerSave();}
  function deleteMilestone(id){pushUndo({milestones});setMilestones(p=>p.filter(m=>m.id!==id));triggerSave();}
  function addUpdate(upd){pushUndo({updates});setUpdates(p=>[...p,sx({id:nextId,createdAt:todayISO(),ptg:""},upd)]);setNextId(n=>n+1);triggerSave();}
  function updateUpdate(id,patch){pushUndo({updates});setUpdates(p=>p.map(u=>u.id===id?sx(u,patch):u));triggerSave();}
  function deleteUpdate(id){pushUndo({updates});setUpdates(p=>p.filter(u=>u.id!==id));triggerSave();}
  function addProject(){if(!newProjName.trim())return;setProjects(p=>[...p,{id:nextId,name:newProjName.trim(),color:COLORS[p.length%COLORS.length]}]);setNextId(n=>n+1);setNewProjName("");setShowAddProj(false);triggerSave();}
  function addMember(){
    setMemErr("");
    if(!newMem.firstName.trim()||!newMem.lastName.trim())return setMemErr("Name required.");
    if(!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(newMem.email))return setMemErr("Valid email required.");
    if(members.some(m=>m.email.toLowerCase()===newMem.email.toLowerCase()))return setMemErr("Email exists.");
    setMembers(p=>[...p,sx({id:nextId},newMem)]);setNextId(n=>n+1);setNewMem({firstName:"",lastName:"",email:""});setShowAddMem(false);triggerSave();
  }

  if(!loaded)return <LoadingScreen/>;

  const sp={tasks:vis,allTasks:tasks,members,projects,milestones:visMS,allMilestones:milestones,updates,cpm,acpm,tod,expanded,setExpanded,updateTask,deleteTask,addSubtask,updateSub,deleteSub,nf,setNf,addTask,dateShift,activeProjId,getMem,getProj,getImpact,nextId,addMilestone,updateMilestone,deleteMilestone,addUpdate,updateUpdate,deleteUpdate};
  const blockedCount=vis.filter(t=>t.status==="blocked").length;
  const doneCount=tasks.filter(t=>t.status==="complete").length;

  return (
    <div style={C.root}>
      <aside style={C.sidebar}>
        <div style={C.brand}>
          <span style={{fontSize:20,color:"#4D96FF"}}>&#9672;</span>
          <span style={C.brandName}>Focusboard</span>
          <span style={C.brandPro}>PRO</span>
        </div>
        <nav style={C.nav}>
          <div style={C.sLabel}>Views</div>
          {[["tasks","&#9776;","Task List"],["kanban","&#8862;","Kanban"],["owner","&#128100;","By Owner"],["milestones","&#9671;","Milestones"],["updates","&#9733;","Status Updates"],["gantt","&#9646;","Timeline"],["critical","&#9670;","Critical Path"]].map(item=>(
            <button key={item[0]} style={sx(C.navBtn,view===item[0]?C.navBtnOn:{})} onClick={()=>setView(item[0])}>
              <span dangerouslySetInnerHTML={{__html:item[1]}} style={C.navIco}/>
              <span style={{flex:1}}>{item[2]}</span>
              {item[0]==="kanban"&&blockedCount>0&&<span style={C.blockedPip}>{blockedCount}</span>}
            </button>
          ))}
          <div style={C.sLabel}>Projects</div>
          <button style={sx(C.navBtn,activeProjId===null?C.navBtnOn:{})} onClick={()=>setActiveProjId(null)}>
            <span style={sx(C.dot,{color:"#555"})}>&#9679;</span>
            <span style={C.navLbl}>All Projects</span>
            <span style={C.navCt}>{tasks.length}</span>
          </button>
          {projects.map(p=>(
            <button key={p.id} style={sx(C.navBtn,activeProjId===p.id?C.navBtnOn:{})} onClick={()=>setActiveProjId(p.id)}>
              <span style={sx(C.dot,{color:p.color})}>&#9679;</span>
              <span style={C.navLbl}>{p.name}</span>
              <span style={C.navCt}>{tasks.filter(t=>t.projectId===p.id).length}</span>
            </button>
          ))}
          {showAddProj
            ?<div style={C.inlineRow}><input style={C.inlineIn} autoFocus placeholder="Project name" value={newProjName} onChange={e=>setNewProjName(e.target.value)} onKeyDown={e=>{if(e.key==="Enter")addProject();}}/><button style={C.inlineBtn} onClick={addProject}>+</button></div>
            :<button style={C.addDash} onClick={()=>setShowAddProj(true)}>+ New Project</button>
          }
          <div style={C.sLabel}>Team</div>
          {members.map(m=>(
            <div key={m.id} style={C.memRow}>
              <div style={sx(C.av,{background:avBg(m.id),width:26,height:26,fontSize:10})}>{inits(m)}</div>
              <div><div style={C.memName}>{m.firstName} {m.lastName}</div><div style={C.memEmail}>{m.email}</div></div>
            </div>
          ))}
          <button style={C.addDash} onClick={()=>setShowAddMem(true)}>+ Add Member</button>
        </nav>
        <div style={C.progBox}>
          <div style={C.progRow}><span>Overall</span><span style={C.progFrac}>{doneCount}/{tasks.length}</span></div>
          <div style={C.track}><div style={sx(C.fill,{width:tasks.length?(doneCount/tasks.length*100)+"%":"0%"})}/></div>
          {blockedCount>0&&<div style={C.blockedAlert}>&#9675; {blockedCount} blocked</div>}
        </div>
        <div style={C.undoBar}>
          <button style={sx(C.undoBtn,canUndo?C.undoBtnOn:{})} onClick={undo} disabled={!canUndo}>&#8630; Undo</button>
          <span style={sx(C.savedDot,{opacity:flash?1:0})}>&#10003; Saved</span>
        </div>
        {dataPath&&<div style={C.dataPath} title={dataPath}>&#128190; {dataPath.split("/").slice(-2).join("/")}</div>}
      </aside>
      <main style={C.main}>
        {view==="tasks"      && <TasksView {...sp}/>}
        {view==="kanban"     && <KanbanView {...sp}/>}
        {view==="owner"      && <OwnerView {...sp}/>}
        {view==="milestones" && <MilestonesView {...sp}/>}
        {view==="updates"    && <UpdatesView {...sp}/>}
        {view==="gantt"      && <GanttView {...sp}/>}
        {view==="critical"   && <CriticalView {...sp}/>}
      </main>
      {showAddMem&&(
        <div style={C.overlay} onClick={()=>setShowAddMem(false)}>
          <div style={C.modal} onClick={e=>e.stopPropagation()}>
            <div style={C.modalHd}><span style={C.modalTtl}>Add Team Member</span><button style={C.modalX} onClick={()=>setShowAddMem(false)}>&#10005;</button></div>
            <div style={C.modalBd}>
              <div style={C.fieldRow}>
                <FF label="First Name" value={newMem.firstName} onChange={v=>setNewMem(p=>sx(p,{firstName:v}))} placeholder="Alex"/>
                <FF label="Last Name"  value={newMem.lastName}  onChange={v=>setNewMem(p=>sx(p,{lastName:v}))}  placeholder="Rivera"/>
              </div>
              <FF label="Email" value={newMem.email} onChange={v=>setNewMem(p=>sx(p,{email:v}))} placeholder="alex@co.com" type="email"/>
              {memErr&&<div style={C.errMsg}>{memErr}</div>}
              <button style={C.modalPrim} onClick={addMember}>Add Member</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

// ── TaskCard ──────────────────────────────────────────────
function TaskCard({task,cpm,getMem,getProj,getImpact,updateTask,deleteTask,expanded,setExpanded,allTasks,members,addSubtask,updateSub,deleteSub,dateShift,idx=0}){
  const [subIn,setSubIn]=useState("");
  const own=getMem(task.ownerId),proj=getProj(task.projectId);
  const isCrit=!!cpm.critIds[task.id],slack=cpm.slack[task.id];
  const shift=dateShift(task.id),impact=getImpact(task),isExp=expanded===task.id;
  const cfg=SCFG[task.status||"not_started"];
  function cycleStatus(){
    const i=STATUSES.indexOf(task.status||"not_started"),next=STATUSES[(i+1)%STATUSES.length];
    const patch={status:next};if(next==="blocked")patch.blockedSince=todayISO();if(next==="complete"){patch.done=true;patch.actualEnd=task.actualEnd||todayISO();}
    updateTask(task.id,patch);
  }
  const toggleDep=depId=>{const deps=task.deps||[];const has=deps.includes(depId);updateTask(task.id,{deps:has?deps.filter(d=>d!==depId):[...deps,depId]});};
  return (
    <div style={sx(C.card,isCrit?C.cardCrit:{},task.status==="blocked"?C.cardBlocked:{},{animationDelay:idx*25+"ms"})}>
      {isCrit&&<div style={C.critStripe}/>}
      {task.status==="blocked"&&!isCrit&&<div style={C.blockedStripe}/>}
      {impact&&(
        <div style={sx(C.impactBar,impact.alreadyImpacting?C.impactRed:C.impactAmber)}>
          <b>{impact.alreadyImpacting?"!! CP BLOCKED":">> "}</b>
          <span>{impact.alreadyImpacting?" "+impact.daysBlocked+"d blocked":"Impacts CP in "+impact.daysUntilImpact+"d | "+impact.daysBlocked+"d blocked | "+impact.slack+"d slack"}</span>
          {task.blockedReason&&<span style={{fontSize:11,fontStyle:"italic",marginLeft:8,opacity:0.7}}>{task.blockedReason}</span>}
        </div>
      )}
      <div style={C.cardMain}>
        <button style={sx(C.stPill,{background:cfg.bg,borderColor:cfg.border,color:cfg.color})} onClick={cycleStatus}>
          {{"not_started":"-","in_progress":">","blocked":"X","complete":"v"}[task.status||"not_started"]}
        </button>
        <div style={C.cardBody}>
          <div style={C.cardTopRow}>
            <span style={sx(C.cardTxt,task.status==="complete"?{textDecoration:"line-through",color:"#555"}:{})}>{task.text}</span>
            <div style={C.badges}>
              {isCrit&&<span style={C.bCrit}>&#9670; Critical</span>}
              {!isCrit&&slack!=null&&<span style={C.bSlack}>+{slack}d</span>}
              {shift!=null&&shift>0&&<span style={C.bPush}>+{shift}d pushed</span>}
              {shift!=null&&shift<0&&<span style={C.bPull}>{shift}d pulled</span>}
            </div>
          </div>
          <div style={C.cardMetaRow}>
            {proj&&<span style={sx(C.projTag,{background:proj.color+"22",color:proj.color})}>{proj.name}</span>}
            <span style={sx(C.dot2,{background:PRI_COLOR[task.priority]})}/>
            <span style={sx(C.stTag,{background:cfg.bg,color:cfg.color,borderColor:cfg.border})}>{cfg.label}</span>
            {task.plannedStart&&<span style={C.dateTag}>{fmtD(task.plannedStart)} - {fmtD(task.plannedEnd)}</span>}
            {task.subtasks?.length>0&&<span style={C.subCt}>{task.subtasks.filter(s=>s.done).length}/{task.subtasks.length} sub</span>}
          </div>
        </div>
        {own&&<div style={C.ownerChip}><div style={sx(C.av,{background:avBg(own.id),width:22,height:22,fontSize:9})}>{inits(own)}</div><div><div style={C.ownerNm}>{own.firstName} {own.lastName}</div><div style={C.ownerEm}>{own.email}</div></div></div>}
        <button style={C.expBtn} onClick={()=>setExpanded(isExp?null:task.id)}>{isExp?"^":"v"}</button>
        <button style={C.delBtn} onClick={()=>deleteTask(task.id)}>x</button>
      </div>
      {isExp&&(
        <div style={C.expPanel}>
          <div style={C.expGrid}>
            <div style={C.expSec}>
              <div style={C.expTtl}>Planned Dates</div>
              <div style={C.expRow}><span style={C.expLbl}>Start</span><input type="date" style={C.expIn} value={task.plannedStart||""} onChange={e=>updateTask(task.id,{plannedStart:e.target.value})}/></div>
              <div style={C.expRow}><span style={C.expLbl}>End</span><input type="date" style={C.expIn} value={task.plannedEnd||""} onChange={e=>updateTask(task.id,{plannedEnd:e.target.value})}/></div>
            </div>
            <div style={C.expSec}>
              <div style={C.expTtl}>Actual Dates</div>
              <div style={C.expRow}><span style={C.expLbl}>Start</span><input type="date" style={C.expIn} value={task.actualStart||""} onChange={e=>updateTask(task.id,{actualStart:e.target.value})}/></div>
              <div style={C.expRow}><span style={C.expLbl}>End</span><input type="date" style={C.expIn} value={task.actualEnd||""} onChange={e=>updateTask(task.id,{actualEnd:e.target.value})}/></div>
            </div>
            <div style={C.expSec}>
              <div style={C.expTtl}>Status</div>
              <select style={C.expSel} value={task.status||"not_started"} onChange={e=>{const v=e.target.value,patch={status:v};if(v==="blocked")patch.blockedSince=todayISO();if(v==="complete"){patch.done=true;patch.actualEnd=task.actualEnd||todayISO();}updateTask(task.id,patch);}}>
                {STATUSES.map(st=><option key={st} value={st}>{SCFG[st].label}</option>)}
              </select>
              {task.status==="blocked"&&<input style={sx(C.expIn,{marginTop:6,width:"100%"})} placeholder="Reason blocked..." value={task.blockedReason||""} onChange={e=>updateTask(task.id,{blockedReason:e.target.value})}/>}
            </div>
            <div style={C.expSec}>
              <div style={C.expTtl}>Owner</div>
              <select style={C.expSel} value={task.ownerId||""} onChange={e=>updateTask(task.id,{ownerId:e.target.value?parseInt(e.target.value):null})}>
                <option value="">Unassigned</option>
                {members.map(m=><option key={m.id} value={m.id}>{m.firstName} {m.lastName}</option>)}
              </select>
            </div>
          </div>
          <div style={C.expSec}>
            <div style={C.expTtl}>Dependencies</div>
            <div style={C.depGrid}>
              {allTasks.filter(t=>t.id!==task.id).map(t=>{
                const ch=(task.deps||[]).includes(t.id);
                return <label key={t.id} style={sx(C.depOpt,ch?C.depOn:{})}><input type="checkbox" style={{display:"none"}} checked={ch} onChange={()=>toggleDep(t.id)}/><span style={C.depBox}>{ch?"v":""}</span><span>{t.text}</span></label>;
              })}
            </div>
          </div>
          <div style={C.expSec}>
            <div style={C.expTtl}>Subtasks</div>
            {(task.subtasks||[]).map(st=>(
              <div key={st.id} style={C.subRow}>
                <button style={sx(C.stChk,st.done?{background:"#4D96FF",borderColor:"#4D96FF"}:{})} onClick={()=>updateSub(task.id,st.id,{done:!st.done,status:!st.done?"complete":"not_started"})}>{st.done?"v":""}</button>
                <span style={sx({flex:1,fontSize:13,color:"#bbb"},st.done?{textDecoration:"line-through"}:{},st.status==="blocked"?{color:"#FF6B6B"}:{})}>{st.text}</span>
                <select style={C.stSel} value={st.status||"not_started"} onChange={e=>updateSub(task.id,st.id,{status:e.target.value,done:e.target.value==="complete"})}>
                  {STATUSES.map(s=><option key={s} value={s}>{SCFG[s].label}</option>)}
                </select>
                <input type="date" style={C.stDate} value={st.plannedEnd||""} onChange={e=>updateSub(task.id,st.id,{plannedEnd:e.target.value})}/>
                <input type="date" style={sx(C.stDate,{color:"#6BCB77"})} value={st.actualEnd||""} onChange={e=>updateSub(task.id,st.id,{actualEnd:e.target.value})}/>
                <button style={C.stDel} onClick={()=>deleteSub(task.id,st.id)}>x</button>
              </div>
            ))}
            <div style={C.stAddRow}>
              <input style={C.stIn} placeholder="Add subtask..." value={subIn} onChange={e=>setSubIn(e.target.value)} onKeyDown={e=>{if(e.key==="Enter"){addSubtask(task.id,subIn);setSubIn("");}}}/>
              <button style={C.stAddBtn} onClick={()=>{addSubtask(task.id,subIn);setSubIn("");}}>+</button>
            </div>
          </div>
          <div style={C.expSec}>
            <div style={C.expTtl}>Notes</div>
            <textarea style={C.notes} rows={3} value={task.notes||""} onChange={e=>updateTask(task.id,{notes:e.target.value})} placeholder="Notes, links, context..."/>
          </div>
        </div>
      )}
    </div>
  );
}

function AddForm({nf,setNf,addTask,members}){
  return (
    <div style={C.addBox}>
      <div style={C.addRow}>
        <input style={C.addIn} placeholder="Add a task..." value={nf.text} onChange={e=>setNf(x=>sx(x,{text:e.target.value}))} onKeyDown={e=>{if(e.key==="Enter")addTask();}}/>
        <button style={C.addBtn} onClick={addTask}>Add</button>
      </div>
      <div style={C.addMeta}>
        <select style={C.sel} value={nf.priority} onChange={e=>setNf(x=>sx(x,{priority:e.target.value}))}>
          <option value="high">High</option><option value="medium">Medium</option><option value="low">Low</option>
        </select>
        <span style={C.metaLbl}>Planned:</span>
        <input type="date" style={C.dateIn} value={nf.plannedStart} onChange={e=>setNf(x=>sx(x,{plannedStart:e.target.value}))}/>
        <span style={C.metaLbl}>to</span>
        <input type="date" style={C.dateIn} value={nf.plannedEnd} onChange={e=>setNf(x=>sx(x,{plannedEnd:e.target.value}))}/>
        <select style={C.sel} value={nf.ownerId} onChange={e=>setNf(x=>sx(x,{ownerId:e.target.value}))}>
          <option value="">Unassigned</option>
          {members.map(m=><option key={m.id} value={m.id}>{m.firstName} {m.lastName}</option>)}
        </select>
      </div>
    </div>
  );
}

function TasksView(p){
  const [filter,setFilter]=useState("all");
  const vis=p.tasks.filter(t=>{
    if(filter==="blocked")return t.status==="blocked";
    if(filter==="done")return t.status==="complete";
    if(filter==="active")return t.status!=="complete";
    return true;
  });
  const blkCt=p.tasks.filter(t=>t.status==="blocked").length;
  return (
    <div>
      <div style={C.ph}>
        <div>
          <h1 style={C.h1}>{p.activeProjId&&p.projects.find(x=>x.id===p.activeProjId)?.name||"All Tasks"}</h1>
          <p style={C.subh}>{vis.filter(t=>t.status!=="complete").length} remaining | {blkCt} blocked</p>
        </div>
        <div style={C.filters}>
          {[["all","All"],["active","Active"],["blocked","Blocked"],["done","Done"]].map(([v,l])=>(
            <button key={v} style={sx(C.fBtn,filter===v?C.fOn:{},v==="blocked"&&blkCt>0?{borderColor:"#FF6B6B44",color:"#FF6B6B"}:{})} onClick={()=>setFilter(v)}>{l}</button>
          ))}
        </div>
      </div>
      <AddForm {...p}/>
      <div style={C.tList}>
        {vis.map((t,i)=><TaskCard key={t.id} task={t} idx={i} {...p}/>)}
        {vis.length===0&&<div style={C.empty}>No tasks here</div>}
      </div>
    </div>
  );
}

function MilestonesView(p){
  const [nms,setNms]=useState({text:"",targetDate:"",deps:[]});
  const [expMs,setExpMs]=useState(null);
  function getMsHealth(ms){
    const deps=(ms.deps||[]).map(d=>p.allTasks.find(t=>t.id===d)).filter(Boolean);
    if(ms.actualDate)return{color:"#6BCB77",label:"Complete",pct:100};
    if(!deps.length)return{color:"#666",label:"Not Started",pct:0};
    const done=deps.filter(t=>t.status==="complete").length;
    const pct=done/deps.length*100;
    if(done===deps.length)return{color:"#6BCB77",label:"Complete",pct};
    if(deps.some(t=>t.status==="blocked"))return{color:"#FF6B6B",label:"At Risk",pct};
    if(deps.some(t=>t.status==="in_progress"))return{color:"#4D96FF",label:"In Progress",pct};
    return{color:"#666",label:"Not Started",pct};
  }
  function submit(){
    if(!nms.text.trim())return;
    p.addMilestone({text:nms.text.trim(),targetDate:nms.targetDate,deps:nms.deps.map(Number),projectId:p.activeProjId||p.projects[0]?.id||1});
    setNms({text:"",targetDate:"",deps:[]});
  }
  return (
    <div>
      <div style={C.ph}><div><h1 style={C.h1}>Milestones</h1><p style={C.subh}>{p.milestones.length} milestones | {p.milestones.filter(m=>m.actualDate).length} complete</p></div></div>
      <div style={sx(C.addBox,{marginBottom:20})}>
        <div style={C.addRow}>
          <input style={C.addIn} placeholder="Milestone name..." value={nms.text} onChange={e=>setNms(x=>sx(x,{text:e.target.value}))} onKeyDown={e=>{if(e.key==="Enter")submit();}}/>
          <input type="date" style={sx(C.dateIn,{flex:"0 0 auto"})} value={nms.targetDate} onChange={e=>setNms(x=>sx(x,{targetDate:e.target.value}))}/>
          <button style={C.addBtn} onClick={submit}>Add Milestone</button>
        </div>
        {p.allTasks.length>0&&<div style={C.expSec}><div style={C.expTtl}>Task Dependencies</div><div style={C.depGrid}>{p.allTasks.map(t=>{const ch=nms.deps.includes(t.id);return <label key={t.id} style={sx(C.depOpt,ch?C.depOn:{})}><input type="checkbox" style={{display:"none"}} checked={ch} onChange={()=>setNms(x=>{const deps=x.deps;const has=deps.includes(t.id);return sx(x,{deps:has?deps.filter(d=>d!==t.id):[...deps,t.id]});})}/><span style={C.depBox}>{ch?"v":""}</span><span>{t.text}</span></label>;})}</div></div>}
      </div>
      <div style={C.tList}>
        {p.milestones.map((ms,i)=>{
          const health=getMsHealth(ms);
          const depTasks=(ms.deps||[]).map(d=>p.allTasks.find(t=>t.id===d)).filter(Boolean);
          const doneDeps=depTasks.filter(t=>t.status==="complete").length;
          const daysUntil=ms.targetDate?diffDays(todayISO(),ms.targetDate):null;
          const isExp=expMs===ms.id;
          return (
            <div key={ms.id} style={sx(C.card,health.color==="#FF6B6B"?{borderColor:"#FF6B6B44"}:{},{animationDelay:i*30+"ms"})}>
              <div style={sx(C.cardMain,{gap:12})}>
                <div style={sx(C.msBadge,{background:health.color+"22",borderColor:health.color+"44",color:health.color})}>&#9671;</div>
                <div style={C.cardBody}>
                  <div style={C.cardTopRow}>
                    <span style={sx(C.cardTxt,{fontSize:14.5,fontWeight:600})}>{ms.text}</span>
                    <div style={C.badges}>
                      <span style={sx(C.stTag,{background:health.color+"22",color:health.color,borderColor:health.color+"44"})}>{health.label}</span>
                      {daysUntil!==null&&!ms.actualDate&&daysUntil>=0&&<span style={sx(C.bSlack,daysUntil<=3?{color:"#FF6B6B",background:"#FF6B6B14",borderColor:"#FF6B6B44"}:{})}>{daysUntil===0?"Today":daysUntil+"d away"}</span>}
                      {daysUntil!==null&&!ms.actualDate&&daysUntil<0&&<span style={C.bPush}>{Math.abs(daysUntil)}d overdue</span>}
                    </div>
                  </div>
                  <div style={C.cardMetaRow}>
                    <span style={C.dateTag}>Target: {fmtD(ms.targetDate)}</span>
                    {ms.actualDate&&<span style={sx(C.dateTag,{color:"#6BCB77"})}>Actual: {fmtD(ms.actualDate)}</span>}
                    {depTasks.length>0&&<span style={C.subCt}>{doneDeps}/{depTasks.length} deps</span>}
                  </div>
                </div>
                {depTasks.length>0&&<div style={C.msProgWrap}><div style={C.track}><div style={sx(C.fill,{width:health.pct+"%"})}/></div><span style={{fontSize:10,color:"#555",marginTop:3}}>{doneDeps}/{depTasks.length}</span></div>}
                <button style={C.expBtn} onClick={()=>setExpMs(isExp?null:ms.id)}>{isExp?"^":"v"}</button>
                <button style={C.delBtn} onClick={()=>p.deleteMilestone(ms.id)}>x</button>
              </div>
              {isExp&&(
                <div style={C.expPanel}>
                  <div style={C.expGrid}>
                    <div style={C.expSec}><div style={C.expTtl}>Target Date</div><input type="date" style={C.expIn} value={ms.targetDate||""} onChange={e=>p.updateMilestone(ms.id,{targetDate:e.target.value})}/></div>
                    <div style={C.expSec}><div style={C.expTtl}>Actual Date</div><input type="date" style={C.expIn} value={ms.actualDate||""} onChange={e=>p.updateMilestone(ms.id,{actualDate:e.target.value})}/></div>
                    <div style={C.expSec}><div style={C.expTtl}>Notes</div><textarea style={sx(C.notes,{minWidth:180})} rows={2} value={ms.notes||""} onChange={e=>p.updateMilestone(ms.id,{notes:e.target.value})} placeholder="Notes..."/></div>
                  </div>
                  <div style={C.expSec}>
                    <div style={C.expTtl}>Task Dependencies</div>
                    <div style={C.depGrid}>
                      {p.allTasks.map(t=>{
                        const ch=(ms.deps||[]).includes(t.id);const tcfg=SCFG[t.status||"not_started"];
                        return <label key={t.id} style={sx(C.depOpt,ch?C.depOn:{},t.status==="complete"?{opacity:0.6}:{})}><input type="checkbox" style={{display:"none"}} checked={ch} onChange={()=>{const deps=ms.deps||[];const has=deps.includes(t.id);p.updateMilestone(ms.id,{deps:has?deps.filter(d=>d!==t.id):[...deps,t.id]});}}/>  <span style={C.depBox}>{ch?"v":""}</span><span style={sx({},t.status==="complete"?{textDecoration:"line-through"}:{})}>{t.text}</span><span style={{fontSize:10,marginLeft:4,color:tcfg.color}}>{{complete:"v",blocked:"X",in_progress:">",not_started:"-"}[t.status||"not_started"]}</span></label>;
                      })}
                    </div>
                  </div>
                </div>
              )}
            </div>
          );
        })}
        {p.milestones.length===0&&<div style={C.empty}>No milestones yet.</div>}
      </div>
    </div>
  );
}

function UpdatesView(p){
  const [showForm,setShowForm]=useState(false);
  const [nUpd,setNUpd]=useState({taskId:"",reportStatus:"not_started",dueDate:"",actualDate:"",summary:"",ptg:""});
  const [filterOwner,setFilterOwner]=useState("all");
  const [editId,setEditId]=useState(null);
  const [editData,setEditData]=useState({});
  const ownerIds=p.allTasks.map(t=>t.ownerId).filter((v,i,a)=>v&&a.indexOf(v)===i);
  const filtered=filterOwner==="all"?p.updates:p.updates.filter(u=>{const t=p.allTasks.find(x=>x.id===u.taskId);return t&&t.ownerId===parseInt(filterOwner);});
  const getTaskName=tid=>{const t=p.allTasks.find(x=>x.id===tid);return t?t.text:"(deleted)";};
  const getTaskOwner=tid=>{const t=p.allTasks.find(x=>x.id===tid);return t?p.getMem(t.ownerId):null;};
  function submit(){
    if(!nUpd.taskId||!nUpd.summary.trim())return;
    if(NEEDS_PTG.includes(nUpd.reportStatus)&&!nUpd.ptg.trim())return;
    p.addUpdate({taskId:parseInt(nUpd.taskId),reportStatus:nUpd.reportStatus,dueDate:nUpd.dueDate,actualDate:nUpd.actualDate,summary:nUpd.summary.trim(),ptg:nUpd.ptg.trim()});
    setNUpd({taskId:"",reportStatus:"not_started",dueDate:"",actualDate:"",summary:"",ptg:""});setShowForm(false);
  }
  function saveEdit(id){p.updateUpdate(id,editData);setEditId(null);setEditData({});}
  const cur=editData;
  return (
    <div>
      <div style={C.ph}>
        <div><h1 style={C.h1}>Status Updates</h1><p style={C.subh}>Owner progress reports | PTG = Path to Green</p></div>
        <div style={{display:"flex",gap:8,alignItems:"center"}}>
          <select style={C.sel} value={filterOwner} onChange={e=>setFilterOwner(e.target.value)}>
            <option value="all">All Owners</option>
            {ownerIds.map(id=>{const m=p.getMem(id);return m?<option key={id} value={id}>{m.firstName} {m.lastName}</option>:null;})}
          </select>
          <button style={C.addBtn} onClick={()=>setShowForm(!showForm)}>+ New Update</button>
        </div>
      </div>
      {showForm&&(
        <div style={sx(C.addBox,{marginBottom:24})}>
          <div style={{fontFamily:"'Syne',sans-serif",fontWeight:700,fontSize:14,color:"#ddd",marginBottom:10}}>New Status Update</div>
          <div style={C.expGrid}>
            <div style={C.expSec}><div style={C.expTtl}>Task *</div><select style={sx(C.expSel,{minWidth:180})} value={nUpd.taskId} onChange={e=>{const t=p.allTasks.find(x=>x.id===parseInt(e.target.value));setNUpd(x=>sx(x,{taskId:e.target.value,dueDate:t?.plannedEnd||"",actualDate:t?.actualEnd||""}));}}><option value="">Select task...</option>{p.allTasks.map(t=>{const own=p.getMem(t.ownerId);return <option key={t.id} value={t.id}>{t.text}{own?" ("+own.firstName+")":""}</option>;})}</select></div>
            <div style={C.expSec}><div style={C.expTtl}>Status *</div><select style={C.expSel} value={nUpd.reportStatus} onChange={e=>setNUpd(x=>sx(x,{reportStatus:e.target.value}))}>{RSTATUSES.map(s=><option key={s} value={s}>{RCFG[s].label}</option>)}</select></div>
            <div style={C.expSec}><div style={C.expTtl}>Due Date</div><input type="date" style={C.expIn} value={nUpd.dueDate} onChange={e=>setNUpd(x=>sx(x,{dueDate:e.target.value}))}/></div>
            <div style={C.expSec}><div style={C.expTtl}>Actual Date</div><input type="date" style={C.expIn} value={nUpd.actualDate} onChange={e=>setNUpd(x=>sx(x,{actualDate:e.target.value}))}/></div>
          </div>
          <div style={C.expSec}><div style={C.expTtl}>Summary *</div><textarea style={sx(C.notes,{width:"100%"})} rows={2} value={nUpd.summary} onChange={e=>setNUpd(x=>sx(x,{summary:e.target.value}))} placeholder="Progress summary..."/></div>
          {NEEDS_PTG.includes(nUpd.reportStatus)&&<div style={C.expSec}><div style={sx(C.expTtl,{color:"#FFD93D"})}>PTG (Path to Green) *</div><textarea style={sx(C.notes,{width:"100%",borderColor:"#FFD93D33"})} rows={2} value={nUpd.ptg} onChange={e=>setNUpd(x=>sx(x,{ptg:e.target.value}))} placeholder="Steps to restore green status..."/></div>}
          <div style={{display:"flex",gap:8,marginTop:4}}><button style={C.addBtn} onClick={submit}>Submit</button><button style={sx(C.addBtn,{background:"transparent",border:"1px solid #252530",color:"#666"})} onClick={()=>setShowForm(false)}>Cancel</button></div>
        </div>
      )}
      {filtered.length===0&&!showForm&&<div style={C.empty}>No status updates yet.</div>}
      <div style={C.tList}>
        {filtered.slice().reverse().map(upd=>{
          const rcfg=RCFG[upd.reportStatus||"not_started"];
          const taskOwner=getTaskOwner(upd.taskId);
          const isEditing=editId===upd.id;
          const ec=isEditing?cur:upd;
          return (
            <div key={upd.id} style={sx(C.card,{borderLeftWidth:3,borderLeftStyle:"solid",borderLeftColor:rcfg.color})}>
              <div style={C.cardMain}>
                <div style={sx(C.rStatusBadge,{background:rcfg.bg,borderColor:rcfg.border,color:rcfg.color})}>{rcfg.label}</div>
                <div style={C.cardBody}>
                  <div style={C.cardTopRow}><span style={C.cardTxt}>{getTaskName(upd.taskId)}</span><div style={C.badges}><span style={sx(C.dateTag,{color:"#555"})}>Reported: {fmtD(upd.createdAt)}</span></div></div>
                  <div style={C.cardMetaRow}>
                    {upd.dueDate&&<span style={C.dateTag}>Due: {fmtD(upd.dueDate)}</span>}
                    {upd.actualDate&&<span style={sx(C.dateTag,{color:"#6BCB77"})}>Actual: {fmtD(upd.actualDate)}</span>}
                    {taskOwner&&<span style={sx(C.projTag,{background:avBg(taskOwner.id)+"22",color:avBg(taskOwner.id)})}>{taskOwner.firstName} {taskOwner.lastName}</span>}
                  </div>
                </div>
                <div style={{display:"flex",gap:4}}><button style={sx(C.expBtn,{color:"#4D96FF88",fontSize:11})} onClick={()=>{setEditId(isEditing?null:upd.id);setEditData(sx({},upd));}}>edit</button><button style={C.delBtn} onClick={()=>p.deleteUpdate(upd.id)}>x</button></div>
              </div>
              <div style={{padding:"0 16px 14px"}}>
                {isEditing?(
                  <div style={{display:"flex",flexDirection:"column",gap:10}}>
                    <div style={sx(C.expGrid,{flexWrap:"wrap"})}>
                      <div style={C.expSec}><div style={C.expTtl}>Status</div><select style={C.expSel} value={ec.reportStatus||"not_started"} onChange={e=>setEditData(x=>sx(x,{reportStatus:e.target.value}))}>{RSTATUSES.map(s=><option key={s} value={s}>{RCFG[s].label}</option>)}</select></div>
                      <div style={C.expSec}><div style={C.expTtl}>Due Date</div><input type="date" style={C.expIn} value={ec.dueDate||""} onChange={e=>setEditData(x=>sx(x,{dueDate:e.target.value}))}/></div>
                      <div style={C.expSec}><div style={C.expTtl}>Actual Date</div><input type="date" style={C.expIn} value={ec.actualDate||""} onChange={e=>setEditData(x=>sx(x,{actualDate:e.target.value}))}/></div>
                    </div>
                    <div style={C.expSec}><div style={C.expTtl}>Summary</div><textarea style={sx(C.notes,{width:"100%"})} rows={2} value={ec.summary||""} onChange={e=>setEditData(x=>sx(x,{summary:e.target.value}))}/></div>
                    {NEEDS_PTG.includes(ec.reportStatus)&&<div style={C.expSec}><div style={sx(C.expTtl,{color:"#FFD93D"})}>PTG</div><textarea style={sx(C.notes,{width:"100%",borderColor:"#FFD93D33"})} rows={2} value={ec.ptg||""} onChange={e=>setEditData(x=>sx(x,{ptg:e.target.value}))}/></div>}
                    <div style={{display:"flex",gap:8}}><button style={sx(C.addBtn,{padding:"7px 16px",fontSize:12})} onClick={()=>saveEdit(upd.id)}>Save</button><button style={sx(C.addBtn,{padding:"7px 16px",fontSize:12,background:"transparent",border:"1px solid #252530",color:"#666"})} onClick={()=>setEditId(null)}>Cancel</button></div>
                  </div>
                ):(
                  <div style={{display:"flex",flexDirection:"column",gap:8}}>
                    <p style={{fontSize:13,color:"#bbb",lineHeight:1.6,margin:0}}>{upd.summary}</p>
                    {upd.ptg&&<div style={sx(C.ptgBox,{borderColor:rcfg.color+"44",background:rcfg.color+"08"})}><span style={sx(C.ptgLabel,{color:rcfg.color})}>PTG:</span><span style={{fontSize:12.5,color:"#ccc",lineHeight:1.5,flex:1}}>{upd.ptg}</span></div>}
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

function KanbanView(p){
  const [dragging,setDragging]=useState(null);
  const [dragOver,setDragOver]=useState(null);
  const blkTasks=p.tasks.filter(t=>t.status==="blocked");
  function onDrop(e,status){
    if(!dragging)return;
    const patch={status};
    if(status==="blocked")patch.blockedSince=todayISO();
    if(status==="complete"){patch.done=true;const found=p.tasks.find(t=>t.id===dragging);patch.actualEnd=found?.actualEnd||todayISO();}
    else patch.done=false;
    p.updateTask(dragging,patch);setDragging(null);setDragOver(null);
  }
  return (
    <div>
      <div style={C.ph}><div><h1 style={C.h1}>Kanban Board</h1><p style={C.subh}>Drag between lanes | {blkTasks.length} blocked</p></div></div>
      {blkTasks.length>0&&<div style={C.blkBar}><span style={{color:"#FF6B6B",fontWeight:700,fontSize:13}}>X Blocked:</span>{blkTasks.map(t=>{const imp=p.getImpact(t);if(!imp)return null;return <span key={t.id} style={sx(C.blkChip,imp.alreadyImpacting?C.blkChipRed:C.blkChipAmb)}>{t.text} - {imp.alreadyImpacting?"ON CP":imp.daysUntilImpact+"d"}</span>;})}</div>}
      <div style={C.board}>
        {STATUSES.map(status=>{
          const cfg=SCFG[status],col=p.tasks.filter(t=>(t.status||"not_started")===status);
          return (
            <div key={status} style={sx(C.col,dragOver===status?C.colOver:{},status==="blocked"?C.colBlk:{})} onDragOver={e=>{e.preventDefault();setDragOver(status);}} onDrop={e=>onDrop(e,status)} onDragLeave={()=>setDragOver(null)}>
              <div style={sx(C.colHd,{borderBottomColor:cfg.color+"44"})}><span style={{color:cfg.color,fontWeight:700,fontSize:12}}>{{not_started:"-",in_progress:">",blocked:"X",complete:"v"}[status]}</span><span style={{color:cfg.color,fontWeight:700,fontSize:12,flex:1}}>{cfg.label}</span><span style={sx(C.colCt,{background:cfg.bg,color:cfg.color})}>{col.length}</span></div>
              <div style={C.colCards}>
                {col.map(task=>{
                  const isCrit=!!p.cpm.critIds[task.id],imp=p.getImpact(task),own=p.getMem(task.ownerId),slack=p.cpm.slack[task.id];
                  return (
                    <div key={task.id} draggable onDragStart={()=>setDragging(task.id)} onDragEnd={()=>{setDragging(null);setDragOver(null);}} onClick={()=>p.setExpanded(p.expanded===task.id?null:task.id)} style={sx(C.kCard,isCrit?C.kCrit:{},task.status==="blocked"?C.kBlk:{},{opacity:dragging===task.id?0.4:1})}>
                      {imp&&<div style={sx(C.kImp,imp.alreadyImpacting?C.kImpRed:C.kImpAmb)}>{imp.alreadyImpacting?"!! On CP":"Impact in "+imp.daysUntilImpact+"d"}</div>}
                      <div style={{display:"flex",alignItems:"flex-start",justifyContent:"space-between",gap:6}}><span style={{fontSize:13,color:"#ccc",flex:1,lineHeight:1.4}}>{task.text}</span>{isCrit&&<span style={{fontSize:10,color:"#FF6B6B"}}>&#9670;</span>}</div>
                      <div style={{display:"flex",gap:6,alignItems:"center",flexWrap:"wrap",marginTop:4}}><span style={sx(C.dot2,{background:PRI_COLOR[task.priority]})}/>{slack!=null&&!isCrit&&<span style={C.slkMini}>+{slack}d</span>}{task.plannedEnd&&<span style={{fontSize:10,color:"#444"}}>{fmtD(task.plannedEnd)}</span>}</div>
                      {task.subtasks?.length>0&&<div style={{display:"flex",alignItems:"center",gap:7,marginTop:5}}><div style={{flex:1,height:3,background:"#252530",borderRadius:99}}><div style={{height:"100%",background:"#4D96FF",borderRadius:99,width:(task.subtasks.filter(s=>s.done).length/task.subtasks.length*100)+"%"}}/></div><span style={{fontSize:10,color:"#555"}}>{task.subtasks.filter(s=>s.done).length}/{task.subtasks.length}</span></div>}
                      {task.blockedReason&&<div style={{fontSize:11,color:"#FF6B6B66",fontStyle:"italic",marginTop:4}}>{task.blockedReason}</div>}
                      {own&&<div style={{display:"flex",alignItems:"center",gap:5,marginTop:4}}><div style={sx(C.av,{background:avBg(own.id),width:18,height:18,fontSize:8})}>{inits(own)}</div><span style={{fontSize:11,color:"#555"}}>{own.firstName}</span></div>}
                    </div>
                  );
                })}
                {col.length===0&&<div style={{textAlign:"center",padding:"20px 0",fontSize:12,color:"#2a2a35",fontStyle:"italic"}}>Drop here</div>}
              </div>
            </div>
          );
        })}
      </div>
      {p.expanded&&(()=>{const t=p.tasks.find(x=>x.id===p.expanded);return t?<div style={{marginTop:24}}><TaskCard task={t} idx={0} {...p}/></div>:null;})()}
    </div>
  );
}

function OwnerView(p){
  const unassigned=p.tasks.filter(t=>!t.ownerId);
  const groups=[...p.members.map(m=>({member:m,tasks:p.tasks.filter(t=>t.ownerId===m.id)})),...(unassigned.length?[{member:null,tasks:unassigned}]:[])].filter(g=>g.tasks.length>0);
  return (
    <div>
      <div style={C.ph}><h1 style={C.h1}>By Owner</h1><p style={C.subh}>Workload per team member</p></div>
      {groups.map(g=>{
        const m=g.member,done=g.tasks.filter(t=>t.status==="complete").length,blk=g.tasks.filter(t=>t.status==="blocked").length,act=g.tasks.filter(t=>t.status==="in_progress").length;
        const totalSubs=g.tasks.reduce((a,t)=>a+(t.subtasks?.length||0),0),doneSubs=g.tasks.reduce((a,t)=>a+(t.subtasks?.filter(s=>s.done).length||0),0);
        return (
          <div key={m?m.id:"unassigned"} style={C.oGrp}>
            <div style={C.oGrpHd}>
              <div style={sx(C.av,{background:m?avBg(m.id):"#333",width:36,height:36,fontSize:14})}>{m?inits(m):"?"}</div>
              <div style={{flex:1}}><div style={{fontSize:15,fontWeight:600,color:"#ddd",fontFamily:"'Syne',sans-serif"}}>{m?m.firstName+" "+m.lastName:"Unassigned"}</div>{m&&<div style={{fontSize:11.5,color:"#444"}}>{m.email}</div>}</div>
              <div style={{display:"flex",gap:14}}>{[["#4D96FF",g.tasks.length,"tasks"],["#FFD93D",act,"active"],blk>0?["#FF6B6B",blk,"blocked"]:null,["#6BCB77",done,"done"],totalSubs>0?["#C77DFF",doneSubs+"/"+totalSubs,"subs"]:null].filter(Boolean).map(item=><div key={item[2]} style={{display:"flex",flexDirection:"column",alignItems:"center"}}><span style={{color:item[0],fontWeight:700}}>{item[1]}</span><span style={{fontSize:10,color:"#444"}}>{item[2]}</span></div>)}</div>
              <div style={{width:80}}><div style={C.track}><div style={sx(C.fill,{width:g.tasks.length?(done/g.tasks.length*100)+"%":"0%"})}/></div></div>
            </div>
            <div style={{padding:"0 18px 12px"}}>
              {g.tasks.map(task=>{
                const imp=p.getImpact(task),isCrit=!!p.cpm.critIds[task.id],cfg=SCFG[task.status||"not_started"];
                return (
                  <div key={task.id} style={sx(C.oRow,task.status==="blocked"?C.oRowBlk:{},isCrit?{borderLeft:"3px solid #FF6B6B44",paddingLeft:10}:{})}>
                    <span style={sx(C.stPill,{background:cfg.bg,borderColor:cfg.border,color:cfg.color,cursor:"default",width:20,height:20,fontSize:11})}>{{not_started:"-",in_progress:">",blocked:"X",complete:"v"}[task.status||"not_started"]}</span>
                    <span style={sx({flex:1,fontSize:13.5,color:"#ccc"},task.status==="complete"?{textDecoration:"line-through",color:"#555"}:{})}>{task.text}</span>
                    <div style={{display:"flex",gap:5,alignItems:"center"}}>{isCrit&&<span style={C.bCrit}>&#9670;</span>}{task.status==="blocked"&&imp&&<span style={sx(C.bPush,imp.alreadyImpacting?{background:"#FF6B6B22",color:"#FF6B6B",borderColor:"#FF6B6B55"}:{})}>{imp.alreadyImpacting?"CP risk":imp.daysUntilImpact+"d"}</span>}{task.plannedEnd&&<span style={C.dateTag}>{fmtD(task.plannedEnd)}</span>}</div>
                    {task.subtasks?.length>0&&<div style={{width:"100%",paddingLeft:36,marginTop:4}}>{task.subtasks.map(st=>{const scfg=SCFG[st.status||"not_started"];return <div key={st.id} style={{display:"flex",alignItems:"center",gap:8,padding:"3px 0"}}><span style={{fontSize:10,color:scfg.color}}>{{complete:"v",blocked:"X",not_started:"-",in_progress:">"}[st.status||"not_started"]}</span><span style={sx({flex:1,fontSize:11.5,color:"#999"},st.done?{textDecoration:"line-through"}:{},st.status==="blocked"?{color:"#FF6B6B"}:{})}>{st.text}</span>{st.plannedEnd&&<span style={{fontSize:10,color:"#444"}}>{fmtD(st.plannedEnd)}</span>}</div>;})}</div>}
                  </div>
                );
              })}
            </div>
          </div>
        );
      })}
      {groups.length===0&&<div style={C.empty}>No tasks yet</div>}
    </div>
  );
}

function GanttView(p){
  const allDates=[...p.tasks.flatMap(t=>[t.plannedStart,t.plannedEnd,t.actualStart,t.actualEnd]),...p.milestones.map(m=>m.targetDate)].filter(Boolean).sort();
  if(!allDates.length)return <div style={C.empty}>Add tasks with planned dates to see the timeline.</div>;
  const minD=allDates[0],maxD=allDates[allDates.length-1];
  const total=Math.max(1,diffDays(minD,maxD))+4;
  const pct=d=>d?Math.max(0,diffDays(minD,d)/total*100):0;
  const wid=(a,b)=>(a&&b)?Math.max(0.5,(diffDays(a,b)+1)/total*100):0;
  const weeks=[];let cur=new Date(minD+"T00:00:00");const endD=new Date(maxD+"T00:00:00");endD.setDate(endD.getDate()+4);
  while(cur<=endD){weeks.push(toISO(cur));cur.setDate(cur.getDate()+7);}
  return (
    <div>
      <div style={C.ph}><div><h1 style={C.h1}>Timeline</h1><p style={C.subh}>Planned vs Actual | Milestones</p></div></div>
      <div style={{display:"flex",gap:16,marginBottom:16,flexWrap:"wrap"}}>{[["#4D96FF","Planned"],["#FF6B6B","Critical"],["#6BCB77","Actual"],["#FFD93D","Pushed"],["#C77DFF","Milestone"]].map(([c,l])=><div key={l} style={{display:"flex",alignItems:"center",gap:6,fontSize:12,color:"#666"}}><div style={{width:12,height:8,borderRadius:3,background:c}}/>{l}</div>)}</div>
      <div style={C.ganttWrap}>
        <div style={C.ganttHd}><div style={C.ganttLbl}/><div style={{flex:1,position:"relative",minWidth:400,height:28}}>{weeks.map(w=><div key={w} style={sx(C.wkLbl,{left:pct(w)+"%"})}>{new Date(w+"T00:00:00").toLocaleDateString("en-US",{month:"short",day:"numeric"})}</div>)}</div></div>
        {p.tasks.map(task=>{
          const isCrit=!!p.cpm.critIds[task.id],shift=p.dateShift(task.id),isBlk=task.status==="blocked",pColor=isCrit?"#FF6B6B":isBlk?"#FF6B6B88":"#4D96FF",hasActual=task.actualStart||task.actualEnd;
          return (
            <div key={task.id} style={C.ganttRow}>
              <div style={C.ganttLbl}><div style={{fontSize:12.5,color:"#ccc",overflow:"hidden",textOverflow:"ellipsis",whiteSpace:"nowrap"}}>{isCrit&&<span style={{color:"#FF6B6B",marginRight:3}}>&#9670;</span>}{isBlk&&<span style={{color:"#FF6B6B",marginRight:3}}>X</span>}{task.text}</div><div style={{fontSize:10.5,color:"#444"}}>{p.getMem(task.ownerId)?.firstName||""} - {SCFG[task.status||"not_started"].label}</div></div>
              <div style={{flex:1,position:"relative",minWidth:400}}>
                {task.plannedStart&&task.plannedEnd&&<div style={sx(C.gBar,{left:pct(task.plannedStart)+"%",width:wid(task.plannedStart,task.plannedEnd)+"%",background:pColor,opacity:isBlk?0.5:0.9})}/>}
                {hasActual&&<div style={sx(C.gBar,{top:22,left:pct(task.actualStart||task.plannedStart)+"%",width:wid(task.actualStart||task.plannedStart,task.actualEnd||task.plannedEnd)+"%",background:shift>0?"#FFD93D":shift<0?"#C77DFF":"#6BCB77",opacity:0.85})}/>}
                {shift!=null&&shift!==0&&<div style={sx(C.shiftLbl,{left:pct(task.plannedEnd)+"%",color:shift>0?"#FFD93D":"#C77DFF"})}>{shift>0?"+"+shift+"d":shift+"d"}</div>}
              </div>
            </div>
          );
        })}
        {p.milestones.map(ms=>{
          if(!ms.targetDate)return null;
          return (
            <div key={"ms-"+ms.id} style={sx(C.ganttRow,{background:"#100d18"})}>
              <div style={C.ganttLbl}><div style={{fontSize:12.5,color:"#C77DFF",overflow:"hidden",textOverflow:"ellipsis",whiteSpace:"nowrap"}}>&#9671; {ms.text}</div><div style={{fontSize:10.5,color:"#444"}}>Milestone - {fmtD(ms.targetDate)}</div></div>
              <div style={{flex:1,position:"relative",minWidth:400}}>
                <div style={{position:"absolute",left:pct(ms.targetDate)+"%",top:6,transform:"translateX(-50%)",width:0,height:0,borderLeft:"8px solid transparent",borderRight:"8px solid transparent",borderTop:"14px solid #C77DFF"}}/>
                {ms.actualDate&&<div style={{position:"absolute",left:pct(ms.actualDate)+"%",top:22,transform:"translateX(-50%)",width:0,height:0,borderLeft:"6px solid transparent",borderRight:"6px solid transparent",borderTop:"11px solid #6BCB77"}}/>}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

function CriticalView(p){
  const critP=Object.keys(p.cpm.critIds).map(id=>p.tasks.find(t=>t.id===parseInt(id))).filter(Boolean).sort((a,b)=>(a.plannedStart||"").localeCompare(b.plannedStart||""));
  const critA=Object.keys(p.acpm.critIds).map(id=>p.tasks.find(t=>t.id===parseInt(id))).filter(Boolean).sort((a,b)=>(a.actualStart||a.plannedStart||"").localeCompare(b.actualStart||b.plannedStart||""));
  const pdur=critP.length?diffDays(critP[0].plannedStart,critP[critP.length-1].plannedEnd):null;
  const adur=critA.length?diffDays(critA[0].actualStart||critA[0].plannedStart,critA[critA.length-1].actualEnd||critA[critA.length-1].plannedEnd):null;
  const delta=(pdur!=null&&adur!=null)?adur-pdur:null;
  const blkCt=p.tasks.filter(t=>t.status==="blocked").length;
  return (
    <div>
      <div style={C.ph}>
        <div><h1 style={C.h1}>Critical Path</h1><p style={C.subh}>CPM - Planned vs Actual</p></div>
        {delta!=null&&<div style={sx(C.deltaBox,{background:delta>0?"#FF6B6B22":delta<0?"#6BCB7722":"#4D96FF22",borderColor:delta>0?"#FF6B6B":delta<0?"#6BCB77":"#4D96FF"})}><div style={{fontFamily:"'Syne',sans-serif",fontWeight:800,fontSize:24,color:delta>0?"#FF6B6B":delta<0?"#6BCB77":"#4D96FF"}}>{delta>0?"+"+delta+"d":delta<0?delta+"d":"On Track"}</div><div style={{fontSize:11,color:"#666",marginTop:2}}>{delta>0?"Pushed":"Pulled in"}</div></div>}
      </div>
      <div style={C.statsRow}>{[["Milestones",p.milestones.length,"#C77DFF"],["Critical Tasks",Object.keys(p.cpm.critIds).length,"#FF6B6B"],["Planned End",p.cpm.projEnd?fmtD(p.cpm.projEnd):"--","#4D96FF"],["Actual End",p.acpm.projEnd?fmtD(p.acpm.projEnd):"--","#6BCB77"],["Blocked",blkCt,"#FF9A3C"]].map(item=><div key={item[0]} style={C.statBox}><div style={{fontFamily:"'Syne',sans-serif",fontWeight:800,fontSize:22,color:item[2]}}>{item[1]}</div><div style={{fontSize:11,color:"#555",marginTop:3}}>{item[0]}</div></div>)}</div>
      <div style={C.cpCols}>
        {[[critP,"Planned Critical Path","#FF6B6B",false],[critA,"Actual Critical Path","#6BCB77",true]].map(([crit,title,color,isActual])=>(
          <div key={title}>
            <div style={{fontSize:12,fontWeight:700,color,marginBottom:12}}>&#9670; {title}</div>
            {crit.length===0&&<div style={C.empty}>{isActual?"Enter actual dates.":"Add planned dates."}</div>}
            {crit.map((task,i)=>{
              const shift=p.dateShift(task.id),isBlk=task.status==="blocked";
              return (
                <div key={task.id}>
                  <div style={sx(C.cpCard,isBlk?{borderColor:"#FF6B6B44",background:"#FF6B6B08"}:{})}>
                    <div style={{display:"flex",alignItems:"center",gap:8,flexWrap:"wrap"}}><span style={{fontSize:10,fontWeight:700,background:color+"22",color,width:20,height:20,borderRadius:"50%",display:"flex",alignItems:"center",justifyContent:"center",flexShrink:0}}>{i+1}</span><span style={{fontSize:13.5,color:"#ddd",flex:1}}>{isBlk&&<span style={{color:"#FF6B6B",marginRight:4}}>X</span>}{task.text}</span>{shift!=null&&shift>0&&<span style={C.bPush}>+{shift}d</span>}{shift!=null&&shift<0&&<span style={C.bPull}>{shift}d</span>}</div>
                    <div style={{display:"flex",gap:8,flexWrap:"wrap",marginTop:6}}>{!isActual&&<span style={{fontSize:11.5,color:"#555"}}>{fmtD(task.plannedStart)} - {fmtD(task.plannedEnd)}</span>}{isActual&&task.actualStart&&<span style={{fontSize:11.5,color:"#6BCB77"}}>{fmtD(task.actualStart)} - {task.actualEnd?fmtD(task.actualEnd):"ongoing"}</span>}{p.getMem(task.ownerId)&&<span style={{fontSize:11.5,color:"#888",background:"#1a1a22",padding:"1px 8px",borderRadius:12}}>{p.getMem(task.ownerId).firstName} {p.getMem(task.ownerId).lastName}</span>}</div>
                    {isBlk&&task.blockedReason&&<div style={{fontSize:11.5,color:"#FF6B6B",fontStyle:"italic",marginTop:4}}>{task.blockedReason}</div>}
                  </div>
                  {i<crit.length-1&&<div style={{textAlign:"center",fontSize:16,color:"#2a2a38",lineHeight:"20px"}}>|</div>}
                </div>
              );
            })}
          </div>
        ))}
      </div>
      <div style={{marginTop:28}}>
        <div style={{fontSize:12,fontWeight:700,color:"#555",letterSpacing:1,textTransform:"uppercase",marginBottom:10}}>All Tasks - Slack and Float</div>
        <div style={C.table}>
          <div style={C.tHd}>{["Task","Status","Planned End","Slack","Variance","Impact"].map((h,i)=><div key={h} style={sx(C.th,i===0?{flex:3}:{})}>{h}</div>)}</div>
          {p.tasks.map(task=>{
            const isCrit=!!p.cpm.critIds[task.id],slack=p.cpm.slack[task.id],shift=p.dateShift(task.id),cfg=SCFG[task.status||"not_started"],imp=p.getImpact(task);
            return (
              <div key={task.id} style={sx(C.tRow,isCrit?{background:"#FF6B6B06",borderLeft:"2px solid #FF6B6B33"}:{},task.status==="blocked"?{background:"#FF6B6B08"}:{})}>
                <div style={sx(C.td,{flex:3})}>{isCrit&&<span style={{color:"#FF6B6B",marginRight:5}}>&#9670;</span>}{task.text}</div>
                <div style={C.td}><span style={{color:cfg.color,fontSize:11}}>{cfg.label}</span></div>
                <div style={C.td}>{fmtD(task.plannedEnd)}</div>
                <div style={C.td}>{slack!=null?<span style={{color:slack===0?"#FF6B6B":slack<=2?"#FF9A3C":"#6BCB77"}}>{slack===0?"Critical":"+"+slack+"d"}</span>:"--"}</div>
                <div style={C.td}>{shift!=null?<span style={{color:shift>0?"#FF6B6B":shift<0?"#6BCB77":"#888"}}>{shift>0?"+"+shift+"d":shift+"d"}</span>:"--"}</div>
                <div style={C.td}>{task.status==="blocked"&&imp?<span style={{color:imp.alreadyImpacting?"#FF6B6B":"#FFD93D",fontWeight:600}}>{imp.alreadyImpacting?"NOW":imp.daysUntilImpact+"d"}</span>:task.status==="complete"?<span style={{color:"#6BCB77"}}>Done</span>:task.actualStart?"Active":"--"}</div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}

function FF({label,value,onChange,placeholder,type="text"}){
  return <div style={C.ffGrp}><label style={{fontSize:11.5,color:"#666"}}>{label}</label><input style={C.ffIn} type={type} placeholder={placeholder} value={value} onChange={e=>onChange(e.target.value)}/></div>;
}

// ── Styles ────────────────────────────────────────────────
const C={
  root:{display:"flex",height:"100vh",background:"#0a0a0c",fontFamily:"'DM Sans',sans-serif",color:"#e0ddd6",overflow:"hidden"},
  sidebar:{width:260,background:"#0f0f12",borderRight:"1px solid #1a1a22",display:"flex",flexDirection:"column",padding:"24px 0",flexShrink:0,overflow:"hidden"},
  brand:{display:"flex",alignItems:"center",gap:8,padding:"0 20px 22px",borderBottom:"1px solid #1a1a22"},
  brandName:{fontFamily:"'Syne',sans-serif",fontWeight:800,fontSize:17,color:"#fff",letterSpacing:"-0.5px"},
  brandPro:{fontSize:9,fontWeight:700,background:"#4D96FF22",color:"#4D96FF",padding:"2px 6px",borderRadius:4,border:"1px solid #4D96FF44",letterSpacing:1},
  nav:{flex:1,padding:"16px 10px",display:"flex",flexDirection:"column",gap:2,overflowY:"auto"},
  sLabel:{fontSize:9,fontWeight:700,letterSpacing:2,color:"#444",textTransform:"uppercase",padding:"12px 10px 5px"},
  navBtn:{display:"flex",alignItems:"center",gap:8,padding:"8px 10px",borderRadius:7,border:"none",background:"transparent",color:"#777",cursor:"pointer",fontSize:13,textAlign:"left",width:"100%"},
  navBtnOn:{background:"#1a1a24",color:"#fff"},
  navIco:{fontSize:12,width:16,textAlign:"center",flexShrink:0},
  dot:{fontSize:8,flexShrink:0},
  navLbl:{flex:1,overflow:"hidden",textOverflow:"ellipsis",whiteSpace:"nowrap"},
  navCt:{fontSize:10,color:"#444"},
  blockedPip:{background:"#FF6B6B",color:"#fff",fontSize:9,fontWeight:700,padding:"1px 5px",borderRadius:99,animation:"pulse 1.5s ease infinite"},
  inlineRow:{display:"flex",gap:4,marginTop:2},
  inlineIn:{flex:1,padding:"6px 9px",background:"#161620",border:"1px solid #2a2a38",borderRadius:6,color:"#e0ddd6",fontSize:12.5},
  inlineBtn:{padding:"6px 10px",background:"#4D96FF",border:"none",borderRadius:6,color:"#fff",fontWeight:700,cursor:"pointer"},
  addDash:{padding:"7px 10px",background:"transparent",border:"1px dashed #252530",borderRadius:7,color:"#444",fontSize:12,cursor:"pointer",textAlign:"left",marginTop:2},
  memRow:{display:"flex",alignItems:"center",gap:8,padding:"5px 10px",borderRadius:7},
  av:{borderRadius:"50%",display:"flex",alignItems:"center",justifyContent:"center",fontWeight:700,color:"#fff",flexShrink:0},
  memName:{fontSize:12.5,color:"#bbb"},
  memEmail:{fontSize:10.5,color:"#444",overflow:"hidden",textOverflow:"ellipsis",whiteSpace:"nowrap",maxWidth:150},
  progBox:{margin:"0 14px 4px",padding:"12px 14px",background:"#141418",borderRadius:9,border:"1px solid #1a1a22"},
  progRow:{display:"flex",justifyContent:"space-between",fontSize:11,color:"#555",marginBottom:7},
  progFrac:{color:"#4D96FF",fontWeight:700},
  track:{height:4,background:"#252530",borderRadius:99,overflow:"hidden"},
  fill:{height:"100%",background:"linear-gradient(90deg,#4D96FF,#C77DFF)",borderRadius:99,transition:"width 0.4s ease"},
  blockedAlert:{marginTop:8,fontSize:10.5,color:"#FF6B6B",padding:"4px 8px",background:"#FF6B6B12",borderRadius:5,border:"1px solid #FF6B6B33",animation:"pulse 2s ease infinite"},
  undoBar:{display:"flex",alignItems:"center",gap:8,padding:"6px 14px 8px"},
  undoBtn:{flex:1,padding:"6px 10px",background:"transparent",border:"1px solid #1a1a22",borderRadius:7,color:"#333",fontSize:12,cursor:"pointer",fontFamily:"'DM Sans',sans-serif"},
  undoBtnOn:{color:"#4D96FF",borderColor:"#4D96FF44",background:"#4D96FF0a"},
  savedDot:{fontSize:11,color:"#6BCB77",transition:"opacity 0.5s",whiteSpace:"nowrap"},
  dataPath:{fontSize:9,color:"#2a2a35",padding:"2px 14px 10px",overflow:"hidden",textOverflow:"ellipsis",whiteSpace:"nowrap"},
  main:{flex:1,padding:"36px 44px",overflowY:"auto"},
  ph:{display:"flex",justifyContent:"space-between",alignItems:"flex-start",marginBottom:24,flexWrap:"wrap",gap:12},
  h1:{fontFamily:"'Syne',sans-serif",fontWeight:800,fontSize:28,color:"#fff",letterSpacing:"-0.5px"},
  subh:{marginTop:3,fontSize:12,color:"#444"},
  filters:{display:"flex",gap:5},
  fBtn:{padding:"5px 13px",borderRadius:18,border:"1px solid #252530",background:"transparent",color:"#555",fontSize:12,cursor:"pointer"},
  fOn:{background:"#1a1a24",borderColor:"#333344",color:"#ccc"},
  addBox:{background:"#0f0f12",border:"1px solid #1a1a22",borderRadius:11,padding:"13px 14px",marginBottom:18,display:"flex",flexDirection:"column",gap:9},
  addRow:{display:"flex",gap:7,flexWrap:"wrap"},
  addIn:{flex:1,minWidth:180,padding:"10px 13px",background:"#0a0a0c",border:"1px solid #1a1a22",borderRadius:7,color:"#e0ddd6",fontSize:13.5},
  addBtn:{padding:"10px 20px",background:"#4D96FF",border:"none",borderRadius:7,color:"#fff",fontWeight:600,fontSize:13,cursor:"pointer",fontFamily:"'Syne',sans-serif",whiteSpace:"nowrap",flexShrink:0},
  addMeta:{display:"flex",gap:7,alignItems:"center",flexWrap:"wrap"},
  sel:{padding:"7px 9px",background:"#0a0a0c",border:"1px solid #1a1a22",borderRadius:7,color:"#999",fontSize:12.5,cursor:"pointer"},
  metaLbl:{fontSize:11.5,color:"#444"},
  dateIn:{padding:"7px 9px",background:"#0a0a0c",border:"1px solid #1a1a22",borderRadius:7,color:"#999",fontSize:12.5},
  tList:{display:"flex",flexDirection:"column",gap:5},
  card:{background:"#0f0f12",border:"1px solid #1a1a22",borderRadius:11,overflow:"hidden",animation:"slideIn 0.25s ease both",position:"relative"},
  cardCrit:{borderColor:"#FF6B6B33"},
  cardBlocked:{borderColor:"#FF6B6B55",background:"#FF6B6B04"},
  critStripe:{position:"absolute",left:0,top:0,bottom:0,width:3,background:"#FF6B6B",borderRadius:"11px 0 0 11px"},
  blockedStripe:{position:"absolute",left:0,top:0,bottom:0,width:3,background:"repeating-linear-gradient(45deg,#FF6B6B,#FF6B6B 4px,transparent 4px,transparent 8px)"},
  impactBar:{display:"flex",alignItems:"center",gap:8,padding:"7px 14px 7px 16px",fontSize:12,borderBottom:"1px solid #1a1a1a"},
  impactRed:{background:"#FF6B6B14",color:"#FF6B6B",animation:"pulse 1.5s ease infinite"},
  impactAmber:{background:"#FFD93D0a",color:"#FFD93D"},
  cardMain:{display:"flex",alignItems:"center",gap:11,padding:"12px 14px 12px 16px"},
  stPill:{width:24,height:24,borderRadius:6,border:"1px solid",cursor:"pointer",display:"flex",alignItems:"center",justifyContent:"center",fontSize:12,fontWeight:700,flexShrink:0},
  cardBody:{flex:1,minWidth:0},
  cardTopRow:{display:"flex",alignItems:"center",gap:8,marginBottom:4,flexWrap:"wrap"},
  cardTxt:{fontSize:14,color:"#ddd"},
  badges:{display:"flex",gap:5,flexWrap:"wrap",marginLeft:"auto"},
  bCrit:{fontSize:10,padding:"1px 7px",borderRadius:12,background:"#FF6B6B22",color:"#FF6B6B",border:"1px solid #FF6B6B44",fontWeight:600},
  bSlack:{fontSize:10,padding:"1px 7px",borderRadius:12,background:"#6BCB7722",color:"#6BCB77",border:"1px solid #6BCB7744"},
  bPush:{fontSize:10,padding:"1px 7px",borderRadius:12,background:"#FFD93D22",color:"#FFD93D",border:"1px solid #FFD93D44",fontWeight:600},
  bPull:{fontSize:10,padding:"1px 7px",borderRadius:12,background:"#C77DFF22",color:"#C77DFF",border:"1px solid #C77DFF44",fontWeight:600},
  cardMetaRow:{display:"flex",gap:5,alignItems:"center",flexWrap:"wrap"},
  projTag:{fontSize:10.5,padding:"1px 7px",borderRadius:18,fontWeight:500},
  dot2:{width:8,height:8,borderRadius:"50%",flexShrink:0},
  stTag:{fontSize:10,padding:"1px 7px",borderRadius:12,border:"1px solid"},
  dateTag:{fontSize:10.5,color:"#555"},
  subCt:{fontSize:10.5,color:"#4D96FF"},
  ownerChip:{display:"flex",alignItems:"center",gap:6,padding:"3px 9px",background:"#161620",borderRadius:18,flexShrink:0,maxWidth:180},
  ownerNm:{fontSize:11.5,color:"#bbb",whiteSpace:"nowrap",overflow:"hidden",textOverflow:"ellipsis"},
  ownerEm:{fontSize:10,color:"#444",whiteSpace:"nowrap",overflow:"hidden",textOverflow:"ellipsis"},
  expBtn:{background:"transparent",border:"none",color:"#3a3a4a",fontSize:12,cursor:"pointer",padding:"4px 5px",flexShrink:0},
  delBtn:{background:"transparent",border:"none",color:"#3a3a4a",fontSize:12,cursor:"pointer",padding:"4px 5px",flexShrink:0},
  expPanel:{padding:"14px 16px",borderTop:"1px solid #161622",display:"flex",flexDirection:"column",gap:16},
  expGrid:{display:"flex",gap:14,flexWrap:"wrap"},
  expSec:{display:"flex",flexDirection:"column",gap:8},
  expTtl:{fontSize:11.5,fontWeight:600,color:"#666",letterSpacing:0.3,marginBottom:2},
  expRow:{display:"flex",alignItems:"center",gap:8},
  expLbl:{fontSize:11.5,color:"#555",width:36,flexShrink:0},
  expIn:{padding:"6px 9px",background:"#0a0a0c",border:"1px solid #252530",borderRadius:6,color:"#aaa",fontSize:12.5},
  expSel:{padding:"7px 9px",background:"#0a0a0c",border:"1px solid #252530",borderRadius:6,color:"#aaa",fontSize:12.5,cursor:"pointer",width:"100%"},
  depGrid:{display:"flex",flexWrap:"wrap",gap:6},
  depOpt:{display:"flex",alignItems:"center",gap:6,padding:"5px 10px",borderRadius:7,border:"1px solid #252530",cursor:"pointer",fontSize:12.5,color:"#666",background:"transparent"},
  depOn:{borderColor:"#4D96FF66",background:"#4D96FF11",color:"#ccc"},
  depBox:{width:14,height:14,borderRadius:3,border:"1px solid #3a3a4a",display:"flex",alignItems:"center",justifyContent:"center",fontSize:9,color:"#4D96FF",flexShrink:0},
  subRow:{display:"flex",alignItems:"center",gap:8,padding:"5px 0",borderBottom:"1px solid #141418"},
  stChk:{width:16,height:16,borderRadius:4,border:"1px solid #3a3a4a",cursor:"pointer",flexShrink:0,display:"flex",alignItems:"center",justifyContent:"center",fontSize:9},
  stSel:{padding:"3px 7px",background:"#0a0a0c",border:"1px solid #1a1a22",borderRadius:5,color:"#777",fontSize:11},
  stDate:{padding:"4px 7px",background:"#0a0a0c",border:"1px solid #1a1a22",borderRadius:5,color:"#777",fontSize:11,width:110},
  stDel:{background:"transparent",border:"none",color:"#333",fontSize:11,cursor:"pointer"},
  stAddRow:{display:"flex",gap:6,marginTop:6},
  stIn:{flex:1,padding:"7px 10px",background:"#0a0a0c",border:"1px dashed #252530",borderRadius:6,color:"#bbb",fontSize:12.5},
  stAddBtn:{padding:"7px 12px",background:"#1a1a24",border:"1px solid #252530",borderRadius:6,color:"#888",fontSize:15,cursor:"pointer"},
  notes:{padding:"9px 11px",background:"#0a0a0c",border:"1px solid #1a1a22",borderRadius:7,color:"#aaa",fontSize:12.5,resize:"vertical",lineHeight:1.6,width:"100%"},
  empty:{textAlign:"center",color:"#333",fontSize:13.5,padding:"48px 0",fontStyle:"italic"},
  msBadge:{fontSize:14,width:28,height:28,borderRadius:8,border:"1px solid",display:"flex",alignItems:"center",justifyContent:"center",flexShrink:0},
  msProgWrap:{display:"flex",flexDirection:"column",alignItems:"center",width:60,gap:2},
  rStatusBadge:{fontSize:10.5,fontWeight:600,padding:"3px 10px",borderRadius:12,border:"1px solid",whiteSpace:"nowrap",flexShrink:0},
  ptgBox:{display:"flex",gap:8,padding:"9px 12px",borderRadius:8,border:"1px solid",alignItems:"flex-start"},
  ptgLabel:{fontSize:11,fontWeight:700,flexShrink:0,marginTop:1,letterSpacing:0.5},
  blkBar:{background:"#FF6B6B0a",border:"1px solid #FF6B6B33",borderRadius:10,padding:"12px 16px",marginBottom:20,display:"flex",alignItems:"center",gap:10,flexWrap:"wrap"},
  blkChip:{fontSize:11,padding:"3px 10px",borderRadius:20,border:"1px solid",fontWeight:500},
  blkChipRed:{background:"#FF6B6B22",borderColor:"#FF6B6B55",color:"#FF6B6B"},
  blkChipAmb:{background:"#FFD93D0a",borderColor:"#FFD93D33",color:"#FFD93D"},
  board:{display:"grid",gridTemplateColumns:"repeat(4,1fr)",gap:12,alignItems:"start"},
  col:{background:"#0c0c0f",border:"1px solid #1a1a22",borderRadius:12,overflow:"hidden"},
  colOver:{background:"#141420",borderColor:"#4D96FF44"},
  colBlk:{background:"#0f0a0a",borderColor:"#FF6B6B22"},
  colHd:{padding:"12px 14px 10px",display:"flex",alignItems:"center",gap:7,borderBottom:"2px solid"},
  colCt:{fontSize:10,fontWeight:700,padding:"1px 6px",borderRadius:99},
  colCards:{padding:"10px",display:"flex",flexDirection:"column",gap:8,minHeight:80},
  kCard:{background:"#131318",border:"1px solid #1e1e26",borderRadius:9,padding:"11px 12px",cursor:"grab",display:"flex",flexDirection:"column",gap:6},
  kCrit:{borderColor:"#FF6B6B44",boxShadow:"0 0 0 1px #FF6B6B22"},
  kBlk:{borderColor:"#FF6B6B55",background:"#FF6B6B06"},
  kImp:{fontSize:10.5,fontWeight:600,padding:"4px 8px",borderRadius:6,border:"1px solid"},
  kImpRed:{background:"#FF6B6B18",borderColor:"#FF6B6B44",color:"#FF6B6B",animation:"pulse 1.5s ease infinite"},
  kImpAmb:{background:"#FFD93D0a",borderColor:"#FFD93D33",color:"#FFD93D"},
  slkMini:{fontSize:10,color:"#6BCB77",background:"#6BCB7714",padding:"1px 5px",borderRadius:10},
  oGrp:{background:"#0f0f12",border:"1px solid #1a1a22",borderRadius:12,marginBottom:14,overflow:"hidden"},
  oGrpHd:{display:"flex",alignItems:"center",gap:12,padding:"16px 18px",borderBottom:"1px solid #151520"},
  oRow:{display:"flex",alignItems:"flex-start",gap:10,padding:"9px 0",borderBottom:"1px solid #111116",flexWrap:"wrap"},
  oRowBlk:{background:"#FF6B6B06"},
  statsRow:{display:"flex",gap:10,marginBottom:24,flexWrap:"wrap"},
  statBox:{flex:1,minWidth:110,background:"#0f0f12",border:"1px solid #1a1a22",borderRadius:10,padding:"14px 16px"},
  cpCols:{display:"grid",gridTemplateColumns:"1fr 1fr",gap:20,marginBottom:32},
  cpCard:{background:"#0f0f12",border:"1px solid #1a1a22",borderRadius:10,padding:"12px 14px"},
  deltaBox:{padding:"12px 18px",borderRadius:10,border:"1px solid",textAlign:"center"},
  table:{background:"#0f0f12",border:"1px solid #1a1a22",borderRadius:11,overflow:"hidden"},
  tHd:{display:"flex",padding:"10px 14px",borderBottom:"1px solid #1a1a22",background:"#0d0d10"},
  th:{flex:1,fontSize:10.5,fontWeight:600,color:"#555",letterSpacing:0.5,textTransform:"uppercase"},
  tRow:{display:"flex",padding:"10px 14px",borderBottom:"1px solid #111116",alignItems:"center"},
  td:{flex:1,color:"#999",fontSize:12.5},
  ganttWrap:{background:"#0f0f12",borderRadius:12,border:"1px solid #1a1a22",overflow:"auto"},
  ganttHd:{display:"flex",borderBottom:"1px solid #1a1a22",position:"sticky",top:0,background:"#0f0f12",zIndex:2},
  ganttLbl:{width:200,minWidth:200,padding:"10px 14px",borderRight:"1px solid #1a1a22",display:"flex",flexDirection:"column",justifyContent:"center",flexShrink:0},
  ganttRow:{display:"flex",borderBottom:"1px solid #111116",minHeight:52},
  wkLbl:{position:"absolute",top:8,fontSize:10,color:"#333",whiteSpace:"nowrap",transform:"translateX(-50%)"},
  gBar:{position:"absolute",top:8,height:14,borderRadius:3,minWidth:3},
  shiftLbl:{position:"absolute",top:2,fontSize:9.5,whiteSpace:"nowrap",fontWeight:600},
  overlay:{position:"fixed",inset:0,background:"rgba(0,0,0,0.75)",display:"flex",alignItems:"center",justifyContent:"center",zIndex:100},
  modal:{background:"#0f0f12",border:"1px solid #252530",borderRadius:14,width:420,overflow:"hidden"},
  modalHd:{display:"flex",justifyContent:"space-between",alignItems:"center",padding:"16px 22px",borderBottom:"1px solid #1a1a22"},
  modalTtl:{fontFamily:"'Syne',sans-serif",fontWeight:700,fontSize:15,color:"#fff"},
  modalX:{background:"transparent",border:"none",color:"#444",fontSize:15,cursor:"pointer"},
  modalBd:{padding:"18px 22px",display:"flex",flexDirection:"column",gap:13},
  fieldRow:{display:"flex",gap:11},
  ffGrp:{flex:1,display:"flex",flexDirection:"column",gap:5},
  ffIn:{padding:"9px 11px",background:"#0a0a0c",border:"1px solid #252530",borderRadius:7,color:"#e0ddd6",fontSize:13.5},
  errMsg:{fontSize:12,color:"#FF6B6B",padding:"7px 11px",background:"#FF6B6B12",borderRadius:7,border:"1px solid #FF6B6B33"},
  modalPrim:{padding:"10px",background:"#4D96FF",border:"none",borderRadius:7,color:"#fff",fontWeight:600,fontSize:13.5,cursor:"pointer"},
};

ReactDOM.createRoot(document.getElementById("root")).render(<App/>);
</script>
</body>
</html>
"""

# ── Launch ──────────────────────────────────────────────────
if __name__ == "__main__":
    api = FocusboardAPI()
    window = webview.create_window(
        "Focusboard PRO",
        html=HTML,
        js_api=api,
        width=1400,
        height=900,
        min_size=(900, 600),
        background_color="#0a0a0c",
    )
    webview.start(debug=False)
