import{useEffect,useState}from'react';import{Activity,Bot,ShieldCheck,ClipboardList,RefreshCw,PlusCircle}from'lucide-react';
const API=import.meta.env.VITE_API_URL||'http://localhost:8090';
type Data={projects:number;runs:any[];approvals:any[];agents:any[];integration:any};
export default function App(){
 const[data,setData]=useState<Data|null>(null),[projects,setProjects]=useState<any[]>([]),[audit,setAudit]=useState<any[]>([]);
 const[project,setProject]=useState(''),[name,setName]=useState('New Zynx project'),[task,setTask]=useState('');
 const[tab,setTab]=useState('Overview'),[error,setError]=useState(''),[token,setToken]=useState('');
 const headers=(json=false):Record<string,string>=>({...json?{'Content-Type':'application/json'}:{},...(token?{'X-Agent-Forge-Token':token}:{})});
 async function load(){try{
  const [o,p,a]=await Promise.all([fetch(API+'/api/overview',{headers:headers()}),fetch(API+'/api/projects',{headers:headers()}),fetch(API+'/api/audit',{headers:headers()})]);
  for(const r of [o,p,a])if(!r.ok)throw new Error(r.status===401?'API token required or invalid':'API unavailable');
  setData(await o.json());setProjects((await p.json()).projects);setAudit((await a.json()).events);setError('');
 }catch(e:any){setError(e.message)}}
 useEffect(()=>{load();const t=setInterval(load,5000);return()=>clearInterval(t)},[token]);
 async function createProject(){const r=await fetch(API+'/api/projects',{method:'POST',headers:headers(true),body:JSON.stringify({name,context:{}})});if(!r.ok){setError('Project creation failed');return}const p=await r.json();setProject(p.id);await load()}
 async function submit(){if(!project||!task.trim())return;const r=await fetch(API+'/api/runs',{method:'POST',headers:headers(true),body:JSON.stringify({project_id:project,task,agent_id:'zynx_main'})});if(!r.ok){setError('Task submission failed');return}setTask('');await load()}
 async function decide(id:string,decision:string){const r=await fetch(API+'/api/approvals/'+id+'/decision',{method:'POST',headers:headers(true),body:JSON.stringify({decision,reviewer:'dashboard-operator'})});if(!r.ok){setError('Approval update failed');return}await load()}
 return <main><aside><div className="brand"><div className="mark">Z</div><div><b>Zynx Agent Forge</b><small>OPERATIONS CONTROL</small></div></div><nav>{['Overview','Agents','Runs','Approvals','Audit'].map(x=><button className={tab===x?'active':''} onClick={()=>setTab(x)} key={x}>{x}</button>)}</nav><div className="sidefoot">Independent control plane<br/>Connected to ZynxAGI MCP bridge</div></aside>
 <section className="content"><header><div><small>ZY​​NX ECOSYSTEM / AGENT FORGE</small><h1>{tab}</h1></div><div className="toolbar"><input type="password" aria-label="Agent Forge API token" value={token} onChange={e=>setToken(e.target.value)} placeholder="API token (session only)"/><button className="refresh" onClick={load}><RefreshCw size={16}/> Refresh</button></div></header>
 {error&&<div className="error">{error}</div>}
 <div className="cards"><div><Activity/><small>PROJECTS</small><strong>{data?.projects??'—'}</strong></div><div><ClipboardList/><small>RECENT RUNS</small><strong>{data?.runs?.length??'—'}</strong></div><div><ShieldCheck/><small>PENDING APPROVALS</small><strong>{data?.approvals?.filter(a=>a.status==='pending').length??'—'}</strong></div><div><Bot/><small>REGISTERED AGENTS</small><strong>{data?.agents?.length??'—'}</strong></div></div>
 {tab==='Overview'&&<><div className="panel"><h2>Start an orchestration run</h2><div className="form"><select value={project} onChange={e=>setProject(e.target.value)}><option value="">Select project</option>{projects.map(p=><option value={p.id} key={p.id}>{p.name}</option>)}</select><input value={name} onChange={e=>setName(e.target.value)} placeholder="Project name"/><button onClick={createProject}><PlusCircle size={16}/> Create project</button></div><textarea value={task} onChange={e=>setTask(e.target.value)} placeholder="Describe a task for the specialist agent…"/><button onClick={submit} disabled={!project||!task.trim()}>Submit task</button></div><div className="panel"><h2>Recent runs</h2><Rows rows={data?.runs||[]} fields={['task','agent_id','status','created_at']}/></div></>}
 {tab==='Agents'&&<div className="panel"><h2>Specialist registry</h2><Rows rows={data?.agents||[]} fields={['id','description','actions']}/><p className="muted">ZynxAGI bridge: {data?.integration?.zynxagi||'checking'} · Existing MCPDispatcher is the dispatch path.</p></div>}
 {tab==='Runs'&&<div className="panel"><h2>Run history</h2><Rows rows={data?.runs||[]} fields={['id','task','agent_id','status','error']}/></div>}
 {tab==='Approvals'&&<div className="panel"><h2>Human approval queue</h2>{(data?.approvals||[]).map(a=><div className="item" key={a.id}><b>{a.action}</b><span>{a.status}</span><small>{a.id}</small>{a.status==='pending'&&<div><button onClick={()=>decide(a.id,'approved')}>Approve</button> <button className="danger" onClick={()=>decide(a.id,'rejected')}>Reject</button></div>}</div>)}</div>}
 {tab==='Audit'&&<div className="panel"><h2>Audit events</h2><Rows rows={audit} fields={['action','actor','resource','created_at','event_hash']}/></div>}
 </section></main>
}
function Rows({rows,fields}:{rows:any[];fields:string[]}){return <div className="rows">{rows.map((r,i)=><div className="rowitem" key={r.id||i}>{fields.map(f=><span key={f}><small>{f}</small>{String(r[f]??'—').slice(0,180)}</span>)}</div>)}{!rows.length&&<p className="muted">No records yet.</p>}</div>}
