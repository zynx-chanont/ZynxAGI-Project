import React from "react";
import type { AgentStatus } from "@zynx/types";
export function StatusDot({status}:{status:AgentStatus}):React.ReactElement {
  const c:Record<AgentStatus,string>={active:"bg-green-500",inactive:"bg-gray-400",error:"bg-red-500",pending:"bg-yellow-400"};
  return <span className={["inline-block h-2.5 w-2.5 rounded-full",c[status]].join(" ")} aria-label={status}/>;
}
