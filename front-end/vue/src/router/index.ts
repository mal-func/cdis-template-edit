import { createRouter, createWebHistory } from "vue-router";
import { useAuthStore, hasPermission } from "@/auth/store";
import AppLayout from "@/layouts/AppLayout.vue";
import LoginPage from "@/pages/LoginPage.vue";
import RegisterPage from "@/pages/RegisterPage.vue";
import DashboardPage from "@/pages/DashboardPage.vue";
import UsersPage from "@/pages/UsersPage.vue";
import SettingsPage from "@/pages/SettingsPage.vue";
import GraphsPage from "@/pages/GraphsPage.vue";
import ChartsPage from "@/pages/ChartsPage.vue";
import TablesPage from "@/pages/TablesPage.vue";
import ForbiddenPage from "@/pages/ForbiddenPage.vue";
import NotFoundPage from "@/pages/NotFoundPage.vue";

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: "/", redirect: "/dashboard" },
    { path: "/login", component: LoginPage, meta: { guestOnly: true } },
    { path: "/register", component: RegisterPage, meta: { guestOnly: true } },
    {
      path: "/", component: AppLayout, meta: { requiresAuth: true },
      children: [
        { path: "dashboard", component: DashboardPage, meta: { title: "Dashboard" } },
        { path: "graphs", component: GraphsPage, meta: { title: "Graphs" } },
        { path: "charts", component: ChartsPage, meta: { title: "Charts" } },
        { path: "tables", component: TablesPage, meta: { title: "Table" } },
        { path: "users", component: UsersPage, meta: { title: "Users", permission: "users:read" } },
        { path: "settings", component: SettingsPage, meta: { title: "Settings" } },
      ],
    },
    { path: "/forbidden", component: ForbiddenPage },
    { path: "/:pathMatch(.*)*", component: NotFoundPage },
  ],
});

router.beforeEach(async (to) => {
  const auth = useAuthStore();
  if (auth.loading) await auth.restoreSession();
  if (to.meta.requiresAuth && !auth.isAuthenticated) {
    return { path: "/login", query: { redirect: to.fullPath } };
  }
  if (to.meta.guestOnly && auth.isAuthenticated) return "/dashboard";
  const permission = to.meta.permission;
  if (typeof permission === "string" && !hasPermission(auth.user, permission)) return "/forbidden";
  return true;
});
export default router;