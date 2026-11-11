import { computed, ref } from "vue";
import { defineStore } from "pinia";
import { api, ApiError, SESSION_EXPIRED_EVENT } from "@/api/http";
import type { AuthOptions, LoginRequest, RegisterRequest, User } from "./types";
export const useAuthStore=defineStore("auth",()=>{
 const user=ref<User|null>(null),loading=ref(true),authOptions=ref<AuthOptions|null>(null),optionsLoading=ref(true);
 const isAuthenticated=computed(()=>user.value!==null);
 async function restoreSession(){loading.value=true;try{const result=await api.get<{user:User}>("/auth/me");user.value=result.user;}catch(error){user.value=null;if(!(error instanceof ApiError)||error.statusCode!==401)console.warn("Failed to restore session",error);}finally{loading.value=false;}}
 async function login(credentials:LoginRequest){const result=await api.post<{user:User}>("/auth/login",credentials);user.value=result.user;}
 async function register(input:RegisterRequest){const result=await api.post<{user:User}>("/auth/register",input);user.value=result.user;}
 async function logout(){try{await api.post<void>("/auth/logout");}finally{user.value=null;}}
 async function loadOptions(){optionsLoading.value=true;try{authOptions.value=await api.get<AuthOptions>("/auth/options");}catch{authOptions.value={selfRegistration:false};}finally{optionsLoading.value=false;}}
 function clearSession(){user.value=null;}
 if(typeof window!=="undefined"){
  window.addEventListener(SESSION_EXPIRED_EVENT,clearSession);
  window.addEventListener("focus",()=>{if(user.value)void restoreSession();});
 }
 return{user,loading,authOptions,optionsLoading,isAuthenticated,restoreSession,login,register,logout,loadOptions};
});
export function hasPermission(user:User|null,permission:string|string[]):boolean{if(!user)return false;const required=Array.isArray(permission)?permission:[permission];return required.some(item=>user.permissions.includes(item));}