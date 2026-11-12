<script setup lang="ts">
import { useAuthStore } from "@/auth/store";
const auth=useAuthStore();
function capitalize(s:string){return s.charAt(0).toUpperCase()+s.slice(1);}
</script>
<template><div><h1 class="page-title">Settings</h1><p class="muted">Your account details, read from the current session.</p><div class="grid" style="max-width:760px;margin-top:20px">
 <section class="card"><h2 style="font-size:16px;margin:0">Account</h2><dl class="settings-list"><div><dt>Name</dt><dd>{{auth.user?.name}}</dd></div><div><dt>Email</dt><dd>{{auth.user?.email}}</dd></div><div><dt>User ID</dt><dd style="font-family:monospace">{{auth.user?.id}}</dd></div></dl></section>
 <section class="card"><h2 style="font-size:16px;margin:0">Roles</h2><div style="margin-top:12px"><span v-for="role in auth.user?.roles??[]" :key="role" class="pill">{{capitalize(role)}}</span></div></section>
 <section class="card"><h2 style="font-size:16px;margin:0">Permissions</h2><div v-if="auth.user?.permissions.length" style="margin-top:12px"><span v-for="permission in auth.user.permissions" :key="permission" class="pill">{{permission}}</span></div><p v-else class="muted">No additional permissions granted.</p></section>
 </div></div></template>
<style scoped>.settings-list{font-size:14px}.settings-list div{display:flex;justify-content:space-between;gap:15px;padding:12px 0;border-bottom:1px solid #f1f5f9}.settings-list dt{color:#64748b}.settings-list dd{margin:0;font-weight:600;text-align:right}</style>