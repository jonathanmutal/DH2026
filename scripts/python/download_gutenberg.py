# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "gutenbergpy",
#     "pandas",
#     "tqdm",
# ]
# ///
import re
import sys
import pandas as pd
from gutenbergpy.gutenbergcache import GutenbergCache, GutenbergCacheTypes
from gutenbergpy.textget import get_text_by_id
from tqdm import tqdm
from pathlib import Path

OUT = Path("gutenberg_corpus")
OUT.mkdir(exist_ok=True)

GutenbergCache.create(refresh=True, download=True, unpack=True, parse=True, cache=True, deleteTemp=True)
cache = GutenbergCache.get_cache(GutenbergCacheTypes.CACHE_TYPE_MONGODB)

books = cache.native_query({type:'Text'})
print(list(books))
sys.exit()
def guess_genre(title):
    t = title.lower()
    poetry_words = ["poems", "poetry", "verses", "sonnets", "songs", "ballads", "rhymes"]
    prose_keywords = ["fiction", "novel", "essays", "biography", "history"]
    if any(w in t for w in poetry_words):
        return "poetry"
    if any(w in t for w in prose_keywords):
        return "prose"
    return "other"

def guess_subgenre(title):
    t = title.lower()
    if "novel" in t:
        return "novel"
    if "essay" in t or "essays" in t:
        return "essay"
    if "poems" in t or "poetry" in t:
        return "poetry_collection"
    if "sonnets" in t:
        return "sonnet"
    if "plays" in t or "tragedy" in t or "comedy" in t:
        return "drama"
    if "letters" in t:
        return "letters"
    if "memoir" in t or "autobiography" in t:
        return "memoir"
    return "unknown"

rows = []

# get all text book IDs
books_ids = cache.native_query("""
SELECT * FROM books
""")

for (book_id,) in tqdm(book_ids):
    try:
        metadata = cache.get_metadata("title", book_id)
        title = list(metadata)[0] if metadata else f"book_{book_id}"

        authors = cache.get_metadata("author", book_id)
        author = "; ".join(authors) if authors else "unknown"

        languages = cache.get_metadata("language", book_id)
        language = "; ".join(languages) if languages else "unknown"

        years = cache.get_metadata("issued", book_id)
        year = list(years)[0] if years else "unknown"

        raw = get_text_by_id(book_id)
        text = raw.decode("utf-8", errors="ignore")

        safe_title = re.sub(r"[^a-zA-Z0-9_-]+", "_", title)[:80]
        path = OUT / f"{book_id}_{safe_title}.txt"
        path.write_text(text, encoding="utf-8")

        rows.append({
            "language": language,
            "genre": guess_genre(title),
            "subgenre": guess_subgenre(title),
            "title": title,
            "author": author,
            "year": year,
            "url": f"https://www.gutenberg.org/ebooks/{book_id}",
            "local_path": str(path)
        })

    except Exception as e:
        print(f"Skipping {book_id}: {e}")

df = pd.DataFrame(rows)
df.to_csv("gutenberg_metadata.csv", index=False)
df.to_json("gutenberg_metadata.json", orient="records", indent=2, force_ascii=False)

print(df.head())
print(f"Downloaded {len(df)} books")

