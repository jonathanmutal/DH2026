# download_10_corpora.py

from pathlib import Path
import nltk
from datasets import load_dataset

OUT_DIR = Path("ready_made_corpora")
OUT_DIR.mkdir(exist_ok=True)

def save_text(name, text):
    path = OUT_DIR / f"{name}.txt"
    path.write_text(text, encoding="utf-8")
    print(f"Saved {path} | {len(text.split()):,} words")

def download_nltk_corpora():
    nltk_ids = [
        "brown",
        "gutenberg",
        "reuters",
        "inaugural",
        "webtext",
        "state_union",
    ]

    for corpus_id in nltk_ids:
        nltk.download(corpus_id, quiet=True)

    from nltk.corpus import brown, gutenberg, reuters, inaugural, webtext, state_union

    save_text("01_brown", " ".join(brown.words()))
    save_text("02_gutenberg_nltk", " ".join(gutenberg.words()))
    save_text("03_reuters", " ".join(reuters.words()))
    save_text("04_inaugural", " ".join(inaugural.words()))
    save_text("05_webtext", " ".join(webtext.words()))
    save_text("06_state_union", " ".join(state_union.words()))

def download_hf_corpora():
    # 7. WikiText-103
    ds = load_dataset("wikitext", "wikitext-103-v1")
    text = "\n".join(ds["train"]["text"])
    save_text("07_wikitext_103", text)

    # 8. WikiText-2
    ds = load_dataset("wikitext", "wikitext-2-v1")
    text = "\n".join(ds["train"]["text"])
    save_text("08_wikitext_2", text)

    # 9. OPUS Books English-French
    # Parallel corpus; we save English and French sides separately.
    ds = load_dataset("Helsinki-NLP/opus_books", "en-fr")
    en_lines, fr_lines = [], []

    for row in ds["train"]:
        trans = row["translation"]
        en_lines.append(trans.get("en", ""))
        fr_lines.append(trans.get("fr", ""))

    save_text("09_opus_books_en", "\n".join(en_lines))
    save_text("09_opus_books_fr", "\n".join(fr_lines))

    # 10. OpenSubtitles-style corpus
    # This may require trust_remote_code depending on your datasets version.
    try:
        ds = load_dataset(
            "Helsinki-NLP/open_subtitles",
            "en-fr",
            trust_remote_code=True,
        )

        en_lines, fr_lines = [], []
        split = list(ds.keys())[0]

        for row in ds[split].select(range(min(100000, len(ds[split])))):
            trans = row.get("translation", {})
            en_lines.append(trans.get("en", ""))
            fr_lines.append(trans.get("fr", ""))

        save_text("10_open_subtitles_en_sample", "\n".join(en_lines))
        save_text("10_open_subtitles_fr_sample", "\n".join(fr_lines))

    except Exception as e:
        print("OpenSubtitles download failed.")
        print("Reason:", e)
        print("You can replace it with another Hugging Face dataset.")

def main():
    download_nltk_corpora()
    download_hf_corpora()

if __name__ == "__main__":
    main()
