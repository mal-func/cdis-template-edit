<script setup lang="ts">
import { onMounted, reactive, ref } from "vue";
import { RouterLink, useRouter } from "vue-router";
import { ShieldCheck, RefreshCw, LayoutDashboard } from "lucide-vue-next";
import { registerSchema } from "@/auth/schemas";
import { useAuthStore } from "@/auth/store";
import { appConfig } from "@/config/env";
import { ApiError } from "@/api/http";
const auth=useAuthStore(),router=useRouter();
const values=reactive({name:"",email:"",password:"",confirmPassword:""}),errors=ref<Record<string,string>>({}),busy=ref(false),serverError=ref("");
onMounted(()=>auth.loadOptions());
async function submit(){errors.value={};serverError.value="";const parsed=registerSchema.safeParse(values);if(!parsed.success){for(const issue of parsed.error.issues)errors.value[String(issue.path[0])]=issue.message;return;}busy.value=true;try{const {confirmPassword,...payload}=parsed.data;void confirmPassword;await auth.register(payload);await router.replace("/dashboard");}catch(e){serverError.value=e instanceof ApiError?e.message:"Unable to create your account. Please try again.";}finally{busy.value=false;}}
</script>
<template>
  <main class="auth-page">
    <aside class="auth-brand-panel">
      <div class="auth-brand-logo"><span><img src="/cdis_logo.png" alt=""></span>{{ appConfig.name }}</div>
      <div class="auth-brand-content">
        <h2>A secure foundation for every project your team ships.</h2>
        <ul class="auth-brand-features">
          <li><span class="auth-feature-icon"><ShieldCheck :size="15" /></span><span>Role-based access control, enforced permission-by-permission on every request</span></li>
          <li><span class="auth-feature-icon"><RefreshCw :size="15" /></span><span>Rotating sessions with automatic refresh-token theft detection</span></li>
          <li><span class="auth-feature-icon"><LayoutDashboard :size="15" /></span><span>A working dashboard, tables, and charts — ready from day one</span></li>
        </ul>
      </div>
      <p class="auth-brand-footer">© {{ new Date().getFullYear() }} {{ appConfig.name }}</p>
    </aside>
    <section class="auth-form-panel">
      <div class="auth-mobile-brand"><span><img src="/cdis_logo.png" alt=""></span>{{ appConfig.name }}</div>
      <div class="auth-card">
        <span class="auth-eyebrow"><ShieldCheck :size="14" />Create your account</span>
        <h1>Create account</h1>
        <p class="auth-subtitle">Join your {{ appConfig.name }} workspace.</p>
        <p v-if="auth.optionsLoading" class="muted">Checking registration settings…</p>
        <div v-else-if="!auth.authOptions?.selfRegistration" class="card">Sign-up is turned off. Accounts are created by an administrator.</div>
        <form v-else @submit.prevent="submit" novalidate>
          <p v-if="serverError" class="error" role="alert" style="margin-bottom:16px">{{ serverError }}</p>
          <div class="field"><label for="register-name">Full name</label><input id="register-name" v-model="values.name" placeholder="Your name" autocomplete="name" :disabled="busy"><span v-if="errors.name" class="error" role="alert">{{ errors.name }}</span></div>
          <div class="field"><label for="register-email">Email address</label><input id="register-email" v-model="values.email" type="email" placeholder="you@company.com" autocomplete="email" :disabled="busy"><span v-if="errors.email" class="error" role="alert">{{ errors.email }}</span></div>
          <div class="field"><label for="register-password">Password</label><input id="register-password" v-model="values.password" type="password" placeholder="Create a password" autocomplete="new-password" :disabled="busy"><span v-if="errors.password" class="error" role="alert">{{ errors.password }}</span></div>
          <div class="field"><label for="register-confirm-password">Confirm password</label><input id="register-confirm-password" v-model="values.confirmPassword" type="password" placeholder="Confirm your password" autocomplete="new-password" :disabled="busy"><span v-if="errors.confirmPassword" class="error" role="alert">{{ errors.confirmPassword }}</span></div>
          <button class="btn auth-submit" type="submit" :disabled="busy">{{ busy?"Creating account…":"Create Account" }}</button>
        </form>
        <p class="auth-switch">Already have an account? <RouterLink to="/login">Sign in</RouterLink></p>
      </div>
    </section>
  </main>
</template>
