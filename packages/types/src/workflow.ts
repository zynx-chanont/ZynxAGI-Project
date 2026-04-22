import { z } from "zod";
export const WorkflowStatusSchema = z.enum(["draft","running","completed","failed"]);
export const WorkflowSchema = z.object({id:z.string().uuid(),name:z.string().min(1),status:WorkflowStatusSchema,steps:z.array(z.object({id:z.string(),agentId:z.string().uuid(),input:z.record(z.unknown())})),createdAt:z.string().datetime(),updatedAt:z.string().datetime()});
export type WorkflowStatus = z.infer<typeof WorkflowStatusSchema>;
export type Workflow = z.infer<typeof WorkflowSchema>;
