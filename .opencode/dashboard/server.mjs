import { createServer } from 'node:http';
import { randomUUID } from 'node:crypto';
import { mkdirSync, readFileSync, realpathSync, renameSync, rmdirSync, rmSync, writeFileSync } from 'node:fs';
import { homedir } from 'node:os';
import { dirname, join, resolve } from 'node:path';
import { pathToFileURL } from 'node:url';
import { normalizeProjects,createTracker,readProject } from './model.mjs';
const publicFiles=new Map([['/',['index.html','text/html']],['/app.mjs',['app.mjs','text/javascript']],['/styles.css',['styles.css','text/css']]]);
const headers={'Cache-Control':'no-store','X-Content-Type-Options':'nosniff','Referrer-Policy':'no-referrer','Cross-Origin-Resource-Policy':'same-origin','Content-Security-Policy':"default-src 'none'; img-src 'self'; style-src 'self'; script-src 'self'; connect-src 'self'; base-uri 'none'; frame-ancestors 'none'; form-action 'none'"};
export function stableReader(read=readProject){
 const previous=new Map();
 return project=>{
  const observed=read(project), state=previous.get(project.id);
  if(observed.state!=='ready'){previous.set(project.id,{...state,key:null});return observed;}
  const key=JSON.stringify(observed.tasks);
  if(!state||state.key===key){previous.set(project.id,{key,accepted:observed});return observed;}
  previous.set(project.id,{key,accepted:state.accepted});return state.accepted||observed;
 };
}
function loadProjects(config){
 try{return normalizeProjects(JSON.parse(readFileSync(config,'utf8').replace(/^\uFEFF/,'')));}
 catch(error){if(error.code==='ENOENT')return [];throw error;}
}
function saveProject(config,project){
 mkdirSync(dirname(config),{recursive:true});
 const lock=config+'.lock', temporary=join(lock,'portfolio.json');
 mkdirSync(lock);
 try{
  const projects=loadProjects(config);
  const comparable=root=>process.platform==='win32'?root.toLowerCase():root;
  const duplicate=projects.some(existing=>{
   let root=existing.root;
   try{root=realpathSync(root);}catch{}
   return comparable(root)===comparable(project.root)&&existing.tag===project.tag;
  });
  if(duplicate)return {error:'This folder and task tag are already in the portfolio.'};
  if(projects.length>=30)return {error:'The portfolio already has 30 projects.'};
  projects.push(project);
  writeFileSync(temporary,JSON.stringify({projects},null,2)+'\n',{mode:0o600});
  renameSync(temporary,config);
  return {projects};
 }finally{rmSync(temporary,{force:true});rmdirSync(lock);}
}
export function makeServer(initialProjects,{interval=750,config}={}){
 const projects=[...initialProjects];
 const tracker=createTracker(projects,stableReader()); let payload=JSON.stringify(tracker.sample());
 const timer=setInterval(()=>{payload=JSON.stringify(tracker.sample());},interval); timer.unref();
 const server=createServer(async(req,res)=>{
  const host='127.0.0.1:'+server.address()?.port;
  const reply=(code,body,type='text/plain')=>{res.writeHead(code,{...headers,'Content-Type':type+'; charset=utf-8'});res.end(req.method==='HEAD'?undefined:body);};
  if(req.headers.host!==host|| (req.headers.origin&&req.headers.origin!=='http://'+host) || (req.url==='/api/portfolio'&&['cross-site','same-site'].includes(req.headers['sec-fetch-site']))) return reply(403,'Forbidden');
  if(req.url==='/api/projects'&&req.method==='POST'){
   const json=(code,body)=>reply(code,JSON.stringify(body),'application/json');
   if(!config)return json(405,{error:'Project registration is disabled.'});
   if(req.headers.origin!=='http://'+host||['cross-site','same-site'].includes(req.headers['sec-fetch-site']))return json(403,{error:'Open the dashboard directly to add a project.'});
   if(req.headers['content-type']!=='application/json')return json(415,{error:'Expected JSON.'});
   const chunks=[];
   let bytes=0;
   try{
    for await(const chunk of req.iterator({destroyOnReturn:false})){
     bytes+=chunk.length;
     if(bytes>8192){req.resume();return json(413,{error:'Project details are too long.'});}
     chunks.push(chunk);
    }
   }catch{return;}
   let project;
   try{
    const {name,root,tag}=JSON.parse(Buffer.concat(chunks).toString('utf8'));
    [project]=normalizeProjects({projects:[{id:randomUUID(),name,root:typeof root==='string'?root.trim():root,tag:tag||undefined}]});
    project.root=realpathSync(project.root);
    [project]=normalizeProjects({projects:[project]});
   }catch{return json(400,{error:'Enter a name, an existing absolute local project folder, and a valid task tag.'});}
   if(readProject(project).state!=='ready')return json(400,{error:'Could not read tasks. Ensure the folder contains task_plan.md, .todo.md, or .taskmaster/tasks/tasks.json.'});
   let saved;
   try{saved=saveProject(config,project);}
   catch{return json(503,{error:'Could not save the local portfolio. Check that the configuration is writable and try again.'});}
   if(saved.error)return json(409,saved);
   const known=new Set(projects.map(existing=>existing.id));
   projects.push(...saved.projects.filter(existing=>!known.has(existing.id)));
   payload=JSON.stringify(tracker.sample());
   return json(201,{id:project.id});
  }
  if(!['GET','HEAD'].includes(req.method)) return reply(405,'Method not allowed');
  if(req.url==='/api/portfolio') return reply(200,payload,'application/json');
  const file=publicFiles.get(req.url);
  if(!file) return reply(404,'Not found');
  try{return reply(200,readFileSync(new URL(file[0],import.meta.url)),file[1]);}catch{return reply(503,'Dashboard asset unavailable');}
 });
 server.on('close',()=>clearInterval(timer));
 return server;
}
if(process.argv[1]&&import.meta.url===pathToFileURL(process.argv[1]).href){
 const {values}=await import('node:util').then(({parseArgs})=>parseArgs({options:{config:{type:'string'},port:{type:'string'}}}));
 const config=resolve(values.config??join(homedir(),'.horus-portfolio','portfolio.json'));
 if(/^[\\/]{2}/.test(config))throw Error('Use a local config file.');
 let projects;try{projects=loadProjects(config);}catch{throw Error('Cannot read configuration as local JSON.');}
 const port=Number(values.port||8917); if(!Number.isSafeInteger(port)||port<1024||port>65535)throw Error('Invalid local port.');
 const app=makeServer(projects,{config});app.listen(port,'127.0.0.1',()=>console.log('Horus Portfolio Dashboard: http://127.0.0.1:'+port));
}
