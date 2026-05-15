# download_gutenberg_utf8_recent.py
import argparse
import csv
import gzip
import os
import re
import tarfile
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date
from pathlib import Path
from urllib.request import urlretrieve

import pandas as pd
import requests
from tqdm import tqdm

CATALOG_URL = "https://www.gutenberg.org/cache/epub/feeds/rdf-files.tar.bz2"

def download_catalog(path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        print("Downloading RDF catalog...")
        urlretrieve(CATALOG_URL, path)

def parse_rdf_catalog(catalog_path: Path) -> pd.DataFrame:
    rows = []

    with tarfile.open(catalog_path, "r:bz2") as tar:
        members = [m for m in tar.getmembers() if m.name.endswith(".rdf")]

        for m in tqdm(members, desc="Parsing RDF"):
            f = tar.extractfile(m)
            if f is None:
                continue

            text = f.read().decode("utf-8", errors="ignore")

            id_match = re.search(r"ebooks/(\d+)", text)
            if not id_match:
                continue
            book_id = id_match.group(1)

            title = re.search(r"<dcterms:title>(.*?)</dcterms:title>", text, re.S)
            title = title.group(1).strip() if title else ""

            author = re.search(r"<pgterms:name>(.*?)</pgterms:name>", text, re.S)
            author = author.group(1).strip() if author else ""

            lang = re.search(r"<rdf:value>([a-z]{2,3})</rdf:value>", text)
            lang = lang.group(1) if lang else ""

            issued = re.search(r"<dcterms:issued[^>]*>(.*?)</dcterms:issued>", text)
            issued = issued.group(1).strip() if issued else ""

            subjects = re.findall(r"<rdf:value>(.*?)</rdf:value>", text, re.S)
            subjects = "; ".join(s.strip() for s in subjects if len(s.strip()) > 2)

            urls = re.findall(r'rdf:about="(https://www\.gutenberg\.org/files/[^"]+?\.txt\.utf-8)"', text)

            for url in urls:
                rows.append({
                    "id": book_id,
                    "title": title,
                    "author": author,
                    "language": lang,
                    "gutenberg_release_date": issued,
                    "subjects": subjects,
                    "txt_url": url,
                })

    return pd.DataFrame(rows).drop_duplicates("id")

def safe_filename(row):
    title = re.sub(r"[^\w\-]+", "_", row["title"])[:80]
    return f'{row["id"]}_{row["language"]}_{title}.txt'

def download_one(row, out_dir: Path):
    out_file = out_dir / safe_filename(row)
    if out_file.exists() and out_file.stat().st_size > 0:
        return "exists", row["id"]

    try:
        r = requests.get(row["txt_url"], timeout=30)
        r.raise_for_status()
        out_file.write_text(r.text, encoding="utf-8")
        return "ok", row["id"]
    except Exception as e:
        return f"failed: {e}", row["id"]

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="gutenberg_utf8_recent")
    parser.add_argument("--languages", nargs="+", default=["en", "fr", "es", "de", "it"])
    parser.add_argument("--workers", type=int, default=8)
    args = parser.parse_args()

    out_dir = Path(args.out)
    text_dir = out_dir / "texts"
    text_dir.mkdir(parents=True, exist_ok=True)

    catalog_path = out_dir / "rdf-files.tar.bz2"
    download_catalog(catalog_path)

    df = parse_rdf_catalog(catalog_path)

    df = df[
        df["language"].isin(args.languages)
        & (df["gutenberg_release_date"] <= 2010)
    ].copy()

    metadata_path = out_dir / "metadata.csv"
    df.to_csv(metadata_path, index=False, quoting=csv.QUOTE_MINIMAL)

    print(f"Books selected: {len(df)}")
    print(f"Metadata written to: {metadata_path}")

    rows = df.to_dict("records")

    with ThreadPoolExecutor(max_workers=args.workers) as ex:
        futures = [ex.submit(download_one, row, text_dir) for row in rows]

        for fut in tqdm(as_completed(futures), total=len(futures), desc="Downloading"):
            status, book_id = fut.result()
            if not status.startswith(("ok", "exists")):
                print(book_id, status)

if __name__ == "__main__":
    main()

