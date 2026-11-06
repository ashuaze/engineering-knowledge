<script setup>
defineProps({ name: String, size: { type: [Number, String], default: 20 } });
const paths = {
  search: ['m21 21-4.4-4.4', 'M19 10.5a8.5 8.5 0 1 1-17 0 8.5 8.5 0 0 1 17 0'],
  menu: ['M4 6h16M4 12h16M4 18h16'],
  close: ['m6 6 12 12M6 18 18 6'],
  arrow: ['M5 12h14m-5-5 5 5-5 5'],
  chevron: ['m9 5 7 7-7 7'],
  down: ['m6 9 6 6 6-6'],
  sun: ['M12 3V1m0 22v-2M3 12H1m22 0h-2M5.6 5.6 4.2 4.2m15.6 15.6-1.4-1.4m0-12.8 1.4-1.4M4.2 19.8l1.4-1.4', 'M17 12a5 5 0 1 1-10 0 5 5 0 0 1 10 0'],
  moon: ['M21 13.3A9 9 0 0 1 10.7 3 9 9 0 1 0 21 13.3Z'],
  book: ['M12 5.5C9 3.5 5.5 3.5 2 4.5v15c3.5-1 7-1 10 1 3-2 6.5-2 10-1v-15c-3.5-1-7-1-10 1Zm0 0v15'],
  up: ['m5 15 7-7 7 7']
};
</script>

<template>
  <svg :width="size" :height="size" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false">
    <path v-for="(d, index) in paths[name] || paths.book" :key="index" :d="d" />
  </svg>
</template>
