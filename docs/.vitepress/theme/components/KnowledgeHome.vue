<script setup>
import { computed } from 'vue';
import { useData, withBase } from 'vitepress';
import ThemeIcon from './ThemeIcon.vue';

const { theme } = useData();
const library = computed(() => theme.value.fieldnotes);
const questions = [
  { title: '客户端超时了，订单到底有没有创建？', topic: 'API · 幂等性', url: '/knowledge/api/idempotency.html' },
  { title: '写了 async，为什么其他请求仍然卡住？', topic: 'Runtime · 执行与等待', url: '/knowledge/runtime/async-and-blocking.html' },
  { title: '业务表已提交，消息却没有发出去？', topic: '消息 · 事务边界', url: '/knowledge/messaging/transactional-outbox.html' },
  { title: 'Agent 重启后，如何判断工具是否执行成功？', topic: 'AI · 状态与恢复', url: '/knowledge/ai/recoverable-runtime.html' }
];
const paths = [
  { title: '请求处理基础', description: '沿一次请求理解系统边界', anchor: 'a-请求处理基础-解释一个请求' },
  { title: '生产可靠性', description: '解释失败、观测与恢复', anchor: 'b-生产可靠性-把失败边界画出来' },
  { title: 'AI 应用与 Agent', description: '从上下文到可恢复执行', anchor: 'c-ai-应用与-agent-从上下文到可恢复执行' },
  { title: '浏览器交互', description: '理解渲染、状态与响应', anchor: 'd-浏览器交互-解释一次点击为什么迟到' }
];
function search() { window.dispatchEvent(new Event('fieldnotes:search')); }
</script>

<template>
  <div class="knowledge-home">
    <section class="home-intro" aria-labelledby="home-title">
      <h1 id="home-title">工程知识库</h1>
      <p class="home-thesis">理解原理，解释故障，<br class="mobile-break" />做出有依据的工程取舍。</p>
      <p class="home-description">从一个实际问题出发，读懂机制、失败边界与技术取舍。面向软件开发、测试、运维、数据与 AI 工程的中文阅读笔记。</p>
      <button type="button" class="home-search" aria-label="搜索知识库" aria-haspopup="dialog" @click="search"><ThemeIcon name="search" /><span>搜索概念、术语或工程问题</span><kbd>/</kbd></button>
      <p class="home-scope">{{ library.articleCount }} 篇正文<span>·</span>{{ library.domains.length }} 个领域<span>·</span>{{ library.termCount }} 组术语</p>
      <nav class="home-shortcuts" aria-label="主要阅读入口">
        <a :href="withBase('/problems.html')">问题导航<ThemeIcon name="arrow" :size="16" /></a>
        <a :href="withBase('/paths/')">学习路径<ThemeIcon name="arrow" :size="16" /></a>
        <a :href="withBase('/glossary/')">分类词汇表<ThemeIcon name="arrow" :size="16" /></a>
        <a :href="withBase('/articles.html')">全部文章<ThemeIcon name="arrow" :size="16" /></a>
      </nav>
    </section>
    <div class="home-reading-grid">
      <section id="建议先读" aria-labelledby="questions-title" class="home-questions">
        <h2 id="questions-title">从正在遇到的问题开始</h2>
        <ul>
          <li v-for="question in questions" :key="question.url"><a :href="withBase(question.url)"><span class="question-title">{{ question.title }}<ThemeIcon name="arrow" :size="18" /></span><span class="question-topic">{{ question.topic }}</span></a></li>
        </ul>
      </section>
      <section aria-labelledby="paths-title" class="home-paths">
        <h2 id="paths-title">沿一条路线读下去</h2>
        <ul>
          <li v-for="item in paths" :key="item.anchor"><a :href="withBase(`/paths/#${item.anchor}`)"><span>{{ item.title }}</span><small>{{ item.description }}</small></a></li>
        </ul>
      </section>
    </div>
    <section aria-labelledby="domains-title" class="home-domains">
      <div class="home-section-heading"><h2 id="domains-title">按领域查阅</h2><a :href="withBase('/map.html')">知识地图<ThemeIcon name="arrow" :size="16" /></a></div>
      <ul><li v-for="domain in library.domains" :key="domain.id"><a :href="withBase(`/knowledge/${domain.id}/`)"><span>{{ domain.title }}</span><small>{{ domain.count }} 篇</small></a></li></ul>
    </section>
    <section aria-labelledby="recent-title" class="home-recent">
      <div class="home-section-heading"><h2 id="recent-title">最近更新</h2><a :href="withBase('/updates.html')">阅读更新<ThemeIcon name="arrow" :size="16" /></a></div>
      <ul><li v-for="article in library.latest" :key="article.url"><a :href="withBase(article.url)"><span>{{ article.title }}</span><time :datetime="article.updated">{{ article.updated }}</time></a></li></ul>
    </section>
    <p id="内容的使用方式" class="home-note">正文分别标注来源核查、实验与设计提案的范围。已有入口与待补机制，见<a :href="withBase('/handbook/concept-roadmap.html')">概念路线图</a>。</p>
  </div>
</template>
