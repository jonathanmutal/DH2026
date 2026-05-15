#!/bin/bash
#SBATCH --job-name=qwen3_gen
#SBATCH --output=logs/qwen3_gen_%j.out
#SBATCH --error=logs/qwen3_gen_%j.err
#SBATCH --partition=shared-gpu
#SBATCH --gres=gpu:1,VramPerGpu:60GB
#SBATCH --cpus-per-task=1
#SBATCH --mem=64G
#SBATCH --time=12:00:00

set -euo pipefail

temperature=${1:-0.0}
top_p=${2:-0.0}
repetition_penalty=${3:-0.0}

mkdir -p logs

module purge
module load GCCcore/13.2.0
module load Python/3.11.5
module load CUDA/12.1.1

export TOKENIZERS_PARALLELISM=false

uv run ./scripts/python/generate/qwen3.py \
  --metadata ./texts/human/subsample_metadata_human.tsv \
  --prompt settings/prompt/roleplay_instruction.yaml \
  --output_root texts/machine/qwen-3 \
  --metadata_output ./texts/machine/subsample_metadata_machine.csv \
  --model Qwen/Qwen3-4B-Instruct-2507 \
  --words 2024 \
  --batch_size 8 \
  --temperatures ${temperature} \
  --top_ps ${top_p} \
  --repetition_penalties ${repetition_penalty} \
  --skip_existing

