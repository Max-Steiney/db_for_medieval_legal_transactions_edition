/* eslint-disable no-console */
/**
 * Wiener Urkundenbuch — Edition Verify (Browser-Konsole)
 *
 * Benutzung:
 *   1. Eine beliebige Top-Level-Seite der Edition im Browser öffnen
 *      (z.B. index.html, persons.html, statistics.html).
 *   2. DevTools öffnen (F12) und in die Konsole wechseln.
 *   3. Diesen gesamten Dateiinhalt kopieren und mit Enter ausführen.
 *   4. Nach ~30–60 Sekunden erscheint am Ende eine Übersichts-Tabelle.
 *
 * Prüfungen:
 *   1. Alle 11 data/*.json + 3 register/*.json laden und parsen.
 *   2. Konsistenz: statistics.totalDocs == search.json.length == docs_lookup keys.
 *   3. Keine Referenzen auf entfernte Kollektionen (Stale-Refs).
 *   4. Zufällige Drilldown-file_keys lösen auf erreichbare Dokumenten-URLs auf.
 *   5. TEI-Download-Links in Dokumentenseiten zeigen auf erreichbare .xml-Dateien.
 *   6. Register-Search-JSONs enthalten Einträge mit Dokumentverweisen (dc > 0).
 *   7. Alle Top-Level-HTMLs sind erreichbar.
 *
 * Rückgabe: { pass, fail, warn, results } als console.table am Ende.
 * Das Snippet läuft read-only (nur HEAD/GET-Requests, kein State-Change).
 */

(async () => {
  const style = {
    head: 'font-weight:bold;color:#5af;font-size:13px',
    pass: 'background:#0a7a2f;color:#fff;padding:1px 6px;border-radius:2px',
    fail: 'background:#b21f1f;color:#fff;padding:1px 6px;border-radius:2px',
    warn: 'background:#c67a00;color:#fff;padding:1px 6px;border-radius:2px',
    dim:  'color:#999',
  };
  const log  = (t, ...a) => console.log(`%c${t}`, style.head, ...a);
  const pass = (t, ...a) => console.log(`%cPASS%c ${t}`, style.pass, '', ...a);
  const fail = (t, ...a) => console.log(`%cFAIL%c ${t}`, style.fail, '', ...a);
  const warn = (t, ...a) => console.log(`%cWARN%c ${t}`, style.warn, '', ...a);

  const results = [];
  const record = (section, target, status, detail = '') =>
    results.push({ section, target, status, detail });

  // Basis-URL: aktuelles Verzeichnis (letztes path-Segment entfernt, falls Datei)
  const base = location.origin + location.pathname.replace(/[^/]*$/, '');
  log(`Edition Verify @ ${base}`);

  const fetchJson = async (rel) => {
    const r = await fetch(base + rel, { cache: 'no-cache' });
    if (!r.ok) throw new Error(`${r.status} ${r.statusText}`);
    return r.json();
  };
  const fetchText = async (rel) => {
    const r = await fetch(base + rel, { cache: 'no-cache' });
    if (!r.ok) throw new Error(`${r.status} ${r.statusText}`);
    return r.text();
  };
  const headOk = async (rel) => {
    try {
      const r = await fetch(base + rel, { method: 'HEAD', cache: 'no-cache' });
      return r.ok;
    } catch { return false; }
  };
  const pickRandom = (arr, n) => {
    const src = [...arr];
    const out = [];
    for (let i = 0; i < n && src.length; i++) {
      const idx = Math.floor(Math.random() * src.length);
      out.push(src.splice(idx, 1)[0]);
    }
    return out;
  };

  // ========== 1. JSON loadability ==========
  log('1. JSON loadability');
  const jsons = {};
  const jsonPaths = [
    'data/docs_lookup.json', 'data/epic_a.json', 'data/epic_b.json',
    'data/epic_c.json', 'data/epic_d.json', 'data/organisations_search.json',
    'data/persons_search.json', 'data/places_search.json', 'data/quality.json',
    'data/search.json', 'data/timeline.json',
    'register/organisations.json', 'register/persons.json', 'register/places.json',
  ];
  for (const p of jsonPaths) {
    try {
      const t0 = performance.now();
      jsons[p] = await fetchJson(p);
      const ms = Math.round(performance.now() - t0);
      pass(`${p} (${ms}ms)`);
      record('json-load', p, 'pass', `${ms}ms`);
    } catch (e) {
      fail(`${p}: ${e.message}`);
      record('json-load', p, 'fail', e.message);
    }
  }

  // ========== 2. Consistency ==========
  log('2. Konsistenz');
  try {
    const statsHtml = await fetchText('statistics.html');
    const m = statsHtml.match(/<script id="stats-data"[^>]*>([\s\S]+?)<\/script>/);
    if (!m) throw new Error('stats-data Script nicht gefunden in statistics.html');
    const stats = JSON.parse(m[1]);
    const totalDocs = stats.summary.totalDocs;
    const searchLen = (jsons['data/search.json'] || []).length;
    const lookupLen = Object.keys(jsons['data/docs_lookup.json'] || {}).length;

    // Strikt: totalDocs muss zu search.json passen (beide kommen aus demselben Build-Step)
    const statsSearchMatch = totalDocs === searchLen;
    (statsSearchMatch ? pass : fail)(
      `totalDocs=${totalDocs} vs search.length=${searchLen} ${statsSearchMatch ? 'ok' : 'MISMATCH'}`
    );
    record('consistency', 'stats vs search', statsSearchMatch ? 'pass' : 'fail',
      `stats=${totalDocs}, search=${searchLen}`);

    // Weich: docs_lookup ist sekundärer Index. Kleine Abweichungen melden als WARN.
    const lookupDelta = Math.abs(totalDocs - lookupLen);
    const lookupPctDelta = totalDocs > 0 ? lookupDelta / totalDocs : 1;
    if (lookupLen === totalDocs) {
      pass(`docs_lookup.keys=${lookupLen} == totalDocs`);
      record('consistency', 'lookup vs stats', 'pass', `${lookupLen}=${totalDocs}`);
    } else if (lookupPctDelta < 0.01) {
      warn(`docs_lookup.keys=${lookupLen} vs totalDocs=${totalDocs} (Δ=${lookupDelta}, ${(lookupPctDelta*100).toFixed(2)}%)`);
      record('consistency', 'lookup vs stats', 'warn', `${lookupLen} vs ${totalDocs} (Δ=${lookupDelta})`);
    } else {
      fail(`docs_lookup.keys=${lookupLen} vs totalDocs=${totalDocs} (Δ=${lookupDelta}, ${(lookupPctDelta*100).toFixed(1)}%)`);
      record('consistency', 'lookup vs stats', 'fail', `${lookupLen} vs ${totalDocs} (Δ=${lookupDelta})`);
    }

    // Stale-Collections-Check
    const stale = /Gewerbuch_D|Satzbuch_CD|Copeybuch_Zeibig|Widmerliste|Genanntenliste_Stubenviertel|GenanntenListe_Weinzettel|test_ready/;
    const staleHits = stats.collections.map(c => c.path).filter(p => stale.test(p));
    (staleHits.length === 0 ? pass : fail)(
      `stale collections in stats: ${staleHits.length === 0 ? 'keine' : staleHits.join(', ')}`
    );
    record('consistency', 'stale refs', staleHits.length === 0 ? 'pass' : 'fail',
      staleHits.join(',') || 'keine');
  } catch (e) {
    fail(`statistics.html Parse: ${e.message}`);
    record('consistency', 'statistics.html', 'fail', e.message);
  }

  // ========== 3. Drilldown file_keys -> documents ==========
  log('3. Drilldown-Ziele (Stichprobe 30)');
  const lookup = jsons['data/docs_lookup.json'] || {};
  const fkeySet = new Set();
  const collectFkeys = (obj) => {
    if (Array.isArray(obj)) {
      for (const x of obj) if (typeof x === 'string' && x.startsWith('f__')) fkeySet.add(x);
    } else if (obj && typeof obj === 'object') {
      for (const v of Object.values(obj)) collectFkeys(v);
    }
  };
  for (const ep of ['data/epic_a.json', 'data/epic_b.json', 'data/epic_c.json', 'data/epic_d.json']) {
    if (jsons[ep]) collectFkeys(jsons[ep]);
  }
  const fkeys = [...fkeySet];
  log(`   unique file_keys referenced in epic_a..d: ${fkeys.length}`);
  const sample = pickRandom(fkeys, Math.min(30, fkeys.length));
  let ok = 0, missing = 0, notFound = 0;
  for (const fk of sample) {
    const entry = lookup[fk];
    if (!entry) { missing++; warn(`${fk}: fehlt in docs_lookup`); continue; }
    if (await headOk(entry.u)) ok++;
    else { notFound++; fail(`${fk} → ${entry.u}: 404`); }
  }
  (notFound === 0 ? pass : fail)(
    `Drilldown-Stichprobe: ${ok}/${sample.length} ok, ${missing} ohne lookup-Eintrag, ${notFound} 404`
  );
  record('drilldowns', `sample ${sample.length}`, notFound === 0 ? 'pass' : 'fail',
    `ok=${ok}, missing=${missing}, 404=${notFound}`);

  // ========== 4. TEI download targets (sample 10) ==========
  log('4. TEI-Download-Targets (Stichprobe 10)');
  const search = jsons['data/search.json'] || [];
  const teiSample = pickRandom(search, Math.min(10, search.length));
  let teiOk = 0, teiNoBtn = 0, tei404 = 0;
  for (const doc of teiSample) {
    try {
      const html = await fetchText(doc.u);
      const m = html.match(/<a[^>]*class="toolbar-btn"[^>]*href="([^"]*tei[^"]*\.xml)"/);
      if (!m) { teiNoBtn++; warn(`${doc.u}: kein TEI-Button`); continue; }
      // Resolve href relative to document URL
      const docBase = base + doc.u.replace(/[^/]*$/, '');
      const teiAbs = new URL(m[1], docBase).href;
      // teiAbs must be under base
      const teiRel = teiAbs.replace(base, '');
      if (await headOk(teiRel)) teiOk++;
      else { tei404++; fail(`${doc.u} → ${teiRel}: 404`); }
    } catch (e) {
      tei404++;
      fail(`${doc.u}: ${e.message}`);
    }
  }
  (tei404 === 0 ? pass : fail)(
    `TEI-Stichprobe: ${teiOk}/${teiSample.length} ok, ${teiNoBtn} ohne Button, ${tei404} 404`
  );
  record('tei', `sample ${teiSample.length}`, tei404 === 0 ? 'pass' : 'fail',
    `ok=${teiOk}, noBtn=${teiNoBtn}, 404=${tei404}`);

  // ========== 5. Register reverse references ==========
  log('5. Register (Dokumentverweise)');
  for (const reg of ['persons', 'organisations', 'places']) {
    const arr = jsons[`data/${reg}_search.json`] || [];
    const withDocs = arr.filter(x => (x.dc || 0) > 0).length;
    const total = arr.length;
    const pct = total ? Math.round(withDocs / total * 100) : 0;
    const ok = withDocs > 0 && total > 0;
    (ok ? pass : fail)(`${reg}: ${withDocs}/${total} mit dc>0 (${pct}%)`);
    record('register', reg, ok ? 'pass' : 'fail', `${withDocs}/${total}`);
  }

  // ========== 6. Top-level navigation ==========
  log('6. Navigation');
  const pages = [
    'about.html', 'documents.html', 'edition_guidelines.html',
    'exploration.html', 'exploration_networks.html', 'exploration_places.html',
    'exploration_roles.html', 'exploration_transactions.html',
    'index.html', 'organisations.html', 'persons.html', 'places.html',
    'quality.html', 'impressum.html', 'statistics.html', 'vault.html',
  ];
  let navOk = 0, navFail = 0;
  for (const p of pages) {
    if (await headOk(p)) { navOk++; }
    else { navFail++; fail(`${p}`); }
  }
  (navFail === 0 ? pass : fail)(`Navigation: ${navOk}/${pages.length} erreichbar`);
  record('navigation', `${pages.length} pages`, navFail === 0 ? 'pass' : 'fail',
    `ok=${navOk}, 404=${navFail}`);

  // ========== Summary ==========
  log('===== Zusammenfassung =====');
  const byStatus = results.reduce((acc, r) => { acc[r.status] = (acc[r.status] || 0) + 1; return acc; }, {});
  console.table(results);
  log(`Total: ${byStatus.pass || 0} pass · ${byStatus.warn || 0} warn · ${byStatus.fail || 0} fail`);
  return { pass: byStatus.pass || 0, warn: byStatus.warn || 0, fail: byStatus.fail || 0, results };
})();
