<script setup lang="ts">
import { onMounted, reactive, ref } from "vue";
import { useRoute, useRouter, RouterLink } from "vue-router";
import { loginSchema } from "@/auth/schemas";
import { useAuthStore } from "@/auth/store";
import { ApiError } from "@/api/http";
const auth=useAuthStore(),router=useRouter(),route=useRoute();
const values=reactive({email:"",password:""}),errors=ref<Record<string,string>>({}),busy=ref(false),serverError=ref("");
onMounted(()=>auth.loadOptions());
async function submit(){
 errors.value={};serverError.value="";
 const parsed=loginSchema.safeParse(values);
 if(!parsed.success){for(const issue of parsed.error.issues)errors.value[String(issue.path[0])]=issue.message;return;}
 busy.value=true;
 try{await auth.login(parsed.data);await router.replace(typeof route.query.redirect==="string"?route.query.redirect:"/dashboard");}
 catch(e){serverError.value=e instanceof ApiError?e.message:"Unable to sign in. Please try again.";}
 finally{busy.value=false;}
}
</script>
<template><div class="auth-page"><form class="auth-card" @submit.prevent="submit">
  <h1>Welcome back</h1><p class="muted" style="margin-bottom:24px">Sign in to your CDIS workspace</p>
  <div class="field"><label for="email">Email</label><input id="email" v-model="values.email" type="email" autocomplete="username" required/><span class="error">{{errors.email}}</span></div>
  <div class="field"><label for="password">Password</label><input id="password" v-model="values.password" type="password" autocomplete="current-password" required/><span class="error">{{errors.password}}</span></div>
  <p v-if="serverError" class="error" role="alert">{{serverError}}</p>
  <button class="btn" style="width:100%" :disabled="busy">{{busy?"Signing in…":"Sign in"}}</button>
  <p v-if="auth.authOptions?.selfRegistration" class="muted" style="text-align:center;margin-top:20px">Don't have an account? <RouterLink to="/register" style="text-decoration:underline;color:#0f172a">Create one</RouterLink></p>
</form></div></template>