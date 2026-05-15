import pandas as pd
import sys


from pathlib import Path


N_PER_GROUP = 50
languages = ["en", "fr", "es", "it", "de"]

def read_dataframe(path: Path):
    return pd.read_csv(path,
                       sep='\t')

def diversified_sample(group, n):
    """
    Sample with maximum author diversity first.
    """

    # Shuffle rows
    group = group.sample(frac=1, random_state=42)

    # First pass: one text per author
    first_pass = (
        group.groupby("author", group_keys=False)
        .head(1)
    )

    if len(first_pass) >= n:
        return first_pass.sample(n=n, random_state=42)

    # If not enough authors, add remaining rows
    remaining_needed = n - len(first_pass)

    remaining = group.loc[
        ~group.index.isin(first_pass.index)
    ]

    if len(remaining) > 0:
        extra = remaining.sample(
            n=min(remaining_needed, len(remaining)),
            random_state=42
        )

        return pd.concat([first_pass, extra])

    return first_pass

if len(sys.argv) < 3:
    print("sub_sample.py <input_tsv> <output_tsv>")
    sys.exit(-1)


arguments = sys.argv[1:]

source_path = Path(arguments[0])
target_path = Path(arguments[1])
df = read_dataframe(source_path)

df_concat = []

for lang in languages:
    df_lang = df[df.language == lang]
    df_genre = df_lang[df_lang.genre != "unknown"]

    sampled_df = (
        df_genre
        .groupby(["century", "genre"], group_keys=False)
        .apply(
            lambda g: diversified_sample(g, N_PER_GROUP)
            .assign(
                century=g.name[0],
                genre=g.name[1]
            )
        )
        .reset_index(drop=True)
    )

    # Join missing metadata back from original df_genre
    metadata = df_genre[["path", "century", "genre"]].drop_duplicates("path")

    sampled_df = sampled_df.drop(columns=["century", "genre"], errors="ignore")

    sampled_df = sampled_df.merge(
        metadata,
        on="path",
        how="left"
    )

    # Reorder columns
    sampled_df = sampled_df[
        [
            "path", "language", "century", "year", "genre",
            "subgenre", "subjects", "title", "author", "url"
        ]
    ]
    df_concat.append(sampled_df)

final_df = pd.concat(df_concat, ignore_index=True)

final_df.to_csv(target_path, sep="\t", index=False)

