import React from "react";
import type { AgentStatus } from "@zynx/types";
export function Badge({label,variant="default"}:{label:string;variant?:"default"|"success"|"warning"|"error"|"info"}):React.ReactElement {
  const v={default:"bg-gray-100 text-gray-700",success:"bg-green-100 text-green-700",warning:"bg-yellow-100 text-yellow-700",error:"bg-red-100 text-red-700",info:"bg-blue-100 text-blue-700"};
  return <span className={["inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium",v[variant]].join(" ")}>{label}</span>;
}
export function AgentStatusBadge({status}:{status:AgentStatus}):React.ReactElement {
  const m:Record<AgentStatus,"default"|"success"|"warning"|"error"|"info">={active:"success",inactive:"default",error:"error",pending:"warning"};
  return <Badge label={status} variant={m[status]}/>;
}
