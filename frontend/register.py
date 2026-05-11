"""Load TEI register files (person/org/place) into lookup dictionaries."""

from pipeline.config import XML_ID
from pipeline.utils.xml_loader import load_index, xpath
from pipeline.utils.text_utils import normalize_space, elem_text


def _reg_text(element):
    """Extract normalized text from a <reg> element, or empty string."""
    regs = xpath(element, ".//tei:reg", )
    if not regs:
        return ""
    for reg in regs:
        txt = normalize_space(elem_text(reg))
        if txt:
            return txt
    return ""


def _format_death_german(death_iso):
    """Format an ISO death date as German `15.07.1396` (or pass through).

    Tooltip convention: `† 15.07.1396`. Returns the ISO value unchanged
    if the format is not parsable (tolerant: year-only values, special
    characters, etc.).
    """
    if not death_iso:
        return ""
    parts = death_iso.split("-")
    if len(parts) == 3 and all(p.isdigit() for p in parts):
        y, m, d = parts
        return f"{int(d):02d}.{int(m):02d}.{int(y):04d}"
    if len(parts) == 1 and parts[0].isdigit():
        return parts[0]
    return death_iso


def load_persons():
    """Load personList.xml into {xml_id: {forename, surname, addName, death}}.

    Tooltip format: "Forename Surname († DD.MM.YYYY) [pe__id]"
    """
    tree = load_index("personList.xml")
    persons = {}

    for person in xpath(tree, "//tei:person"):
        xml_id = person.get(XML_ID, "")
        if not xml_id:
            continue

        forename = ""
        surname = ""
        add_name = ""

        for fn in xpath(person, ".//tei:forename"):
            forename = _reg_text(fn) or normalize_space(elem_text(fn))
            if forename:
                break

        for sn in xpath(person, ".//tei:surname"):
            surname = _reg_text(sn) or normalize_space(elem_text(sn))
            if surname:
                break

        for an in xpath(person, ".//tei:addName"):
            add_name = _reg_text(an) or normalize_space(elem_text(an))
            if add_name:
                break

        death = ""
        death_elems = xpath(person, ".//tei:death")
        if death_elems:
            death = death_elems[0].get("notAfter", "") or normalize_space(
                elem_text(death_elems[0])
            )

        parts = [p for p in [forename, surname, add_name] if p]
        display = " ".join(parts) if parts else xml_id

        persons[xml_id] = {
            "forename": forename,
            "surname": surname,
            "addName": add_name,
            "death": death,
            "display": display,
            "sex": person.get("sex", ""),
        }

    return persons


def load_orgs():
    """Load orgList.xml into {xml_id: {name, type}}.

    Tooltip format: "Name (Type) [org__id]"
    """
    tree = load_index("orgList.xml")
    orgs = {}

    for org in xpath(tree, "//tei:org"):
        xml_id = org.get(XML_ID, "")
        if not xml_id:
            continue

        name = ""
        for on in xpath(org, ".//tei:orgName"):
            name = _reg_text(on) or normalize_space(elem_text(on))
            if name:
                break

        orgs[xml_id] = {
            "name": name or xml_id,
            "type": org.get("type", ""),
        }

    return orgs


def load_places():
    """Load placeList.xml into {xml_id: {name, type, lat, lng}}.

    Tooltip format: "Name (Type) [lat, lng] [pl__id]"
    """
    tree = load_index("placeList.xml")
    places = {}

    for place in xpath(tree, "//tei:place"):
        xml_id = place.get(XML_ID, "")
        if not xml_id:
            continue

        name = ""
        for pn in xpath(place, ".//tei:placeName"):
            name = _reg_text(pn) or normalize_space(elem_text(pn))
            if name:
                break

        lat, lng = "", ""
        geo_elems = xpath(place, ".//tei:geo")
        if geo_elems:
            coords = normalize_space(elem_text(geo_elems[0])).split()
            if len(coords) >= 2:
                lat, lng = coords[0], coords[1]

        places[xml_id] = {
            "name": name or xml_id,
            "type": place.get("type", ""),
            "lat": lat,
            "lng": lng,
        }

    return places


def build_tooltip_person(person_data, xml_id):
    """Build tooltip string for a person."""
    parts = [person_data["display"]]
    if person_data["death"]:
        parts.append(f"(† {_format_death_german(person_data['death'])})")
    parts.append(f"[{xml_id}]")
    return " ".join(parts)


def build_tooltip_org(org_data, xml_id):
    """Build tooltip string for an organisation."""
    parts = [org_data["name"]]
    if org_data["type"]:
        parts.append(f"({org_data['type']})")
    parts.append(f"[{xml_id}]")
    return " ".join(parts)


def build_tooltip_place(place_data, xml_id):
    """Build tooltip string for a place."""
    parts = [place_data["name"]]
    if place_data["type"]:
        parts.append(f"({place_data['type']})")
    if place_data["lat"] and place_data["lng"]:
        parts.append(f"[{place_data['lat']}, {place_data['lng']}]")
    parts.append(f"[{xml_id}]")
    return " ".join(parts)
