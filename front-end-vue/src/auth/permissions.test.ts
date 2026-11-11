import { describe, expect, it } from "vitest";
import { hasPermission } from "./store";
import type { User } from "./types";
const user:User={id:"1",name:"Test",email:"test@example.com",roles:["admin"],permissions:["users:read","roles:manage"]};
describe("hasPermission",()=>{
 it("returns false for signed-out users",()=>expect(hasPermission(null,"users:read")).toBe(false));
 it("checks a single permission",()=>expect(hasPermission(user,"roles:manage")).toBe(true));
 it("uses any-of semantics for permission arrays",()=>expect(hasPermission(user,["users:write","users:read"])).toBe(true));
 it("does not infer permissions from role names",()=>expect(hasPermission({...user,permissions:[]},"admin")).toBe(false));
});