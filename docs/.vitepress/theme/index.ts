import DefaultTheme from 'vitepress/theme-without-fonts';
import Layout from './Layout.vue';
import ArticleMeta from './components/ArticleMeta.vue';
import KnowledgeHome from './components/KnowledgeHome.vue';
import './tokens.css';
import './style.css';

export default {
  extends: DefaultTheme,
  Layout,
  enhanceApp({ app }) {
    app.component('ArticleMeta', ArticleMeta);
    app.component('KnowledgeHome', KnowledgeHome);
  }
};
