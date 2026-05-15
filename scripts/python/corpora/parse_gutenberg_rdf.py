from pathlib import Path
import xml.etree.ElementTree as ET
import pandas as pd
from tqdm import tqdm
import re

RDF_ROOT = Path("./texts/cache/epub")
OUTPUT_CSV = Path("./texts/human/gutenberg_rdf_metadata.csv")

NS = {
    "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
    "pgterms": "http://www.gutenberg.org/2009/pgterms/",
    "dcterms": "http://purl.org/dc/terms/",
    "dcam": "http://purl.org/dc/dcam/",
}
def get_author_years(root):
    agent = root.find(".//dcterms:creator/pgterms:agent", NS)
    if agent is None:
        return None, None

    birth = text_or_none(agent.find("./pgterms:birthdate", NS))
    death = text_or_none(agent.find("./pgterms:deathdate", NS))
    if birth:
        birth = int(birth)
    if death:
        death = int(death)
    return birth, death

def text_or_none(elem):
    if elem is None:
        return None
    if elem.text is None:
        return None
    return elem.text.strip()

def get_book_id(root):
    ebook = root.find(".//pgterms:ebook", NS)
    if ebook is None:
        return None

    about = ebook.attrib.get(f"{{{NS['rdf']}}}about", "")
    match = re.search(r"ebooks/(\d+)", about)
    return int(match.group(1)) if match else None

def get_title(root):
    return text_or_none(root.find(".//dcterms:title", NS))

def get_language(root):
    langs = []
    for lang in root.findall(".//dcterms:language/rdf:Description/rdf:value", NS):
        if lang.text:
            langs.append(lang.text.strip())
    return "; ".join(sorted(set(langs))) if langs else None

def get_authors(root):
    authors = []
    for creator in root.findall(".//dcterms:creator/pgterms:agent/pgterms:name", NS):
        if creator.text:
            authors.append(creator.text.strip())
    return "; ".join(authors) if authors else None

def get_year(root):
    issued = text_or_none(root.find(".//dcterms:issued", NS))
    if issued:
        return issued[:4]
    return None

def get_subjects(root):
    subjects = []
    for subj in root.findall(".//dcterms:subject/rdf:Description/rdf:value", NS):
        if subj.text:
            subjects.append(subj.text.strip())
    return "; ".join(sorted(set(subjects))) if subjects else None

def get_bookshelves(root):
    shelves = []
    for shelf in root.findall(".//pgterms:bookshelf/rdf:Description/rdf:value", NS):
        if shelf.text:
            shelves.append(shelf.text.strip())
    return "; ".join(sorted(set(shelves))) if shelves else None

def get_download_url(book_id):
    return f"https://www.gutenberg.org/ebooks/{book_id}" if book_id else None

def infer_genre(title, subjects, bookshelves):
    text = " ".join([
        title or "",
        subjects or "",
        bookshelves or "",
    ]).lower()

    poetry_keywords = [
        "poetry", "poems", "verse", "verses", "sonnet", "sonnets",
        "ballad", "ballads", "songs", "rhymes", "epic poetry"
    ]

    drama_keywords = [
        "drama", "plays", "tragedy", "comedies", "comedy"
    ]

    if any(k in text for k in poetry_keywords):
        return "poetry"

    if any(k in text for k in drama_keywords):
        return "drama"

    return "prose"

def infer_subgenre(title, subjects, bookshelves):
    text = " ".join([
        title or "",
        subjects or "",
        bookshelves or "",
    ]).lower()

    rules = [
        ("sonnet", ["sonnet", "sonnets"]),
        ("epic_poetry", ["epic poetry", "epic"]),
        ("poetry_collection", ["poems", "poetry", "verse", "verses"]),
        ("novel", ["fiction", "novel", "novels"]),
        ("short_story", ["short stories", "short story"]),
        ("essay", ["essay", "essays"]),
        ("drama", ["drama", "plays", "tragedy", "comedy"]),
        ("biography", ["biography", "autobiography", "memoir"]),
        ("letters", ["letters", "correspondence"]),
        ("history", ["history"]),
        ("philosophy", ["philosophy"]),
        ("religion", ["religion", "bible", "sermons", "theology"]),
        ("travel", ["travel", "voyages", "description and travel"]),
        ("children", ["children", "juvenile"]),
    ]

    for label, keywords in rules:
        if any(k in text for k in keywords):
            return label

    return "unknown"

rows = []

rdf_files = list(RDF_ROOT.rglob("*.rdf"))
print(f"Found {len(rdf_files)} RDF files")

for rdf_file in tqdm(rdf_files):
    try:
        tree = ET.parse(rdf_file)
        root = tree.getroot()

        book_id = get_book_id(root)
        if book_id is None:
            continue

        title = get_title(root)
        language = get_language(root)
        author = get_authors(root)
        year = get_year(root)
        birth_year, death_year = get_author_years(root)
        estimated_published = None
        if birth_year:
            estimated_published = 40 + birth_year
        elif death_year:
            estimated_published = death_year
        subjects = get_subjects(root)
        bookshelves = get_bookshelves(root)

        genre = infer_genre(title, subjects, bookshelves)
        subgenre = infer_subgenre(title, subjects, bookshelves)

        rows.append({
            "id": book_id,
            "language": language,
            "genre": genre,
            "subgenre": subgenre,
            "title": title,
            "author": author,
            "year": year,
            "url": get_download_url(book_id),
            "subjects": subjects,
            "bookshelves": bookshelves,
            "rdf_file": str(rdf_file),
            "author_birth_year": birth_year,
            "author_death_year": death_year,
            "estimated_published": estimated_published
        })

    except Exception as e:
        print(f"Error parsing {rdf_file}: {e}")

df = pd.DataFrame(rows)

df = df.sort_values(["language", "year", "author", "title"], na_position="last")

df.to_csv(OUTPUT_CSV, index=False, encoding="utf-8", sep='\t')

print(f"Saved {len(df)} records to {OUTPUT_CSV}")
print(df.head())
