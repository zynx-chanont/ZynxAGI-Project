import { z } from "zod";
export const AgentStatusSchema = z.enum(["active","inactive","error","pending"]);
export const AgentSchema = z.object({id:z.string().uuid(),name:z.string().min(1),status:AgentStatusSchema,model:z.string(),createdAt:z.string().datetime(),updatedAt:z.string().datetime(),metadata:z.record(z.unknown()).optional()});
export type AgentStatus = z.infer<typeof AgentStatusSchema>;
export type Agent = z.infer<typeof AgentSchema>;
