<script setup lang="ts">
import { onMounted, reactive, ref } from "vue";
import { RouterLink, useRouter } from "vue-router";
import { registerSchema } from "@/auth/schemas";
import { useAuthStore } from "@/auth/store";
import { ApiError } from "@/api/http";
const auth=useAuthStore(),router=useRouter();
const values=reactive({name:"",email:"",password:"",confirmPassword:""}),errors=ref<Record<string,string>>({}),busy=ref(false),serverError=ref("");
onMounted(()=>auth.loadOptions());
async function submit(){errors.value={};serverError.value="";const parsed=registerSchema.safeParse(values);if(!parsed.success){for(const issue of parsed.error.issues)errors.value[String(issue.path[0])]=issue.message;return;}busy.value=true;try{const {confirmPassword,...payload}=parsed.data;void confirmPassword;await auth.register(payload);await router.replace("/dashboard");}catch(e){serverError.value=e instanceof ApiError?e.message:"Unable to create your account. Please try again.";}finally{busy.value=false;}}
</script>
<template><div class="auth-page"><form class="auth-card" @submit.prevent="submit">
 <h1>Create account</h1><p class="muted" style="margin-bottom:24px">Join your CDIS workspace</p>
 <p v-if="auth.optionsLoading" class="muted">Checking registration settings…</p>
 <div v-else-if="!auth.authOptions?.selfRegistration" class="card">Sign-up is turned off. Accounts are created by an administrator.</div>
 <template v-else><div class="field"><label>Name</label><input v-model="values.name" autocomplete="name"/><span class="error">{{errors.name}}</span></div><div class="field"><label>Email</label><input v-model="values.email" type="email" autocomplete="email"/><span class="error">{{errors.email}}</span></div><div class="field"><label>Password</label><input v-model="values.password" type="password" autocomplete="new-password"/><span class="error">{{errors.password}}</span></div><div class="field"><label>Confirm password</label><input v-model="values.confirmPassword" type="password" autocomplete="new-password"/><span class="error">{{errors.confirmPassword}}</span></div><p v-if="serverError" class="error" role="alert">{{serverError}}</p><button class="btn" style="width:100%" :disabled="busy">{{busy?"Creating account…":"Create account"}}</button></template>
 <p class="muted" style="text-align:center;margin-top:20px">Already have an account? <RouterLink to="/login" style="text-decoration:underline;color:#0f172a">Sign in</RouterLink></p>
</form></div></template>