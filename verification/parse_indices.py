"""Register-Loader für personList.xml, orgList.xml, placeList.xml.

Liest die drei Register aus dem Pipeline-Repo unabhängig von der
Build-Pipeline. Liefert je ein Dict `xml_id → Record` mit den Feldern,
die für Aggregation und Vergleich relevant sind (sex, name, Bezeichnung).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Optional

from lxml import etree

from verification.config import NS, ORG_LIST, PERSON_LIST, PLACE_LIST


@dataclass
class PersonRecord:
    xml_id: str
    sex: Optional[str] = None
    forename: Optional[str] = None
    surname: Optional[str] = None


@dataclass
class OrgRecord:
    xml_id: str
    name: Optional[str] = None


@dataclass
class PlaceRecord:
    xml_id: str
    name: Optional[str] = None


def _text_of(node) -> Optional[str]:
    if node is None:
        return None
    text = node.text
    if text is None:
        return None
    text = text.strip()
    return text or None


def load_persons() -> Dict[str, PersonRecord]:
    """Alle <person>-Einträge aus personList.xml nach xml_id."""
    tree = etree.parse(str(PERSON_LIST))
    root = tree.getroot()
    out: Dict[str, PersonRecord] = {}
    for person in root.iter(f"{{{NS['tei']}}}person"):
        xml_id = person.get("{http://www.w3.org/XML/1998/namespace}id")
        if not xml_id:
            continue
        sex = person.get("sex")
        forename = _text_of(person.find(".//tei:forename/tei:reg", NS))
        surname = _text_of(person.find(".//tei:surname/tei:reg", NS))
        out[xml_id] = PersonRecord(xml_id=xml_id, sex=sex, forename=forename, surname=surname)
    return out


def load_orgs() -> Dict[str, OrgRecord]:
    tree = etree.parse(str(ORG_LIST))
    root = tree.getroot()
    out: Dict[str, OrgRecord] = {}
    for org in root.iter(f"{{{NS['tei']}}}org"):
        xml_id = org.get("{http://www.w3.org/XML/1998/namespace}id")
        if not xml_id:
            continue
        name = _text_of(org.find("tei:orgName/tei:reg", NS)) or _text_of(org.find("tei:orgName", NS))
        out[xml_id] = OrgRecord(xml_id=xml_id, name=name)
    return out


def load_places() -> Dict[str, PlaceRecord]:
    tree = etree.parse(str(PLACE_LIST))
    root = tree.getroot()
    out: Dict[str, PlaceRecord] = {}
    for place in root.iter(f"{{{NS['tei']}}}place"):
        xml_id = place.get("{http://www.w3.org/XML/1998/namespace}id")
        if not xml_id:
            continue
        name = _text_of(place.find("tei:placeName/tei:reg", NS)) or _text_of(place.find("tei:placeName", NS))
        out[xml_id] = PlaceRecord(xml_id=xml_id, name=name)
    return out
