from pathlib import Path

import sys
import re


START_RE = re.compile(
    r"\*\*\*\s*START OF (?:THE|THIS) PROJECT GUTENBERG EBOOK.*?\*\*\*",
    re.IGNORECASE | re.DOTALL,
)

END_RE = re.compile(
    r"\*\*\*\s*END OF (?:THE|THIS) PROJECT GUTENBERG EBOOK.*?\*\*\*",
    re.IGNORECASE | re.DOTALL,
)


METADATA_LINE_RE = re.compile(
    r"""
    ^\s*
    (
        title|author|editor|translator|illustrator|release\ date|language|credits|
        titel|autor|herausgeber|übersetzer|illustrator|sprache|
        título|autor|editor|traductor|ilustrador|idioma|lengua|
        titolo|autore|curatore|traduttore|illustratore|lingua
    )
    \s*:.*$
    """,
    re.IGNORECASE | re.MULTILINE | re.VERBOSE,
)


NOISE_KEYWORDS_RE = re.compile(
    r"""
    \b(
        edited\ by|translated\ by|illustrated\ by|transcribed\ by|
        published\ by|publisher|edition|copyright|preface\ by|

        herausgegeben\ von|übersetzt\ von|illustriert\ von|
        verlag|ausgabe|vorwort|copyright|

        editado\ por|traducido\ por|ilustrado\ por|
        transcrito\ por|publicado\ por|editorial|edición|prólogo|derechos\ reservados|

        a\ cura\ di|tradotto\ da|illustrato\ da|
        trascritto\ da|pubblicato\ da|editore|edizione|prefazione|diritti\ riservati
    )\b
    """,
    re.IGNORECASE | re.VERBOSE,
)


TOC_RE = re.compile(
    r"""
    ^\s*
    (
        contents|table\s+of\s+contents|
        inhalt|inhaltsverzeichnis|
        índice|indice|tabla\s+de\s+contenido|
        sommario|indice
    )
    \s*$
    .*?
    (?=
        ^\s*
        (
            chapter|book|part|section|
            kapitel|buch|teil|abschnitt|
            capítulo|libro|parte|sección|
            capitolo|libro|parte|sezione
        )
        \s+([ivxlcdm]+|\d+)\b
        |
        \Z
    )
    """,
    re.IGNORECASE | re.DOTALL | re.MULTILINE | re.VERBOSE,
)


def normalize_newlines(text: str) -> str:
    return text.replace("\r\n", "\n").replace("\r", "\n")


def remove_gutenberg_boilerplate(text: str) -> str:
    start = START_RE.search(text)
    if start:
        text = text[start.end():]

    end = END_RE.search(text)
    if end:
        text = text[:end.start()]

    return text


def remove_line_indexes(text: str) -> str:
    return re.sub(r"^\s*\d{1,6}\s+(?=\S)", "", text, flags=re.MULTILINE)


def remove_metadata_lines(text: str) -> str:
    return METADATA_LINE_RE.sub("", text)


def remove_transcription_notes(text: str) -> str:
    patterns = [
        # English
        r"^\s*Transcribed from.*?(?=\n\s*\n)",
        r"^\s*Produced by.*?(?=\n\s*\n)",
        r"^\s*E-text prepared by.*?(?=\n\s*\n)",

        # German
        r"^\s*Transkribiert.*?(?=\n\s*\n)",
        r"^\s*Hergestellt von.*?(?=\n\s*\n)",
        r"^\s*Erstellt von.*?(?=\n\s*\n)",

        # Spanish
        r"^\s*Transcrito.*?(?=\n\s*\n)",
        r"^\s*Producido por.*?(?=\n\s*\n)",
        r"^\s*Preparado por.*?(?=\n\s*\n)",

        # Italian
        r"^\s*Trascritto.*?(?=\n\s*\n)",
        r"^\s*Prodotto da.*?(?=\n\s*\n)",
        r"^\s*Preparato da.*?(?=\n\s*\n)",
    ]

    for pattern in patterns:
        text = re.sub(
            pattern,
            "",
            text,
            flags=re.IGNORECASE | re.DOTALL | re.MULTILINE,
        )

    return text


def remove_title_page_noise(text: str, max_lines: int = 100) -> str:
    lines = text.splitlines()
    front = lines[:max_lines]
    rest = lines[max_lines:]

    cleaned_front = []
    for line in front:
        if NOISE_KEYWORDS_RE.search(line):
            continue
        cleaned_front.append(line)

    return "\n".join(cleaned_front + rest)


def remove_table_of_contents(text: str) -> str:
    return TOC_RE.sub("", text)


def normalize_spaces(text: str) -> str:
    text = re.sub(r"[ \t]+$", "", text, flags=re.MULTILINE)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def clean_gutenberg_text(text: str) -> str:
    text = normalize_newlines(text)
    text = remove_gutenberg_boilerplate(text)
    text = remove_line_indexes(text)
    text = remove_transcription_notes(text)
    text = remove_metadata_lines(text)
    text = remove_title_page_noise(text)
    text = remove_table_of_contents(text)
    text = normalize_spaces(text)
    return text


def clean_file(input_path: Path, output_path: Path):
    text = input_path.read_text(encoding="utf-8", errors="replace")
    cleaned = clean_gutenberg_text(text)
    output_path.write_text(cleaned, encoding="utf-8")


def clean_folder(input_dir: str, output_dir: str):
    input_dir = Path(input_dir)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    for path in input_dir.glob("*.txt"):
        output_path = output_dir / path.name
        clean_file(path, output_path)
        print(f"Cleaned: {path.name}")


if __name__ == "__main__":
    if len(sys.argv[1:]) < 2:
        print("Please provide the input and output directories")
        sys.exit()

    input_dir = sys.argv[1]
    output_dir = sys.argv[2]

    clean_folder(
        input_dir=input_dir,
        output_dir=output_dir,
    )

