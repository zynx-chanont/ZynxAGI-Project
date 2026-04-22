import { z } from "zod";
export const UserRoleSchema = z.enum(["admin","developer","viewer"]);
export const UserSchema = z.object({id:z.string().uuid(),email:z.string().email(),name:z.string().min(1),role:UserRoleSchema,tenantId:z.string().uuid(),createdAt:z.string().datetime()});
export type UserRole = z.infer<typeof UserRoleSchema>;
export type User = z.infer<typeof UserSchema>;
