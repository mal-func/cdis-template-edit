import { describe, expect, it } from "vitest";
import { loginSchema, registerSchema } from "./schemas";

describe("loginSchema",()=>{
  it("accepts valid credentials",()=>expect(loginSchema.safeParse({email:"person@example.com",password:"password123"}).success).toBe(true));
  it("rejects invalid email and short password",()=>expect(loginSchema.safeParse({email:"bad",password:"short"}).success).toBe(false));
});
describe("registerSchema",()=>{
  it("requires matching passwords",()=>expect(registerSchema.safeParse({name:"Test",email:"person@example.com",password:"password123",confirmPassword:"different"}).success).toBe(false));
  it("trims name and email",()=>expect(registerSchema.parse({name:" Test ",email:" person@example.com ",password:"password123",confirmPassword:"password123"}).name).toBe("Test"));
});