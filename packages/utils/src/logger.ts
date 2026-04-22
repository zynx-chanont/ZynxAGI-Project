type Level = "debug"|"info"|"warn"|"error";
const lvl: Record<Level,number> = {debug:0,info:1,warn:2,error:3};
const cur = (process.env["LOG_LEVEL"] ?? "info") as Level;
function log(l: Level, msg: string, meta?: unknown) {
  if (lvl[l]! < lvl[cur]!) return;
  const out = JSON.stringify({timestamp:new Date().toISOString(),level:l,message:msg,...(meta?{meta}:{})});
  l==="error"?console.error(out):l==="warn"?console.warn(out):console.log(out);
}
export const logger = {debug:(m:string,x?:unknown)=>log("debug",m,x),info:(m:string,x?:unknown)=>log("info",m,x),warn:(m:string,x?:unknown)=>log("warn",m,x),error:(m:string,x?:unknown)=>log("error",m,x)};
