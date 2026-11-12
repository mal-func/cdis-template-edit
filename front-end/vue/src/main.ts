import { createApp } from "vue";
import { createPinia } from "pinia";
import { VueQueryPlugin, QueryClient } from "@tanstack/vue-query";
import App from "./App.vue";
import router from "./router";
import "./styles.css";
import "leaflet/dist/leaflet.css";

const queryClient = new QueryClient({
  defaultOptions: { queries: { retry: 1, refetchOnWindowFocus: false, staleTime: 30_000 } },
});
createApp(App).use(createPinia()).use(router).use(VueQueryPlugin, { queryClient }).mount("#app");