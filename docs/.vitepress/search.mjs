// The same self-contained function is serialized into the browser search client.
// Overlapping Han pairs make Chinese phrases searchable without a dictionary download.
export function tokenize(text) {
  const normalized = text.normalize('NFKC').toLowerCase();
  const tokens = normalized.match(/[a-z0-9_]+/g) || [];
  for (const [run] of normalized.matchAll(/\p{Script=Han}+/gu)) {
    const chars = [...run];
    if (chars.length === 1) tokens.push(run);
    for (let i = 0; i < chars.length - 1; i++) tokens.push(chars[i] + chars[i + 1]);
  }
  return [...new Set(tokens)];
}
