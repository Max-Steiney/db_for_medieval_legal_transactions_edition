"""Timeline-Aggregat: Dokument-Counts pro Dekade und Korpus."""

from collections import Counter, defaultdict
from pathlib import Path

from ._shared import _cached_csv, _decade, _meta, _write_json


def aggregate_timeline(docs_data_dir: Path) -> dict:
    """Aggregate filenames.csv into timeline data by collection and decade."""
    rows = _cached_csv("filenames.csv")

    collections: dict[str, dict] = {}
    decades: dict[int, Counter] = defaultdict(Counter)
    placeholder_count = 0
    all_years = []

    for row in rows:
        coll = row.get("collection", "unknown")
        date_str = row.get("date", "")

        if coll not in collections:
            collections[coll] = {"count": 0, "dates": []}
        collections[coll]["count"] += 1

        dec = _decade(date_str)
        if dec is None:
            placeholder_count += 1
        else:
            decades[dec]["total"] += 1
            decades[dec][coll] += 1
            year = int(date_str[:4])
            all_years.append(year)
            collections[coll]["dates"].append(date_str)

    # Summarise collections
    coll_summary = {}
    for name, info in collections.items():
        dates = sorted(info["dates"])
        coll_summary[name] = {
            "count": info["count"],
            "min_date": dates[0] if dates else None,
            "max_date": dates[-1] if dates else None,
        }

    # Build decade list (fill gaps)
    if all_years:
        min_decade = (min(all_years) // 10) * 10
        max_decade = (max(all_years) // 10) * 10
    else:
        min_decade, max_decade = 1170, 1520

    decades_out = {}
    for d in range(min_decade, max_decade + 10, 10):
        entry = {"total": decades[d]["total"]}
        for coll_name in collections:
            entry[coll_name] = decades[d].get(coll_name, 0)
        decades_out[str(d)] = entry

    result = {
        "meta": _meta(
            description="Document counts by decade and source collection",
            sources=["filenames.csv"],
            dimensions=[
                {"name": "decade", "type": "temporal", "values": "1170-1520 (step 10)"},
                {"name": "collection", "type": "categorical",
                 "values": sorted(collections.keys())},
            ],
            measures=[
                {"name": "count", "type": "integer",
                 "description": "Number of source documents"},
            ],
        ),
        "total": len(rows),
        "period": [min(all_years) if all_years else None,
                   max(all_years) if all_years else None],
        "placeholder_count": placeholder_count,
        "collections": coll_summary,
        "decades": decades_out,
    }

    _write_json(result, docs_data_dir / "timeline.json")
    return result


# ---------------------------------------------------------------------------
# Epic A aggregation (V0-T3): roles x sex x institutions
# ---------------------------------------------------------------------------

