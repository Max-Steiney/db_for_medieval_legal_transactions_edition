"""HTML-Reader fuer die TEI-zu-HTML-Coverage-Stufe.

Liest die gerenderten Profil- und Quellen-HTMLs unter `docs/` und
extrahiert die Werte, die der Vertrag (siehe ``contract.py``) als
Frontend-sichtbar erwartet. Spiegel zu ``parse_tei.py`` / ``parse_indices.py``
fuer die andere Seite des Vergleichs.

Der Reader nutzt ``lxml.html`` mit CSS-Selektoren, weil die Frontend-
Templates konsistente Klassennamen ausspielen (.person-name, .ph-meta-
strip, .rel-table, .person-source-table). Selektoren werden hier zentral
gehalten, damit Layout-Refactors im Frontend nur an einer Stelle
nachgezogen werden muessen.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from lxml import html as lxml_html

from verification.config import (
    HTML_DOCUMENTS,
    HTML_REGISTER_ORGS,
    HTML_REGISTER_PERSONS,
)


@dataclass
class PersonProfileHtml:
    """Was das gerenderte Personenprofil ueber eine Person sagt."""

    pe_id: str
    path: Path
    display_name: Optional[str] = None
    name_orig: Optional[str] = None
    sex_label: Optional[str] = None
    note: Optional[str] = None
    death_display: Optional[str] = None
    active_min: Optional[str] = None
    active_max: Optional[str] = None
    source_count_displayed: Optional[int] = None
    source_titles: List[str] = field(default_factory=list)
    authority_urls: List[str] = field(default_factory=list)
    wiki_url: Optional[str] = None
    # Beziehungen: pro rel_type die Anzahl der Zeilen in der Tabelle.
    relation_counts: Dict[str, int] = field(default_factory=dict)
    # Quellen-Tabelle: Liste der idno-Werte (Signaturen) als Anker fuer
    # die Pruefung "alle Belege werden gerendert".
    source_idnos: List[str] = field(default_factory=list)
    # Roh-Listen fuer "Beziehungs-Partner pro Typ" — IDs aus den Links.
    relation_partner_ids: Dict[str, List[str]] = field(default_factory=dict)


@dataclass
class OrgProfileHtml:
    """Was das gerenderte Organisations-Profil ueber eine Org sagt."""

    org_id: str
    path: Path
    name: Optional[str] = None
    type_label: Optional[str] = None
    observance: Optional[str] = None
    active_min: Optional[str] = None
    active_max: Optional[str] = None
    place_name: Optional[str] = None
    parent_org_id: Optional[str] = None
    source_count_displayed: Optional[int] = None
    source_labels: List[str] = field(default_factory=list)
    authority_urls: List[str] = field(default_factory=list)
    relation_counts: Dict[str, int] = field(default_factory=dict)
    source_idnos: List[str] = field(default_factory=list)
    children_ids: List[str] = field(default_factory=list)


def _text(el) -> str:
    if el is None:
        return ""
    return " ".join(el.text_content().split()).strip()


def _href_id(href: str, prefix: str) -> Optional[str]:
    """register/persons/pe__hans.html -> pe__hans (oder None)."""
    if not href:
        return None
    last = href.rsplit("/", 1)[-1]
    if last.endswith(".html"):
        last = last[:-5]
    if last.startswith(prefix):
        return last
    return None


def _meta_pair(tree, label: str) -> Optional[str]:
    """ph-meta-strip-Wert fuer ein dt-Label finden. Robust gegen
    Whitespace und Tooltip-Icons im dt."""
    for pair in tree.cssselect(".ph-meta-strip .ph-meta-pair"):
        dt = pair.cssselect("dt")
        dd = pair.cssselect("dd")
        if not dt or not dd:
            continue
        # dt kann ein tip_glossary-Icon enthalten — Plain-Text vergleichen.
        dt_text = _text(dt[0])
        # Vergleich auf "Label" oder "Label" + nachfolgende Tooltip-Icons.
        if dt_text == label or dt_text.startswith(label):
            return _text(dd[0])
    return None


def _rel_blocks(tree) -> List[Tuple[str, int, List[str]]]:
    """Pro .rel-block: (rel_type aus Klasse, Anzahl-Zeilen, Partner-IDs).
    rel_type kommt aus rel-block-<type>-Klasse."""
    out = []
    for block in tree.cssselect(".rel-block"):
        rel_type = None
        for cls in block.get("class", "").split():
            if cls.startswith("rel-block-") and cls != "rel-block-head":
                rel_type = cls[len("rel-block-"):]
                break
        if not rel_type:
            continue
        rows = block.cssselect("tbody > tr")
        partner_ids: List[str] = []
        for tr in rows:
            for a in tr.cssselect("a.rel-other-link, a.rel-other-link--person, a.rel-other-link--org"):
                href = a.get("href", "")
                pid = _href_id(href, "pe__") or _href_id(href, "org__")
                if pid:
                    partner_ids.append(pid)
        out.append((rel_type, len(rows), partner_ids))
    return out


def read_person_profile(path: Path) -> PersonProfileHtml:
    """Liest eine docs/register/persons/<id>.html und gibt die strukturierten
    Felder zurueck. Erwartet das Markup aus dem aktuellen person.html-Template."""
    pe_id = path.stem
    tree = lxml_html.parse(str(path)).getroot()
    p = PersonProfileHtml(pe_id=pe_id, path=path)

    name_el = tree.cssselect(".person-name")
    if name_el:
        p.display_name = _text(name_el[0])

    orig_el = tree.cssselect(".ph-subline em")
    # Erstes <em> in ph-subline ist die Quellen-Wortlaut-Form (sofern vorhanden).
    if orig_el:
        # ph-subline kann auch andere <em> enthalten, daher nur das, das nach
        # "Im Quellen-Wortlaut" steht.
        for span in tree.cssselect(".ph-subline > span"):
            label = span.cssselect(".orig-label")
            if label and "Quellen-Wortlaut" in _text(label[0]):
                em = span.cssselect("em")
                if em:
                    p.name_orig = _text(em[0])
                    break

    note_el = tree.cssselect(".person-note")
    if note_el:
        p.note = _text(note_el[0])

    p.sex_label = _meta_pair(tree, "Geschlecht")
    belegt = _meta_pair(tree, "Belegt")
    if belegt:
        # "1367–1402" oder "1404"
        if "–" in belegt or "&ndash;" in belegt:
            for sep in ("–", "–"):
                if sep in belegt:
                    parts = belegt.split(sep)
                    if len(parts) == 2:
                        p.active_min = parts[0].strip()
                        p.active_max = parts[1].strip()
                    break
        else:
            p.active_min = belegt.strip()
            p.active_max = belegt.strip()
    p.death_display = _meta_pair(tree, "Verstorben vor")
    src_count = _meta_pair(tree, "Quellen")
    if src_count and src_count.isdigit():
        p.source_count_displayed = int(src_count)

    # Genannt als ... — Chips in den person-titles-details.
    for chip in tree.cssselect(".person-titles-details .pt-chip"):
        t = _text(chip)
        if t:
            p.source_titles.append(t)

    # External Links.
    for a in tree.cssselect(".ph-subline a.ext-link"):
        href = a.get("href", "")
        label = _text(a)
        if "wienwiki" in href.lower():
            p.wiki_url = href
        else:
            p.authority_urls.append(href)

    # Beziehungs-Bloecke.
    for rel_type, count, partner_ids in _rel_blocks(tree):
        p.relation_counts[rel_type] = count
        p.relation_partner_ids[rel_type] = partner_ids

    # Quellen-Tabelle: src-col-idno Anker-Texte als Signaturen. Nur
    # tbody-Zellen zaehlen, weil der <th> die selbe Klasse traegt.
    for td in tree.cssselect(".person-source-table tbody td.src-col-idno"):
        idno = _text(td)
        if idno:
            p.source_idnos.append(idno)

    return p


def read_org_profile(path: Path) -> OrgProfileHtml:
    """Liest eine docs/register/orgs/<id>.html. Analog zu read_person_profile."""
    org_id = path.stem
    tree = lxml_html.parse(str(path)).getroot()
    o = OrgProfileHtml(org_id=org_id, path=path)

    name_el = tree.cssselect(".person-name")
    if name_el:
        o.name = _text(name_el[0])

    o.type_label = _meta_pair(tree, "Typ")
    o.observance = _meta_pair(tree, "Observanz")
    belegt = _meta_pair(tree, "Belegt")
    if belegt:
        for sep in ("–", "–"):
            if sep in belegt:
                parts = belegt.split(sep)
                if len(parts) == 2:
                    o.active_min = parts[0].strip()
                    o.active_max = parts[1].strip()
                break
        else:
            o.active_min = belegt.strip()
            o.active_max = belegt.strip()
    o.place_name = _meta_pair(tree, "Standort")
    src_count = _meta_pair(tree, "Quellen")
    if src_count and src_count.isdigit():
        o.source_count_displayed = int(src_count)

    # Parent-Org aus Meta-Strip.
    for pair in tree.cssselect(".ph-meta-strip .ph-meta-pair"):
        dt = pair.cssselect("dt")
        if dt and _text(dt[0]).startswith("Übergeordnet"):
            a = pair.cssselect("dd a")
            if a:
                href = a[0].get("href", "")
                o.parent_org_id = _href_id(href, "org__")

    for chip in tree.cssselect(".person-titles-details .pt-chip"):
        t = _text(chip)
        if t:
            o.source_labels.append(t)

    for a in tree.cssselect(".ph-subline a.ext-link"):
        o.authority_urls.append(a.get("href", ""))

    for rel_type, count, partner_ids in _rel_blocks(tree):
        o.relation_counts[rel_type] = count
        # Bei Org-Profilen sind Partner immer Personen (pe__-IDs).

    for td in tree.cssselect(".person-source-table tbody td.src-col-idno"):
        idno = _text(td)
        if idno:
            o.source_idnos.append(idno)

    # Untergeordnete Orgs.
    for a in tree.cssselect(".org-children a.child-link"):
        cid = _href_id(a.get("href", ""), "org__")
        if cid:
            o.children_ids.append(cid)

    return o


@dataclass
class DocumentHtml:
    """Was die gerenderte Quellen-Detailseite ueber ein Dokument sagt."""

    idno: str
    path: Path
    title: Optional[str] = None
    date_display: Optional[str] = None
    place_display: Optional[str] = None
    corpus_label: Optional[str] = None
    # data-ref-Werte aller annotierten Elemente im Body, deduped.
    person_refs: List[str] = field(default_factory=list)
    org_refs: List[str] = field(default_factory=list)
    place_refs: List[str] = field(default_factory=list)
    event_refs: List[str] = field(default_factory=list)


def read_document(path: Path) -> DocumentHtml:
    """Liest docs/documents/<corpus>/<sub>/<idno>.html und gibt strukturierte
    Felder zurueck. idno ist der Dateiname ohne .html."""
    idno = path.stem
    tree = lxml_html.parse(str(path)).getroot()
    d = DocumentHtml(idno=idno, path=path)

    # H1 enthaelt nur "Nr. <idno>". Der <title> im <head> hat die Form
    # "Nr. <idno> (<date_display>), Datenbank" — daraus ziehen wir das
    # Datum.
    h1 = tree.cssselect("h1")
    if h1:
        d.title = _text(h1[0])
    title_tag = tree.cssselect("head > title")
    if title_tag:
        import re
        m = re.search(r"\(([^)]+)\)", _text(title_tag[0]))
        if m:
            d.date_display = m.group(1).strip()

    for pair in tree.cssselect(".doc-toolbar-meta .meta-pair"):
        label_el = pair.cssselect(".meta-label")
        value_el = pair.cssselect(".meta-value")
        if not label_el or not value_el:
            continue
        label = _text(label_el[0])
        value = _text(value_el[0])
        if label == "Originaldatierung":
            d.place_display = value  # tatsaechlich enthaelt das oft Ort+Datum
        elif label == "Quelle":
            d.corpus_label = value

    # data-ref-Annotationen im Body: ein Eintrag pro Vorkommen, dann
    # dedupliziert pro Kategorie.
    seen_p, seen_o, seen_pl, seen_e = set(), set(), set(), set()
    for el in tree.cssselect("[data-ref]"):
        ref = el.get("data-ref", "").strip()
        if not ref:
            continue
        if ref.startswith("pe__") and ref not in seen_p:
            seen_p.add(ref)
            d.person_refs.append(ref)
        elif ref.startswith("org__") and ref not in seen_o:
            seen_o.add(ref)
            d.org_refs.append(ref)
        elif ref.startswith("pl__") and ref not in seen_pl:
            seen_pl.add(ref)
            d.place_refs.append(ref)
        elif ref.startswith("ev__") and ref not in seen_e:
            seen_e.add(ref)
            d.event_refs.append(ref)
    return d


def iter_person_profiles() -> List[Path]:
    """Alle Personen-Profil-HTMLs im docs/-Output."""
    if not HTML_REGISTER_PERSONS.exists():
        return []
    return sorted(HTML_REGISTER_PERSONS.glob("pe__*.html"))


def iter_org_profiles() -> List[Path]:
    if not HTML_REGISTER_ORGS.exists():
        return []
    return sorted(HTML_REGISTER_ORGS.glob("org__*.html"))


def iter_documents() -> List[Path]:
    """Alle Quellen-HTMLs unter docs/documents/<corpus>/<sub>/*.html."""
    if not HTML_DOCUMENTS.exists():
        return []
    paths: List[Path] = []
    for corpus_dir in HTML_DOCUMENTS.iterdir():
        if not corpus_dir.is_dir():
            continue
        for sub_dir in corpus_dir.iterdir():
            if not sub_dir.is_dir():
                continue
            paths.extend(sub_dir.glob("*.html"))
    return sorted(paths)
