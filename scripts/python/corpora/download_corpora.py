from pathlib import Path
from contextlib import contextmanager

from tqdm import tqdm

import pandas as pd
import xml.etree.ElementTree as ET
import requests
import re


INPUT_CSV = "./texts/human/gutenberg_filtered_by_language_century_genre.csv"
OUTPUT_TSV = "./texts/human/metadata_human.tsv"
OUTPUT_PARQUET = "./texts/human"
OUT_ROOT = Path("./texts/human")

NS = {
    "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
    "pgterms": "http://www.gutenberg.org/2009/pgterms/",
    "dcterms": "http://purl.org/dc/terms/",
}

def safe_filename(title):
    title = str(title).strip()
    title = re.sub(r"[^\w\s.-]", "", title, flags=re.UNICODE)
    title = re.sub(r"\s+", "_", title)
    return title[:120] or "untitled"

def find_utf8_txt_url(rdf_file):
    rdf_file = Path(rdf_file)
    if not rdf_file.exists():
        return None

    root = ET.parse(rdf_file).getroot()

    for file_elem in root.findall(".//pgterms:file", NS):
        url = file_elem.attrib.get(f"{{{NS['rdf']}}}about", "")

        if not url.endswith(".txt.utf-8"):
            continue

        fmt = file_elem.find(".//rdf:value", NS)
        fmt_text = fmt.text.lower() if fmt is not None and fmt.text else ""

        if "text/plain" in fmt_text and "charset=utf-8" in fmt_text:
            return url

    return None

def download_text(url, path):
    path.parent.mkdir(parents=True, exist_ok=True)

    r = requests.get(url, timeout=30)
    r.raise_for_status()

    if not path.exists():
        path.write_text(r.text, encoding="utf-8")


def latest_parquet(folder):
    files = list(Path(folder).glob("*.parquet"))
    if not files:
        return pd.DataFrame()
    latest = max(
        files,
        key=lambda p: int(re.search(r"step(\d+)\.parquet$", p.name).group(1))
    )
    print(latest)
    df = pd.read_parquet(latest)
    return df

def main():
    df = pd.read_csv(INPUT_CSV, sep="\t")

    metadata_rows = []

    latest_saved = latest_parquet(OUTPUT_PARQUET)
    print(latest_saved.head())
    print(len(latest_saved))
    for index, row in tqdm(df.iterrows(), total=len(df)):
        if index < len(latest_saved):
            continue
        lang = str(row["language"])
        genre = str(row["genre"])
        title = str(row["title"])
        rdf_file = row["rdf_file"]

        txt_url = find_utf8_txt_url(rdf_file)

        if not txt_url:
            print(f"No UTF-8 txt found for: {title}")
            continue

        filename = safe_filename(title) + ".txt"
        out_path = OUT_ROOT / lang / genre / filename

        if not out_path.exists():
            try:
                download_text(txt_url, out_path)
            except Exception as e:
                print(f"Download failed for {title}: {e}")
                continue

        metadata_rows.append({
            "path": str(out_path),
            "language": row.get("language"),
            "century": row.get("century"),
            "year": row.get("year"),
            "genre": row.get("genre"),
            "subgenre": row.get("subgenre"),
            "subjects": row.get("subjects"),
            "title": row.get("title"),
            "author": row.get("author"),
            "url": txt_url,
        })

        if index % 1000 == 0:
            pd.DataFrame(metadata_rows).to_parquet(OUTPUT_PARQUET / Path(f"step{index}.parquet"))

    pd.DataFrame(metadata_rows).to_parquet(OUTPUT_PARQUET / Path(f"step{index}.parquet"))
    out_df = pd.concat([latest_saved, pd.DataFrame(metadata_rows)], ignore_index=True)

    out_df.to_csv(
        OUTPUT_TSV,
        sep="\t",
        index=False,
        encoding="utf-8"
    )

    print(f"Saved metadata to {OUTPUT_TSV}")
    print(f"Downloaded {len(out_df)} texts")

if __name__ == "__main__":
    main()
