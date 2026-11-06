// An explicitly compressed binary keeps static hosts from needing custom HTTP headers.
// Browsers without streaming decompression retain the plain-JSON path.
export async function fetchSearchIndex(url) {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 15000);
  try {
    const compressed = typeof DecompressionStream === 'function';
    let response = await fetch(compressed ? url.replace(/\.json$/, '.bin') : url, {
      cache: 'no-cache', signal: controller.signal
    });
    if (compressed && response.status === 404) {
      response = await fetch(url, { cache: 'no-cache', signal: controller.signal });
      if (!response.ok) throw new Error('Search unavailable');
      return await response.json();
    }
    if (!response.ok) throw new Error('Search unavailable');
    return compressed
      ? await new Response(response.body.pipeThrough(new DecompressionStream('gzip'))).json()
      : await response.json();
  } finally { clearTimeout(timeout); }
}
