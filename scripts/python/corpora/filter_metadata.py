import pandas as pd
import numpy as np
import sys
import math


df = pd.read_csv("./texts/human/gutenberg_rdf_metadata.csv", sep="\t")

# Gutenberg language codes:
# en = English, fr = French, es = Spanish, it = Italian
languages = ["en", "fr", "es", "it", "de"]

df = df[df["language"].isin(languages)].copy()

# Clean year
df["year"] = pd.to_numeric(df["year"])
df = df.dropna(subset=["year"])
df["year"] = df["year"].astype(int)

# Optional: keep only reasonable literary years
df = df[(df["year"] <= 2010)]

def century_from_year(year):
    if not year or math.isnan(year):
        return None
    century = (int(year) - 1) // 100 + 1
    if century == 1:
        return "1st century"
    elif century == 2:
        return "2nd century"
    elif century == 3:
        return "3rd century"
    else:
        print(f"{century}")
        return f"{century}th century"

df["century"] = df["estimated_published"].apply(century_from_year)

# Reorder columns
df = df[
    [
        "id",
        "language",
        "century",
        "genre",
        "subgenre",
        "title",
        "author",
        "year",
        "url",
        "subjects",
        "bookshelves",
        "rdf_file",
    ]
]

# Save filtered full file
df.to_csv("./texts/human/gutenberg_filtered_by_language_century_genre.csv",
          index=False,
          sep='\t')

# Summary table: language × century × genre
summary = (
    df.groupby(["language", "century", "genre"])
      .size()
      .reset_index(name="count")
      .sort_values(["language", "century", "genre"])
)

summary.to_csv("./texts/human/gutenberg_summary_by_language_century_genre.csv", index=False)

