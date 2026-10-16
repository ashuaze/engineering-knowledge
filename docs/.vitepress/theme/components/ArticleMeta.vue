<script setup>
import { useData } from 'vitepress';

const { frontmatter } = useData();
const kinds = { concept: '概念', comparison: '对比', pattern: '模式', case: '案例', lab: '实验', decision: '决策' };
const states = { evolving: '持续完善', reviewed: '已审阅', deprecated: '已弃用' };
const evidence = { 'source-checked': '已核查来源', tested: '随附实验已执行', 'design-proposal': '设计提案 / 教学推演' };
</script>

<template>
  <div v-if="frontmatter.id" class="article-meta" aria-label="文章信息">
    <div class="article-meta-labels">
      <span class="article-kind">{{ kinds[frontmatter.kind] }}</span>
      <span>{{ states[frontmatter.status] }}</span>
      <span>{{ evidence[frontmatter.verification] }}</span>
    </div>
    <p>
      更新 <time :datetime="frontmatter.updated">{{ frontmatter.updated }}</time>
      <span v-if="frontmatter.last_verified"> · 核查 <time :datetime="frontmatter.last_verified">{{ frontmatter.last_verified }}</time></span>
      <span v-else> · 尚无独立核查日期</span>
    </p>
  </div>
</template>
