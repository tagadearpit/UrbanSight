import fs from 'node:fs';
import path from 'node:path';
const base=(process.env.BACKEND_URL||'http://localhost:4173').replace(/\/$/,'');
const scenarioName=(process.env.SCENARIO||'all').toLowerCase();
const scenarios=['scenario-road-defects.json','scenario-traffic.json','scenario-incidents.json'].map(file=>JSON.parse(fs.readFileSync(path.resolve('scenarios',file))));
const events=scenarioName==='all'?scenarios.flatMap(x=>x.events):scenarios.find(x=>x.name?.toLowerCase().includes(scenarioName))?.events||scenarios[0].events;
const routePath=[[19.076,72.877],[19.083,72.889],[19.091,72.902],[19.099,72.916],[19.108,72.929],[19.115,72.941]];
const speed=Math.max(1,Number(process.env.SPEED||1)); let cursor=0; let position=0;
function makeEvent(){const raw=events[cursor++%events.length];const [latitude,longitude]=routePath[position++%routePath.length];const metadata={...(raw.metadata||{}),inferenceMode:'SIMULATION',source:'edge-simulator',routePosition:position};return {...raw,eventId:`edge-${Date.now()}-${cursor}`,latitude,longitude,timestamp:new Date().toISOString(),evidence:{imageUrl:'demo://evidence/simulated-frame.jpg',videoUrl:null},metadata};}
async function once(){const payload=makeEvent();const response=await fetch(`${base}/api/events`,{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify(payload)});const body=await response.text();console.log(JSON.stringify({eventType:payload.eventType,busId:payload.busId,status:response.status,body}));}
console.log(`UrbanSight edge simulator · scenario=${scenarioName} · speed=${speed}x · backend=${base}`);await once();setInterval(()=>once().catch(error=>console.error('simulator error',error.message)),Math.max(500,3000/speed));
