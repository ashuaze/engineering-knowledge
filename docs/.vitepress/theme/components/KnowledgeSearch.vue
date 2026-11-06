<script setup>
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue';
import { useRoute, withBase } from 'vitepress';
import ThemeIcon from './ThemeIcon.vue';

const dialog = ref();
const input = ref();
const query = ref('');
const state = ref('idle');
const results = ref([]);
const searching = ref(false);
const route = useRoute();
let worker;
let fallbackDocuments;
let fallbackSearch;
let trigger;
let restoreFocus = true;
let requestId = 0;
let searchTimer;
let loading;
let disposed = false;
const hasQuery = computed(() => query.value.trim().length > 0);

function runSearch() {
  clearTimeout(searchTimer);
  const id = ++requestId;
  searching.value = !!query.value.trim();
  if (state.value !== 'ready') return;
  searchTimer = setTimeout(() => {
    if (worker) worker.postMessage({ type: 'search', id, query: query.value });
    else if (fallbackSearch) { results.value = fallbackSearch(fallbackDocuments, query.value); searching.value = false; }
  }, 80);
}

async function fallback() {
  worker?.terminate();
  worker = undefined;
  try {
    const [loader, search] = await Promise.all([import('../load-search.mjs'), import('../search-core.mjs')]);
    const index = await loader.fetchSearchIndex(withBase('/search-index.json'));
    if (index.version !== 1 || !Array.isArray(index.documents)) throw new Error('Invalid index');
    if (disposed) return;
    fallbackDocuments = search.prepareDocuments(index.documents);
    fallbackSearch = search.searchDocuments;
    state.value = 'ready';
    runSearch();
  } catch { if (!disposed) state.value = 'error'; }
}

function loadSearch() {
  if (state.value === 'loading' || state.value === 'ready') return;
  state.value = 'loading';
  results.value = [];
  try {
    worker?.terminate();
    worker = new Worker(new URL('../search.worker.mjs', import.meta.url), { type: 'module' });
    worker.onmessage = ({ data }) => {
      if (data.type === 'ready') { state.value = 'ready'; runSearch(); }
      else if (data.type === 'results' && data.id === requestId) { results.value = data.results; searching.value = false; }
      else if (data.type === 'error') state.value = 'error';
    };
    worker.onerror = () => { loading = fallback(); };
    worker.postMessage({ type: 'load', url: new URL(withBase('/search-index.json'), location.href).href });
  } catch { loading = fallback(); }
}

async function openSearch() {
  if (dialog.value?.open) return;
  trigger = document.activeElement;
  restoreFocus = true;
  dialog.value.showModal();
  document.documentElement.classList.add('has-dialog');
  await nextTick();
  input.value?.focus();
  loadSearch();
}

function closeSearch(restore = true) {
  restoreFocus = restore;
  dialog.value?.close();
}

function afterClose() {
  if (!document.querySelector('dialog[open]')) document.documentElement.classList.remove('has-dialog');
  if (restoreFocus && trigger?.isConnected) trigger.focus({ preventScroll: true });
}

function backdrop(event) {
  if (event.target !== dialog.value) return;
  const box = dialog.value.getBoundingClientRect();
  if (event.clientX < box.left || event.clientX > box.right || event.clientY < box.top || event.clientY > box.bottom) closeSearch();
}

function keys(event) {
  if (event.key === 'Escape') { event.preventDefault(); closeSearch(); return; }
  if (!['ArrowDown', 'ArrowUp'].includes(event.key) || !results.value.length) return;
  const links = [...dialog.value.querySelectorAll('.search-result')];
  const current = links.indexOf(document.activeElement);
  const next = event.key === 'ArrowDown' ? Math.min(current + 1, links.length - 1) : current - 1;
  event.preventDefault();
  if (next < 0) input.value?.focus();
  else links[next]?.focus();
}

function hotkey(event) {
  const editing = event.target instanceof HTMLElement && (event.target.isContentEditable || /INPUT|TEXTAREA|SELECT/.test(event.target.tagName));
  if (((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === 'k') || (event.key === '/' && !editing && !event.altKey && !event.ctrlKey && !event.metaKey)) {
    event.preventDefault();
    openSearch();
  }
}

watch(query, () => { results.value = []; runSearch(); });
watch(() => route.path, () => closeSearch(false));
onMounted(() => {
  window.addEventListener('keydown', hotkey);
  window.addEventListener('fieldnotes:search', openSearch);
});
onBeforeUnmount(() => {
  disposed = true;
  worker?.terminate();
  clearTimeout(searchTimer);
  window.removeEventListener('keydown', hotkey);
  window.removeEventListener('fieldnotes:search', openSearch);
  document.documentElement.classList.remove('has-dialog');
});
</script>

<template>
  <button class="search-trigger" type="button" aria-label="搜索知识库" aria-haspopup="dialog" @click="openSearch">
    <ThemeIcon name="search" :size="18" /><span>搜索知识库</span><kbd>Ctrl K</kbd>
  </button>
  <ClientOnly>
    <Teleport to="body">
      <dialog ref="dialog" class="knowledge-search" aria-labelledby="search-heading" @close="afterClose" @cancel.prevent="closeSearch()" @click="backdrop" @keydown="keys">
        <header class="search-heading">
          <h2 id="search-heading">搜索知识库</h2>
          <button class="icon-button" type="button" aria-label="关闭搜索" @click="closeSearch()"><ThemeIcon name="close" /></button>
        </header>
        <form class="search-form" role="search" @submit.prevent>
          <ThemeIcon name="search" />
          <label class="visually-hidden" for="knowledge-query">搜索文章、概念与术语</label>
          <input id="knowledge-query" ref="input" v-model="query" type="search" placeholder="搜索概念、术语或工程问题" autocomplete="off" spellcheck="false" maxlength="100" />
          <button v-if="query" type="button" class="icon-button" aria-label="清空搜索" @click="query = ''; input?.focus()"><ThemeIcon name="close" :size="16" /></button>
        </form>
        <div class="search-body" :aria-busy="state === 'loading'">
          <p v-if="state === 'loading'" class="search-message" role="status">正在准备搜索，请稍候…</p>
          <div v-else-if="state === 'error'" class="search-message" role="alert">
            <p>搜索暂时无法加载，请重试。</p>
            <button class="text-button" type="button" @click="loadSearch">重新加载</button>
            <a :href="withBase('/articles.html')" @click="closeSearch(false)">前往文章目录</a>
          </div>
          <p v-else-if="!hasQuery" class="search-message">支持中文、英文和术语缩写。试试“幂等性”“重试预算”或“RAG”。</p>
          <template v-else>
            <p class="search-result-count" role="status">{{ searching ? '正在查找…' : results.length ? `找到 ${results.length} 个相关结果` : '没有找到相关内容，试试其他中文术语或英文名称。' }}</p>
            <ul class="search-results">
              <li v-for="result in results" :key="result.url">
                <a class="search-result" :href="withBase(result.url)" @click="closeSearch(false)">
                  <span class="result-context">{{ result.domain }}<span aria-hidden="true"> · </span>{{ result.kind }}</span>
                  <span class="result-title">{{ result.title }}</span>
                  <span class="result-description">{{ result.description }}</span>
                </a>
              </li>
            </ul>
          </template>
        </div>
        <footer class="search-footer"><span><kbd>↑</kbd> <kbd>↓</kbd> 选择结果</span><span><kbd>Enter</kbd> 打开</span><span><kbd>Esc</kbd> 关闭</span></footer>
      </dialog>
    </Teleport>
  </ClientOnly>
</template>
