// Production boundary: keep auth on the server and never trust a role sent by the browser.
const buckets=new Map();
export function rateLimit(req,res,next,{limit=120,windowMs=60000}={}){const key=req.socket.remoteAddress||'unknown';const now=Date.now();const b=buckets.get(key);if(!b||now-b.started>windowMs){buckets.set(key,{started:now,count:1});return next()}if(++b.count>limit){res.writeHead(429,{'content-type':'application/json'});return res.end(JSON.stringify({error:'rate limit exceeded'}))}next()}
export function requireRole(roles){return (req,res,next)=>{const user=req.authenticatedUser;if(!user)return res.writeHead(401)&&res.end(JSON.stringify({error:'authentication required'}));if(!roles.includes(user.role))return res.writeHead(403)&&res.end(JSON.stringify({error:'forbidden'}));next()}}
export function audit(action,userId,metadata={}){console.info(JSON.stringify({audit:true,action,userId,metadata,timestamp:new Date().toISOString()}))}
// Replace this development adapter with OAuth/JWT verification before production deployment.
export function authenticateDevelopment(req,_res,next){req.authenticatedUser={id:'demo-authority',role:'TRANSPORT_AUTHORITY'};next()}
