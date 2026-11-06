export const normalize = value => (value || '').normalize('NFKC').toLocaleLowerCase();

export function prepareDocuments(documents) {
  return documents.map(document => ({ ...document,
    normalizedTitle: normalize(document.title),
    normalizedAliases: normalize(document.aliases),
    normalizedDescription: normalize(document.description),
    normalizedText: normalize(document.text)
  }));
}

export function searchDocuments(documents, query, limit = 20) {
  const parts = normalize(query).match(/[\p{Letter}\p{Number}_]+/gu) || [];
  if (!parts.length) return [];
  const phrase = parts.join(' ');
  const matchers = parts.map(part => /^[a-z0-9_]+$/.test(part)
    ? value => new RegExp(`(?:^|[^a-z0-9_])${part}`).test(value)
    : value => value.includes(part));
  const phraseMatches = /^[a-z0-9_]+$/.test(phrase) ? matchers[0] : value => value.includes(phrase);
  return documents.flatMap(document => {
    const title = document.normalizedTitle;
    const aliases = document.normalizedAliases;
    const description = document.normalizedDescription;
    const text = document.normalizedText;
    let score = title === phrase ? 100 : phraseMatches(title) ? 60 : 0;
    for (const matches of matchers) {
      if (matches(title)) score += 30;
      else if (matches(aliases)) score += 14;
      else if (matches(description)) score += 8;
      else if (matches(text)) score += 1;
      else return [];
    }
    const { normalizedTitle, normalizedAliases, normalizedDescription, normalizedText, text: fullText, ...result } = document;
    return [{ ...result, score }];
  }).sort((a, b) => b.score - a.score || a.title.localeCompare(b.title, 'zh-CN')).slice(0, limit);
}
