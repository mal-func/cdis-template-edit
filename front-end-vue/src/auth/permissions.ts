import type { User } from "./types";

/** Match the backend's any-of permission semantics; never infer permissions from role names. */
export function hasPermission(user:User|null,permission:string|string[]):boolean{
 if(!user)return false;
 const required=Array.isArray(permission)?permission:[permission];
 return required.some(item=>user.permissions.includes(item));
}