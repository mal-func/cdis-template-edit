<script setup lang="ts">
import { onMounted, reactive, ref } from "vue";
import { RouterLink, useRoute, useRouter } from "vue-router";
import { Eye, EyeOff, ShieldCheck, RefreshCw, LayoutDashboard } from "lucide-vue-next";
import { loginSchema } from "@/auth/schemas";
import { useAuthStore } from "@/auth/store";
import { appConfig } from "@/config/env";
import { ApiError } from "@/api/http";
const auth=useAuthStore(),router=useRouter(),route=useRoute();
const values=reactive({email:"",password:""}),errors=ref<Record<string,string>>({}),busy=ref(false),serverError=ref(""),showPassword=ref(false);
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
        <span class="auth-eyebrow"><ShieldCheck :size="14" />Secure sign-in</span>
        <h1>Welcome back</h1>
        <p class="auth-subtitle">Sign in to your {{ appConfig.name }} account to continue.</p>
        <form @submit.prevent="submit" novalidate>
          <div v-if="serverError" class="error" role="alert" style="margin-bottom:16px">{{ serverError }}</div>
          <div class="field">
            <label for="email">Email address</label>
            <input id="email" v-model="values.email" type="email" placeholder="you@company.com" autocomplete="email" :disabled="busy" :aria-invalid="Boolean(errors.email)">
            <span v-if="errors.email" class="error" role="alert">{{ errors.email }}</span>
          </div>
          <div class="field">
            <label for="password">Password</label>
            <div class="password-field">
              <input id="password" v-model="values.password" :type="showPassword?'text':'password'" placeholder="Enter your password" autocomplete="current-password" :disabled="busy" :aria-invalid="Boolean(errors.password)">
              <button class="password-toggle" type="button" :aria-label="showPassword?'Hide password':'Show password'" @click="showPassword=!showPassword"><EyeOff v-if="showPassword" :size="17" /><Eye v-else :size="17" /></button>
            </div>
            <span v-if="errors.password" class="error" role="alert">{{ errors.password }}</span>
          </div>
          <button class="btn auth-submit" type="submit" :disabled="busy">{{ busy?"Signing in…":"Sign In" }}</button>
        </form>
        <p v-if="auth.authOptions?.selfRegistration" class="auth-switch">Don't have an account? <RouterLink to="/register">Create one</RouterLink></p>
      </div>
    </section>
  </main>
</template>
