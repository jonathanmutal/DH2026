#!/bin/bash
#SBATCH --job-name=gutenberg_download
#SBATCH --partition=shared-cpu
#SBATCH --time=12:00:00
#SBATCH --cpus-per-task=1
#SBATCH --mem=16G
#SBATCH --output=logs/gutenberg_download_%j.out
#SBATCH --error=logs/gutenberg_download_%j.err

set -euo pipefail

mkdir -p logs

echo "Job started on $(date)"
echo "Running on node: $(hostname)"
echo "CPUs: ${SLURM_CPUS_PER_TASK}"

export PYTHONUNBUFFERED=1

uv run ./scripts/python/corpora/download_corpora.py

genres=(prose poetry drama)
languages=(es it en de fr)
for genre in "${genres[@]}"
do
  for language in "${languages[@]}"
  do
    uv run ./scripts/python/preprocess_gutenberg.py ./texts/human/${language}/${genre}/ ./texts/clean_human/${language}/${genre}/ 
  done
done

echo "Job finished on $(date)"
