/* Verified cover lookup for LibraryMS: only use a cover when both title and author match. */
(function () {
  'use strict';
  const resultCache = new Map();
  const STOP_WORDS = new Set(['the', 'a', 'an', 'of', 'for', 'and', 'to', 'with', 'in', 'on', 'by', 'from']);

  function cleanText(value) {
    return String(value || '').normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase()
      .replace(/&/g, ' and ').replace(/[^a-z0-9]+/g, ' ').trim().replace(/\s+/g, ' ');
  }
  function tokens(value) {
    return cleanText(value).split(' ').filter(function (token) {
      return token && !STOP_WORDS.has(token) && !/^\d+(st|nd|rd|th)?$/.test(token);
    });
  }
  function overlapScore(expected, actual) {
    const wanted = tokens(expected), found = new Set(tokens(actual));
    if (!wanted.length || !found.size) return 0;
    return wanted.filter(function (word) { return found.has(word); }).length / wanted.length;
  }
  function titleScore(expected, actual) {
    const wanted = cleanText(expected), found = cleanText(actual);
    if (!wanted || !found) return 0;
    if (wanted === found) return 1;
    if (found.includes(wanted)) return 0.99;
    const score = overlapScore(expected, actual);
    if (tokens(actual).length < Math.max(2, tokens(expected).length * 0.65)) return score * 0.75;
    return score;
  }
  function authorScore(expected, actual) {
    const wanted = cleanText(expected), found = cleanText(actual);
    if (!wanted || !found) return 0;
    if (wanted === found || found.includes(wanted)) return 1;
    return overlapScore(expected, actual);
  }
  function normalizeImageUrl(url) {
    if (!url) return '';
    const normalized = String(url).replace(/^http:\/\//i, 'https://');
    try {
      const parsed = new URL(normalized, window.location.href);
      if (parsed.protocol !== 'https:' && parsed.origin !== window.location.origin) return '';
      return parsed.href;
    } catch (_error) { return ''; }
  }
  function storedCoverUrl(value) {
    const cover = String(value || '').trim();
    if (!cover) return '';
    if (/^https?:\/\//i.test(cover)) return normalizeImageUrl(cover);
    let relative = cover.replace(/\\/g, '/').replace(/^\/+/, '');
    relative = relative.replace(/^static\/books\//i, '').replace(/^books\//i, '');
    if (relative.split('/').some(function (part) { return !part || part === '.' || part === '..'; })) return '';
    return '/static/books/' + relative.split('/').map(encodeURIComponent).join('/');
  }
  function volumeIsbnMatch(volumeInfo, expectedIsbn) {
    const expected = String(expectedIsbn || '').replace(/[^0-9X]/gi, '').toUpperCase();
    if (!expected) return false;
    return (volumeInfo.industryIdentifiers || []).some(function (item) {
      return String(item.identifier || '').replace(/[^0-9X]/gi, '').toUpperCase() === expected;
    });
  }
  function bestGoogleCandidate(data, title, author, isbn) {
    const items = data && Array.isArray(data.items) ? data.items : [];
    const candidates = [];
    items.forEach(function (item) {
      const info = item.volumeInfo || {};
      const authors = (info.authors || []).join(', ');
      const ts = titleScore(title, info.title || ''), as = authorScore(author, authors);
      const imageLinks = info.imageLinks || {};
      const imageUrl = normalizeImageUrl(imageLinks.extraLarge || imageLinks.large || imageLinks.medium || imageLinks.small || imageLinks.thumbnail || imageLinks.smallThumbnail || '');
      if (ts >= 0.76 && as >= 0.5 && imageUrl) {
        candidates.push({ url: imageUrl, title: info.title || '', authors: authors, source: 'Google Books', isbnMatch: volumeIsbnMatch(info, isbn),
          sourceUrl: normalizeImageUrl(info.infoLink || 'https://books.google.com/'),
          score: ts * 0.68 + as * 0.32 + (volumeIsbnMatch(info, isbn) ? 0.12 : 0) });
      }
    });
    candidates.sort(function (a, b) { return b.score - a.score; });
    return candidates[0] || null;
  }
  async function queryGoogleBooks(query, title, author, isbn) {
    const params = new URLSearchParams({ q: query, maxResults: '10', printType: 'books', projection: 'full' });
    const response = await fetch('https://www.googleapis.com/books/v1/volumes?' + params.toString(), { headers: { Accept: 'application/json' } });
    if (!response.ok) throw new Error('Google Books request failed');
    return bestGoogleCandidate(await response.json(), title, author, isbn);
  }
  async function searchGoogleBooks(title, author, isbn) {
    // Prefer the exact edition when an ISBN is present, then use title + author as fallback.
    const normalizedIsbn = String(isbn || '').replace(/[^0-9X]/gi, '').toUpperCase();
    if (normalizedIsbn) {
      try {
        const exactEdition = await queryGoogleBooks('isbn:' + normalizedIsbn, title, author, normalizedIsbn);
        if (exactEdition && volumeHasExactIsbn(exactEdition)) return exactEdition;
      } catch (_error) { /* title-and-author search below is the safe fallback */ }
    }
    return queryGoogleBooks('intitle:"' + title + '" inauthor:"' + author + '"', title, author, normalizedIsbn);
  }
  function volumeHasExactIsbn(candidate) {
    return Boolean(candidate && candidate.isbnMatch);
  }
  function bestOpenLibraryCandidate(data, title, author) {
    const docs = data && Array.isArray(data.docs) ? data.docs : [];
    const candidates = [];
    docs.forEach(function (item) {
      const authors = (item.author_name || []).join(', ');
      const ts = titleScore(title, item.title || ''), as = authorScore(author, authors);
      if (ts >= 0.76 && as >= 0.5 && item.cover_i) {
        candidates.push({ url: 'https://covers.openlibrary.org/b/id/' + encodeURIComponent(item.cover_i) + '-L.jpg',
          title: item.title || '', authors: authors, source: 'Open Library',
          sourceUrl: 'https://openlibrary.org/search?q=' + encodeURIComponent(title + ' ' + author), score: ts * 0.68 + as * 0.32 });
      }
    });
    candidates.sort(function (a, b) { return b.score - a.score; });
    return candidates[0] || null;
  }
  async function searchOpenLibrary(title, author) {
    const params = new URLSearchParams({ title: title, author: author, limit: '10', fields: 'title,author_name,cover_i,isbn' });
    const response = await fetch('https://openlibrary.org/search.json?' + params.toString(), { headers: { Accept: 'application/json' } });
    if (!response.ok) throw new Error('Open Library request failed');
    return bestOpenLibraryCandidate(await response.json(), title, author);
  }
  async function findMatchingCover(title, author, isbn) {
    const key = [cleanText(title), cleanText(author), String(isbn || '').replace(/[^0-9X]/gi, '')].join('|');
    if (resultCache.has(key)) return resultCache.get(key);
    const task = (async function () {
      if (!title || !author) return null;
      try { const result = await searchGoogleBooks(title, author, isbn); if (result) return result; } catch (_error) { /* use fallback */ }
      try { const result = await searchOpenLibrary(title, author); if (result) return result; } catch (_error) { /* unavailable/offline */ }
      return null;
    })();
    resultCache.set(key, task);
    return task;
  }
  function showCover(img, url) {
    return new Promise(function (resolve) {
      if (!img || !url) return resolve(false);
      const probe = new Image();
      probe.onload = function () {
        img.src = url;
        img.style.display = 'block';
        const placeholder = img.nextElementSibling;
        if (placeholder && (placeholder.classList.contains('book-cover-placeholder') || placeholder.classList.contains('book-detail-cover-placeholder'))) placeholder.style.display = 'none';
        resolve(true);
      };
      probe.onerror = function () { resolve(false); };
      probe.referrerPolicy = 'no-referrer-when-downgrade';
      probe.src = url;
    });
  }
  async function loadCatalogCovers() {
    const images = Array.from(document.querySelectorAll('.book-cover-auto'));
    let cursor = 0;
    async function worker() {
      while (cursor < images.length) {
        const img = images[cursor++], initial = storedCoverUrl(img.dataset.cover || '');
        if (initial && await showCover(img, initial)) continue;
        const match = await findMatchingCover(img.dataset.title || '', img.dataset.author || '', img.dataset.isbn || '');
        if (match) await showCover(img, match.url);
      }
    }
    await Promise.all(Array.from({ length: Math.min(4, images.length) }, worker));
  }
  function setPreview(form, url) {
    const preview = form.querySelector('.cover-editor-preview');
    if (!preview) return;
    preview.hidden = true;
    preview.onload = null;
    preview.onerror = null;
    if (!url) { preview.removeAttribute('src'); return; }
    preview.onload = function () { preview.hidden = false; };
    preview.onerror = function () { preview.hidden = true; };
    preview.src = url;
  }
  function showStatus(form, message, className) {
    const status = form.querySelector('.cover-search-status');
    if (!status) return;
    status.textContent = message;
    status.className = 'cover-search-status small mt-2 ' + (className || 'text-muted');
  }
  function initializeCoverEditor(form) {
    const titleInput = form.querySelector('[name="title"]'), authorInput = form.querySelector('[name="author"]');
    const isbnInput = form.querySelector('[name="isbn"]'), coverValue = form.querySelector('.cover-image-value');
    const removeValue = form.querySelector('.remove-cover-value'), fileInput = form.querySelector('.cover-file-input');
    const findButton = form.querySelector('.find-book-cover'), clearButton = form.querySelector('.clear-book-cover');
    if (!titleInput || !authorInput || !coverValue || !findButton) return;
    if (storedCoverUrl(coverValue.value)) setPreview(form, storedCoverUrl(coverValue.value));
    if (fileInput) fileInput.addEventListener('change', function () {
      const file = fileInput.files && fileInput.files[0];
      if (!file) return;
      if (!/^image\/(jpeg|png|webp)$/.test(file.type) || file.size > 5 * 1024 * 1024) {
        fileInput.value = ''; showStatus(form, 'Choose a JPG, PNG, or WEBP image no larger than 5 MB.', 'text-danger'); return;
      }
      if (removeValue) removeValue.value = '0';
      setPreview(form, URL.createObjectURL(file));
      showStatus(form, 'Your uploaded cover will be saved with this book.', 'text-success');
    });
    findButton.addEventListener('click', async function () {
      const title = titleInput.value.trim(), author = authorInput.value.trim();
      if (!title || !author) { showStatus(form, 'Enter the book title and author before searching.', 'text-danger'); return; }
      findButton.disabled = true; showStatus(form, 'Searching book catalogs and checking the title and author…', 'text-muted');
      try {
        const match = await findMatchingCover(title, author, isbnInput ? isbnInput.value.trim() : '');
        if (!match) { showStatus(form, 'No sufficiently matching cover was found. Upload the exact front cover manually.', 'text-warning'); return; }
        const preview = form.querySelector('.cover-editor-preview');
        const loaded = await showCover(preview, match.url);
        if (!loaded) { showStatus(form, 'A catalog entry matched, but its cover image could not load. The saved selection was not changed; upload the exact cover manually.', 'text-warning'); return; }
        if (fileInput) fileInput.value = '';
        coverValue.value = match.url;
        if (removeValue) removeValue.value = '0';
        preview.hidden = false;
        showStatus(form, 'Matched “' + match.title + '” by ' + match.authors + ' — ' + match.source + '. Check the preview before saving.', 'text-success');
      } finally { findButton.disabled = false; }
    });
    if (clearButton) clearButton.addEventListener('click', function () {
      if (fileInput) fileInput.value = '';
      coverValue.value = '';
      if (removeValue) removeValue.value = '1';
      setPreview(form, '');
      showStatus(form, 'The saved cover will be removed. If an exact online match is available, the public page can still show it.', 'text-muted');
    });
  }
  document.addEventListener('DOMContentLoaded', function () {
    loadCatalogCovers();
    document.querySelectorAll('.cover-search-form').forEach(initializeCoverEditor);
  });
  window.LibraryBookCovers = { findMatchingCover: findMatchingCover };
})();
