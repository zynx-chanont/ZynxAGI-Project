import { z } from "zod";
export type ValidationResult<T> = {success:true;data:T}|{success:false;errors:string[]};
export function validate<T>(schema: z.ZodType<T>, input: unknown): ValidationResult<T> {
  const r = schema.safeParse(input);
  if (r.success) return {success:true,data:r.data};
  return {success:false,errors:r.error.issues.map(i=>`${i.path.join(".")}: ${i.message}`)};
}
