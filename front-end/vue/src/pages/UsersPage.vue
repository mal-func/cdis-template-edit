<script setup lang="ts">
import { computed, ref } from "vue";
import { useMutation, useQuery, useQueryClient } from "@tanstack/vue-query";
import { api, ApiError } from "@/api/http";
import { hasPermission, useAuthStore } from "@/auth/store";
import type { Role, User, Pagination } from "@/auth/types";
const PAGE_SIZE=20,page=ref(0),search=ref(""),editing=ref<User|null>(null),selected=ref<string[]>([]),saveError=ref("");
const auth=useAuthStore(),client=useQueryClient();
const canManageRoles=computed(()=>hasPermission(auth.user,"roles:manage"));
const usersQuery=useQuery({queryKey:computed(()=>["users","list",page.value]),queryFn:()=>api.get<{users:User[];pagination:Pagination}>("/users",{limit:PAGE_SIZE,offset:page.value*PAGE_SIZE})});
const rolesQuery=useQuery({queryKey:["roles","list"],queryFn:()=>api.get<{roles:Role[]}>("/roles"),enabled:canManageRoles});
const usersPending=computed(()=>usersQuery.isPending.value),usersError=computed(()=>usersQuery.isError.value);
const rolesPending=computed(()=>rolesQuery.isPending.value),rolesError=computed(()=>rolesQuery.isError.value);
const roles=computed(()=>rolesQuery.data.value?.roles??[]);
const save=useMutation({mutationFn:()=>api.put<{user:User}>("/users/"+encodeURIComponent(editing.value!.id)+"/roles",{roles:selected.value}),onSuccess:async()=>{await client.invalidateQueries({queryKey:["users","list"]});editing.value=null;},onError:(e)=>{saveError.value=e instanceof ApiError?e.message:"Couldn't save roles. Please try again."; }});
const savePending=computed(()=>save.isPending.value);
const total=computed(()=>usersQuery.data.value?.pagination.total??0),pages=computed(()=>Math.max(1,Math.ceil(total.value/PAGE_SIZE)));
const filtered=computed(()=> (usersQuery.data.value?.users??[]).filter(u=>(u.name+" "+u.email).toLowerCase().includes(search.value.toLowerCase())));
function openRoles(user:User){editing.value=user;selected.value=[...user.roles];saveError.value="";}
function toggle(role:string){selected.value=selected.value.includes(role)?selected.value.filter(r=>r!==role):[...selected.value,role];}
function close(){editing.value=null;save.reset();}
</script>
<template><div><h1 class="page-title">Users</h1><p class="muted">Manage workspace users and their assigned roles.</p>
 <div class="toolbar"><input v-model="search" placeholder="Search this page…" style="padding:10px 12px;border:1px solid #cbd5e1;border-radius:8px;width:min(100%,320px)"/><span class="muted">{{total}} users</span></div>
 <section class="card"><p v-if="usersPending" class="muted">Loading users…</p><p v-else-if="usersError" class="error">Failed to load users.</p><div v-else class="table-wrap"><table class="data-table"><thead><tr><th>Name</th><th>Email</th><th>Roles</th><th v-if="canManageRoles">Actions</th></tr></thead><tbody><tr v-for="user in filtered" :key="user.id"><td>{{user.name}}</td><td>{{user.email}}</td><td><span v-for="role in user.roles" :key="role" class="pill">{{role}}</span></td><td v-if="canManageRoles"><span v-if="user.id===auth.user?.id" class="muted">You</span><button v-else class="btn btn-secondary" @click="openRoles(user)">Edit roles</button></td></tr><tr v-if="!filtered.length"><td colspan="4" class="muted">No users found.</td></tr></tbody></table></div>
 <div class="toolbar" style="margin-bottom:0"><span class="muted">Page {{page+1}} of {{pages}}</span><div style="display:flex;gap:8px"><button class="btn btn-secondary" :disabled="page===0" @click="page--">Previous</button><button class="btn btn-secondary" :disabled="page+1>=pages" @click="page++">Next</button></div></div></section>
 <div v-if="editing" class="modal-backdrop" @click.self="close"><section class="modal card" role="dialog" aria-modal="true" aria-labelledby="roles-title"><h2 id="roles-title" style="margin:0;font-size:18px">Edit roles</h2><p class="muted">{{editing.name}} ({{editing.email}}). Changes apply on their next request.</p>
 <p v-if="rolesPending" class="muted">Loading roles…</p><p v-else-if="rolesError" class="error">Couldn't load available roles.</p>
 <label v-for="role in roles" :key="role.name" class="role-option"><input type="checkbox" :checked="selected.includes(role.name)" @change="toggle(role.name)"/><span><strong>{{role.name}}</strong><small class="muted" style="display:block">{{role.description}}</small><small class="muted">{{role.permissions.join(", ")||"No extra permissions"}}</small></span></label>
 <p v-if="selected.length===0" class="error">A user must keep at least one role.</p><p v-if="saveError" class="error" role="alert">{{saveError}}</p>
 <div class="toolbar"><button class="btn btn-secondary" @click="close">Cancel</button><button class="btn" :disabled="!selected.length||savePending||selected.length===editing.roles.length&&selected.every(r=>editing?.roles.includes(r))" @click="save.mutate()">{{savePending?"Saving…":"Save roles"}}</button></div>
 </section></div>
</div></template>
<style scoped>.modal-backdrop{position:fixed;inset:0;background:#0f172a66;z-index:50;display:grid;place-items:center;padding:16px}.modal{width:min(100%,480px);max-height:85vh;overflow:auto}.role-option{display:flex;gap:12px;padding:12px;border:1px solid #e2e8f0;border-radius:8px;margin:8px 0;font-size:13px}.role-option input{margin-top:3px}</style>