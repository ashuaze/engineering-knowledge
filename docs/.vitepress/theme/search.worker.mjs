import { prepareDocuments, searchDocuments } from './search-core.mjs';
import { fetchSearchIndex } from './load-search.mjs';

let documents = [];
self.onmessage = async ({ data }) => {
  if (data.type === 'load') {
    try {
      const index = await fetchSearchIndex(data.url);
      if (index.version !== 1 || !Array.isArray(index.documents)) throw new Error('Invalid index');
      documents = prepareDocuments(index.documents);
      self.postMessage({ type: 'ready' });
    } catch { self.postMessage({ type: 'error' }); }
  } else if (data.type === 'search') {
    self.postMessage({ type: 'results', id: data.id, results: searchDocuments(documents, data.query) });
  }
};
