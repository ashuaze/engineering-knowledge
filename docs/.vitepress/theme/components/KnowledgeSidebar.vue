<script setup>
import { computed } from 'vue';
import { useData, useRoute, withBase } from 'vitepress';
import ThemeIcon from './ThemeIcon.vue';

defineEmits(['navigate']);
const { theme, site } = useData();
const route = useRoute();
const groups = computed(() => Array.isArray(theme.value.sidebar) ? theme.value.sidebar : []);
const relative = computed(() => decodeURI(route.path).replace(site.value.base, '/').replace(/index\.html$/, ''));
const active = link => relative.value === decodeURI(link).replace(/index\.html$/, '');
const containsActive = group => group.items?.some(item => active(item.link));
</script>

<template>
  <nav class="knowledge-sidebar" aria-label="知识目录">
    <template v-for="(group, index) in groups" :key="group.text">
      <section v-if="group.collapsed === undefined" class="sidebar-section">
        <h2>{{ group.text }}</h2>
        <ul>
          <li v-for="item in group.items" :key="item.link">
            <a :href="withBase(item.link)" :aria-current="active(item.link) ? 'page' : undefined" @click="$emit('navigate')">{{ item.text }}</a>
          </li>
        </ul>
      </section>
      <details v-else class="sidebar-section" :open="containsActive(group)">
        <summary><span>{{ group.text }}</span><ThemeIcon name="chevron" :size="16" /></summary>
        <ul>
          <li v-for="item in group.items" :key="item.link">
            <a :href="withBase(item.link)" :aria-current="active(item.link) ? 'page' : undefined" @click="$emit('navigate')">{{ item.text }}</a>
          </li>
        </ul>
      </details>
    </template>
  </nav>
</template>
