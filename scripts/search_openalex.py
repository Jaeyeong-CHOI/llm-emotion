#!/usr/bin/env python3
import argparse
import json
import time
import urllib.parse
import urllib.request
from pathlib import Path


def fetch_openalex(query: str, per_page: int = 25):
    base = "https://api.openalex.org/works"
    params = {
        "search": query,
        "per-page": per_page,
        "select": "id,display_name,publication_year,doi,primary_location,authorships,concepts,type",
    }
    url = f"{base}?{urllib.parse.urlencode(params)}"
    with urllib.request.urlopen(url, timeout=30) as r:
        return json.loads(r.read().decode("utf-8"))


def normalize_row(item, group, query):
    title = item.get("display_name")
    year = item.get("publication_year")
    doi = item.get("doi")
    location = item.get("primary_location") or {}
    landing = location.get("landing_page_url")
    source = (location.get("source") or {}).get("display_name")
    authors = []
    for a in item.get("authorships", [])[:5]:
        name = (a.get("author") or {}).get("display_name")
        if name:
            authors.append(name)
    return {
        "group": group,
        "query": query,
        "title": title,
        "year": year,
        "doi": doi,
        "url": landing,
        "venue": source,
        "authors": authors,
        "type": item.get("type"),
        "openalex_id": item.get("id"),
    }


def dedup_key(row):
    if row.get("doi"):
        return ("doi", row["doi"].lower())
    return ("title", (row.get("title") or "").strip().lower())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    cfg = json.loads(Path(args.config).read_text(encoding="utf-8"))
    per_query = int(cfg.get("per_query", 25))

    rows = []
    for g in cfg.get("groups", []):
        gname = g.get("name", "unknown")
        for q in g.get("queries", []):
            data = fetch_openalex(q, per_page=per_query)
            for item in data.get("results", []):
                rows.append(normalize_row(item, gname, q))
            time.sleep(0.5)

    deduped = {}
    for r in rows:
        k = dedup_key(r)
        if k not in deduped:
            deduped[k] = r

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8") as f:
        for r in sorted(deduped.values(), key=lambda x: (x.get("year") or 0), reverse=True):
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    print(f"Fetched {len(rows)} records, deduped to {len(deduped)} -> {out}")


if __name__ == "__main__":
    main()
