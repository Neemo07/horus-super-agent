const $=s=>document.querySelector(s);
const names={'pending':'Pending','done':'Done','in-progress':'In progress','review':'Review','deferred':'Deferred','cancelled':'Cancelled','blocked':'Blocked','unknown':'Unknown','ready':'Available','stale':'Stale data','unavailable':'Unavailable'};
const tone=s=>['done','ready'].includes(s)?'good': ['blocked','stale','unavailable'].includes(s)?'warn':s==='review'?'review':'';
const element=(kind,value,cls)=>{const n=document.createElement(kind);if(value!==undefined)n.textContent=value;if(cls)n.className=cls;return n;};
const chip=s=>element('span',names[s]??'Unknown','chip '+tone(s));
const time=t=>t?new Date(t).toLocaleTimeString([],{hour:'2-digit',minute:'2-digit',second:'2-digit'}):'Unavailable';
let last='', current={projects:[],activity:[]}, selected=null, theme='dark';
const trigger=$('#theme');
const detail=$('#detail');
const projectDialog=$('#project-dialog');
const projectForm=$('#project-form');
const projectSubmit=projectForm.querySelector('button[type="submit"]');
const projectCancel=$('#cancel-project');
const projectError=$('#project-error');
$('#add-project').addEventListener('click',()=>{
 projectError.textContent='';
 projectDialog.showModal();
});
projectCancel.addEventListener('click',()=>projectDialog.close());
projectDialog.addEventListener('cancel',event=>{
 if(projectSubmit.disabled)event.preventDefault();
});
projectForm.addEventListener('submit',async event=>{
 event.preventDefault();
 if(projectSubmit.disabled)return;
 const project=Object.fromEntries(new FormData(projectForm));
 project.tag=project.tag.trim();
 projectError.textContent='';
 projectSubmit.disabled=projectCancel.disabled=true;
 projectSubmit.textContent='Adding…';
 try{
  const response=await fetch('/api/projects',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(project)});
  const result=await response.json();
  if(!response.ok){projectError.textContent=result.error;return;}
  projectDialog.close();
  projectForm.reset();
  $('#find').value=$('#filter').value='';
  $('#group').value='project';
  $('#project-status').textContent=project.name.trim()+' added.';
 }catch{projectError.textContent='Could not reach the dashboard. Try again.';}
 finally{
  projectSubmit.disabled=projectCancel.disabled=false;
  projectSubmit.textContent='Add project';
 }
});
detail.addEventListener('close',()=>{
 const ref=selected&&selected.p+'/'+selected.t;
 const row=Array.from($('#portfolio').querySelectorAll('button[data-ref]')).find(button=>button.dataset.ref===ref);
 (row??$('#find')).focus({preventScroll:true});
 selected=null;
});
try{theme=localStorage.getItem('tmpm-theme')==='light'?'light':'dark';}catch{}
const applyTheme=()=>{document.documentElement.classList.toggle('light',theme==='light');trigger.textContent=theme==='light'?'Mission Control':'Day Shift';trigger.setAttribute('aria-pressed',String(theme==='light'));};
applyTheme();trigger.addEventListener('click',()=>{theme=theme==='light'?'dark':'light';applyTheme();try{localStorage.setItem('tmpm-theme',theme);}catch{}});
for(const selector of ['#find','#filter','#group'])$(selector).addEventListener(selector==='#find'?'input':'change',render);
const progressOrder=['in-progress','review','blocked','pending','done','deferred','cancelled','unknown'];
function taskRow(project,task,showProject=false){
 const li=element('li'), button=element('button',undefined,'task-row'), content=element('span');
 button.type='button';button.dataset.ref=project.id+'/'+task.id;
 const subtaskCount=task.subtasks.length;
 const metadata=[subtaskCount+' '+(subtaskCount===1?'subtask':'subtasks')];
 if(showProject)metadata.unshift(project.name);
 if(task.blockers.length)metadata.push(task.blockers.length+' '+(task.blockers.length===1?'dependency':'dependencies')+' open');
 content.append(element('strong',task.id+' · '+task.title),element('small',metadata.join(' · ')));
 button.append(content);
 if(task.blockers.length)button.append(element('span','Dependencies open','chip warn'));
 button.append(chip(task.status));
 button.addEventListener('click',()=>{selected={p:project.id,t:task.id};showDetail();detail.showModal();});
 li.append(button);
 return li;
}
function render(){
 const p=current.projects, all=p.flatMap(x=>x.tasks), focused=document.activeElement?.dataset?.ref;
 const metrics=$('#metrics');metrics.replaceChildren();
 for(const [n,label] of [[p.length,'Configured projects'],[all.filter(t=>t.status==='in-progress').length,'In progress'],[all.filter(t=>t.status==='review').length,'Awaiting review'],[all.filter(t=>t.status==='blocked'||t.blockers?.length).length,'Blocked / dependencies open']]){
  const card=element('div',undefined,'metric');card.append(element('strong',n),element('span',label));metrics.append(card);
 }
 const term=$('#find').value.trim().toLowerCase(), filter=$('#filter').value;
 const box=$('#portfolio');box.replaceChildren();
 const byProgress=$('#group').value==='progress';
 const groups=new Map(progressOrder.map(status=>[status,[]]));
 let count=0;
 for(const pr of p){
   const matchProject=pr.name.toLowerCase().includes(term);
   const matches=pr.tasks.filter(t=>(!term||matchProject||[t.id,t.title,...t.subtasks.map(s=>s.title)].some(x=>x.toLowerCase().includes(term)))&&(!filter||(filter==='blockers'?(t.status==='blocked'||t.blockers.length):t.status===filter)));
   if((term||filter)&&!matches.length&&!(matchProject&&pr.state!=='ready'))continue;
   if(byProgress){
    for(const task of matches)groups.get(task.status).push(taskRow(pr,task,true));
    count+=matches.length;
    if(pr.state!=='ready')box.append(element('p',pr.name+' · '+names[pr.state],'source-warning warn'));
    continue;
   }
   count++;
   const card=element('article',undefined,'project'), head=element('div',undefined,'project-head');
   head.append(element('h3',pr.name),chip(pr.state));card.append(head);
   card.append(element('p',pr.tag+' · '+pr.tasks.length+' tasks · '+pr.tasks.filter(t=>t.status==='done').length+' done · '+(pr.observedAt?'Last change '+time(pr.observedAt):'No snapshot available'),'project-meta'));
   if(pr.state==='stale')card.append(element('p','Showing the last readable snapshot. Source is currently unavailable.','warn'));
   const list=element('ul',undefined,'task-list');
   for(const task of matches)list.append(taskRow(pr,task));
   if(!matches.length)card.append(element('p',pr.state==='ready'?'No tasks in this project.':'No readable backlog. Verify the local project configuration.','empty'));
   card.append(list);box.append(card);
 }
 if(byProgress)for(const [status,rows] of groups){
  if(!rows.length)continue;
  const group=element('article',undefined,'project'), head=element('div',undefined,'project-head');
  head.append(element('h3',names[status]),element('span',String(rows.length),'muted'));
  const list=element('ul',undefined,'task-list');
  list.append(...rows);group.append(head,list);box.append(group);
 }
 $('#shown').textContent=count+' '+(byProgress?(count===1?'task':'tasks'):(count===1?'project':'projects'))+' shown';
 if(!count)box.append(element('p',p.length?'No projects or tasks match.':'Add a local Task Master project to get started.','empty'));
 if(focused)for(const btn of box.querySelectorAll('button'))if(btn.dataset.ref===focused){btn.focus({preventScroll:true});break;}
 const a=$('#activity');a.replaceChildren();
 if(!current.activity.length)a.append(element('li','No changes observed since startup.','empty'));
 for(const row of current.activity.slice(0,16)){const li=element('li'), kind=row.subtaskId?'Subtask '+row.taskId+'.'+row.subtaskId:'Task '+row.taskId;
  li.append(element('strong',row.task),element('small',row.project+' · '+kind+' · '+time(row.at)),element('small',(row.from?names[row.from]+' → ':'Added · ')+names[row.to]+' · actor unknown'));a.append(li);}
 if($('#detail').open)showDetail();
}
function showDetail(){
 const p=current.projects.find(x=>x.id===selected?.p), t=p?.tasks.find(x=>x.id===selected?.t), box=$('#detail-body');box.replaceChildren();
 $('#detail-title').textContent=t?.title??'Task unavailable';
 $('#detail-meta').textContent=p&&t?p.name+' / '+t.id:'';
 if(!t)return;
 box.append(chip(t.status),element('p',t.dependencies.length?'Dependencies: '+t.dependencies.join(', '):'No task dependencies.'));
 if(t.blockers.length)box.append(element('p','Open or missing dependencies: '+t.blockers.join(', '),'warn'));
 if(p.state==='stale')box.append(element('p','This view is from the last readable snapshot.','warn'));
 box.append(element('p','Delivery evidence: not supplied by this backlog. Done does not establish UAT or acceptance.','muted'),element('h3','Subtasks'));
 const ul=element('ul',undefined,'subtasks');
 for(const s of t.subtasks){const li=element('li');li.append(element('span',s.id+' · '+s.title+(s.blockers.length?' · open: '+s.blockers.join(', '):'')),chip(s.status));ul.append(li);}
 box.append(ul);if(!t.subtasks.length)box.append(element('p','No subtasks.','empty'));
}
async function poll(){
 try{
   const res=await fetch('/api/portfolio',{cache:'no-store'});if(!res.ok)throw Error();
   const body=await res.text();
   if(body!==last){current=JSON.parse(body);last=body;render();}
   const el=$('#connection');const degraded=current.projects.some(x=>x.state!=='ready');
   el.textContent=degraded?'Local · Source warnings':'Local · Connected';el.className='chip '+(degraded?'warn':'good');
 }catch{const el=$('#connection');el.textContent='Offline · Last view';el.className='chip warn';}
 setTimeout(poll,1150);
}
poll();
