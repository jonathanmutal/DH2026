# Downloading and extracting the corpora
mkdir -p ./texts/human
# get the rdf files to get the metadata of the whole books
wget https://www.gutenberg.org/cache/epub/feeds/rdf-files.tar.bz2 -O ./texts/rdf-files.tar.bz2
# untar
tar -xjf ./texts/rdf-files.tar.bz2 ./texts/.
# this transforms the metadata from rdf to csv for the gutenberg books
# under ./texts/human/gutenberg_rdf_metadata.csv
# this script also infers the gendre (prose, poetry and drama)
uv run ./scripts/python/corpora/parse_gutenberg_rdf.py
# Filter Italian, French, Spanish, English and German books.
# This will save a csv file in ./texts/human/gutenberg_filtered_by_language_century_genre.csv
# and the stats are in ./texts/human/gutenberg_summary_by_language_century_genre.csv 
uv run ./scripts/python/corpora/filter_metadata.py
# Download the corpora on all languages (the one filtered by metadata)
# It will save pandas dataframe in parquet format each 1k iteration
# To do so, we use slurm so we can download the data 12h
sbatch ./scripts/slurm/corpora/download_corpora.sh
# preprocess the corpus
# remove the head and footer from the project Gutenberg

