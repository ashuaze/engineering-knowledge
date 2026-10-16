<script setup>
import DefaultTheme from 'vitepress/theme-without-fonts';
import { useData } from 'vitepress';
import ArticleMeta from './components/ArticleMeta.vue';

const { page } = useData();
</script>

<template>
  <DefaultTheme.Layout>
    <template #doc-before>
      <p v-if="page.relativePath === 'index.md'" class="fieldnotes-eyebrow">ENGINEERING FIELDNOTES</p>
      <ArticleMeta />
    </template>
  </DefaultTheme.Layout>
</template>
