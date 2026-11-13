<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref, watch } from "vue";
import { useRoute, useRouter, RouterLink, RouterView } from "vue-router";
import { useAuthStore, hasPermission } from "@/auth/store";
import { appConfig } from "@/config/env";
import { LayoutDashboard, LineChart, ChartPie, Table2, Users, Settings, Menu, LogOut, Bell, MoonStar, Search } from "lucide-vue-next";
const auth=useAuthStore(),route=useRoute(),router=useRouter();
const collapsed=ref(false),mobileOpen=ref(false),dark=ref(typeof window==="undefined"||localStorage.getItem("cdis-shell-theme")!=="light");
const searchQuery=ref(""),searchInput=ref<HTMLInputElement|null>(null);
const nav=[{label:"Dashboard",to:"/dashboard",icon:LayoutDashboard},{label:"Graphs",to:"/graphs",icon:LineChart},{label:"Charts",to:"/charts",icon:ChartPie},{label:"Table",to:"/tables",icon:Table2}];
const title=computed(()=>String(route.meta.title??"Dashboard"));
const initials=computed(()=>auth.user?.name.split(" ").slice(0,2).map(x=>x[0]?.toUpperCase()).join("")??"");
const searchResults=computed(()=>{const q=searchQuery.value.trim().toLowerCase();return q?nav.filter(item=>item.label.toLowerCase().includes(q)):[];});
function handleShortcut(event:KeyboardEvent){if((event.metaKey||event.ctrlKey)&&event.key.toLowerCase()==="k"){event.preventDefault();searchInput.value?.focus();}}
function selectSearch(path:string){searchQuery.value="";void router.push(path);}
watch(dark,(value)=>{document.documentElement.classList.toggle("dark",value);localStorage.setItem("cdis-shell-theme",value?"dark":"light");},{immediate:true});
watch(()=>auth.isAuthenticated,(authenticated)=>{if(!authenticated&&route.meta.requiresAuth)void router.replace({path:"/login",query:{redirect:route.fullPath}});});
onMounted(()=>window.addEventListener("keydown",handleShortcut));
onBeforeUnmount(()=>window.removeEventListener("keydown",handleShortcut));
async function signOut(){await auth.logout();}
</script>
<template>
  <div
    class="app-shell"
    :class="{dark}"
  >
    <aside
      class="sidebar"
      :class="{collapsed,mobileOpen}"
    >
      <div class="brand">
        <span class="brand-mark"><img
          src="/cdis_logo.png"
          :alt="appConfig.name"
        ></span><span v-if="!collapsed">{{ appConfig.name }}<small style="display:block;color:#94a3b8;font-size:10px;letter-spacing:2px">DASHBOARD</small></span>
      </div>
      <nav class="nav-list">
        <RouterLink
          v-for="item in nav"
          :key="item.to"
          :to="item.to"
          class="nav-link"
          @click="mobileOpen=false"
        ><component
          :is="item.icon"
          :size="18"
        /><span v-if="!collapsed">{{ item.label }}</span></RouterLink><RouterLink
          v-if="hasPermission(auth.user,'users:read')"
          to="/users"
          class="nav-link"
          @click="mobileOpen=false"
        ><Users :size="18" /><span v-if="!collapsed">Users</span></RouterLink>
      </nav>
      <div class="sidebar-bottom">
        <RouterLink
          to="/settings"
          class="nav-link"
        ><Settings :size="18" /><span v-if="!collapsed">Settings</span></RouterLink><button
          v-if="!mobileOpen"
          class="nav-link"
          style="width:100%;border:0;background:transparent"
          @click="collapsed=!collapsed"
        >
          <Menu :size="18" /><span v-if="!collapsed">Collapse</span>
        </button>
      </div>
    </aside>
    <div
      class="main-area"
      :class="{collapsed}"
    >
      <header class="topbar">
        <button
          class="btn btn-secondary mobile-menu"
          @click="mobileOpen=!mobileOpen"
        >
          <Menu :size="17" />
        </button>
        <div class="nav-search">
          <Search :size="16" /><input
            ref="searchInput"
            v-model="searchQuery"
            type="search"
            placeholder="Search anything…"
            aria-label="Search navigation"
            @keydown.escape="searchQuery=''"
          ><kbd>Ctrl K</kbd><div
            v-if="searchResults.length"
            class="search-results"
          >
            <button
              v-for="item in searchResults"
              :key="item.to"
              @click="selectSearch(item.to)"
            >
              {{ item.label }}
            </button>
          </div>
        </div>
        <button
          class="btn btn-secondary"
          aria-label="Notifications"
          title="No notifications yet"
        >
          <Bell :size="17" />
        </button>
        <button
          class="btn btn-secondary"
          aria-label="Toggle theme"
          @click="dark=!dark"
        >
          <MoonStar :size="17" />
        </button>
        <div
          v-if="auth.user"
          class="user-menu"
        >
          <span class="avatar">{{ initials }}</span><span class="user-name"><strong style="display:block;font-size:13px">{{ auth.user.name }}</strong><small class="muted">{{ auth.user.roles[0] }}</small></span><button
            class="btn btn-secondary"
            aria-label="Log out"
            @click="signOut"
          >
            <LogOut :size="16" />
          </button>
        </div>
      </header><main class="page-content">
        <div
          v-if="route.path!=='/dashboard'"
          class="muted"
          style="margin-bottom:16px"
        >
          Dashboard / {{ title }}
        </div><RouterView />
      </main>
    </div>
  </div>
</template>