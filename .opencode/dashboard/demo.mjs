import {mkdtempSync,mkdirSync,writeFileSync,readFileSync,renameSync} from 'node:fs';
import {tmpdir} from 'node:os';
import {join} from 'node:path';
import {spawn} from 'node:child_process';
import {fileURLToPath} from 'node:url';
const base=mkdtempSync(join(tmpdir(),'TaskMasterProMax-demo-'));
const fixtures=[
 {id:'atlas',name:'Atlas Release',tasks:[
 {id:1,title:'Publish the API contract',status:'done',subtasks:[{id:1,title:'Verify example payloads',status:'done'}]},
 {id:2,title:'Confirm the rollout checklist',status:'review',dependencies:[1],subtasks:[{id:1,title:'Draft rollback notes',status:'done'},{id:2,title:'Review smoke test evidence',status:'review',dependencies:[1]}]},
 {id:3,title:'Promote staging build',status:'pending',dependencies:[2]}]},
 {id:'harbor',name:'Harbor Migration',tasks:[
 {id:1,title:'Map service ownership',status:'in-progress',subtasks:[{id:1,title:'Inventory handover exceptions',status:'in-progress'},{id:2,title:'Review escalation owners',status:'pending',dependencies:[1]}]},
 {id:2,title:'Rehearse contingency cutover',status:'pending',dependencies:[1]},
 {id:3,title:'Evaluate archive import',status:'deferred'}]},
 {id:'lumen',name:'Lumen Pilot',tasks:[
 {id:1,title:'Lock the pilot assumptions',status:'done'},{id:2,title:'Validate the operator workflow',status:'in-progress',subtasks:[{id:1,title:'Run first-pass timed walkthrough',status:'done'},{id:2,title:'Record operator notes',status:'pending'}]},
 {id:3,title:'Decide pilot exit criteria',status:'review',dependencies:[1]}]}
];
const destination=join(base,'atlas','.taskmaster','tasks','tasks.json');
for(const {id,tasks} of fixtures){const dir=join(base,id,'.taskmaster','tasks');mkdirSync(dir,{recursive:true});writeFileSync(join(dir,'tasks.json'),JSON.stringify({master:{tasks}},null,2));}
const config=join(base,'portfolio.json');
writeFileSync(config,JSON.stringify({projects:fixtures.map(({id,name})=>({id,name:name+' · Demo',root:join(base,id)}))}));
console.log('Synthetic sources created in:',base);
console.log('Run with --simulate to move an Atlas task and subtask to Done once, 24 seconds after startup.');
const child=spawn(process.execPath,[fileURLToPath(new URL('./server.mjs',import.meta.url)),'--config',config,'--port','8917'],{stdio:'inherit'});
const timer=process.argv.includes('--simulate')?setTimeout(()=>{
 const state=JSON.parse(readFileSync(destination,'utf8'));const t=state.master.tasks.find(t=>t.id===2);t.status='done';t.subtasks[1].status='done';const temporary=destination+'.next';writeFileSync(temporary,JSON.stringify(state,null,2));renameSync(temporary,destination);console.log('Synthetic Atlas task plus subtask moved to Done.');
},24000):null;
child.once('exit',code=>{if(timer)clearTimeout(timer);process.exitCode=code??0;});
for(const sig of ['SIGINT','SIGTERM'])process.on(sig,()=>{if(timer)clearTimeout(timer);child.kill();});
