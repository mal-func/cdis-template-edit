<script setup lang="ts">
defineProps<{title:string;description?:string|null}>();
</script>
<template>
  <section class="card">
    <h2 style="font-size:16px;margin:0 0 12px">
      {{ title }}
    </h2><slot /><p
      v-if="description"
      class="muted"
    >
      {{ description }}
    </p>
  </section>
</template>