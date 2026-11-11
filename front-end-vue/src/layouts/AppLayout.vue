<script setup lang="ts">
import { computed, ref, watch } from "vue";
import { useRoute, useRouter, RouterLink, RouterView } from "vue-router";
import { useAuthStore, hasPermission } from "@/auth/store";
import { appConfig } from "@/config/env";
import { LayoutDashboard, LineChart, ChartPie, Table2, Users, Settings, Menu, LogOut, Bell, MoonStar } from "lucide-vue-next";
const auth=useAuthStore(),route=useRoute(),router=useRouter();
const collapsed=ref(false),mobileOpen=ref(false),dark=ref(false);
const nav=[{label:"Dashboard",to:"/dashboard",icon:LayoutDashboard},{label:"Graphs",to:"/graphs",icon:LineChart},{label:"Charts",to:"/charts",icon:ChartPie},{label:"Table",to:"/tables",icon:Table2}];
const title=computed(()=>String(route.meta.title??"Dashboard"));
const initials=computed(()=>auth.user?.name.split(" ").slice(0,2).map(x=>x[0]?.toUpperCase()).join("")??"");
watch(()=>auth.isAuthenticated,(authenticated)=>{if(!authenticated&&route.meta.requiresAuth)void router.replace({path:"/login",query:{redirect:route.fullPath}});});
async function signOut(){await auth.logout();}
</script>
<template><div class="app-shell" :class="{dark}">
 <aside class="sidebar" :class="{collapsed,mobileOpen}">
  <div class="brand"><span class="brand-mark"><img src="/cdis_logo.png" :alt="appConfig.name"/></span><span v-if="!collapsed">{{appConfig.name}}<small style="display:block;color:#94a3b8;font-size:10px;letter-spacing:2px">DASHBOARD</small></span></div>
  <nav class="nav-list"><RouterLink v-for="item in nav" :key="item.to" :to="item.to" class="nav-link" @click="mobileOpen=false"><component :is="item.icon" :size="18"/><span v-if="!collapsed">{{item.label}}</span></RouterLink><RouterLink v-if="hasPermission(auth.user,'users:read')" to="/users" class="nav-link" @click="mobileOpen=false"><Users :size="18"/><span v-if="!collapsed">Users</span></RouterLink></nav>
  <div class="sidebar-bottom"><RouterLink to="/settings" class="nav-link"><Settings :size="18"/><span v-if="!collapsed">Settings</span></RouterLink><button v-if="!mobileOpen" class="nav-link" style="width:100%;border:0;background:transparent" @click="collapsed=!collapsed"><Menu :size="18"/><span v-if="!collapsed">Collapse</span></button></div>
 </aside>
 <div class="main-area" :class="{collapsed}"><header class="topbar">
  <button class="btn btn-secondary mobile-menu" @click="mobileOpen=!mobileOpen"><Menu :size="17"/></button>
  <button class="btn btn-secondary" aria-label="Notifications" title="No notifications yet"><Bell :size="17"/></button>
  <button class="btn btn-secondary" aria-label="Toggle theme" @click="dark=!dark"><MoonStar :size="17"/></button>
  <div class="user-menu" v-if="auth.user"><span class="avatar">{{initials}}</span><span class="user-name"><strong style="display:block;font-size:13px">{{auth.user.name}}</strong><small class="muted">{{auth.user.roles[0]}}</small></span><button class="btn btn-secondary" aria-label="Log out" @click="signOut"><LogOut :size="16"/></button></div>
 </header><main class="page-content"><div class="muted" style="margin-bottom:16px">Home / {{title}}</div><RouterView/></main></div>
</div></template>