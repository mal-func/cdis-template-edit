import { z } from "zod";

export const loginSchema = z.object({
  email: z.string().trim().pipe(z.email("Please enter a valid email address.")),
  password: z.string().min(8, "Password must contain at least 8 characters."),
});
export const registerSchema = z.object({
  name: z.string().trim().min(1, "Please enter your name.").max(255, "Name is too long."),
  email: z.string().trim().pipe(z.email("Please enter a valid email address.")),
  password: z.string().min(8, "Password must contain at least 8 characters."),
  confirmPassword: z.string(),
}).refine((value) => value.password === value.confirmPassword, {
  message: "Passwords don't match.", path: ["confirmPassword"],
});
export type LoginValues = z.infer<typeof loginSchema>;
export type RegisterValues = z.infer<typeof registerSchema>;