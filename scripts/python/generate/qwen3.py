# generate_qwen3_batch.py
import re
import argparse
import csv
import hashlib
import itertools
import json
from pathlib import Path

import pandas as pd
import torch
import yaml
from jinja2 import Template
from tqdm import tqdm
from transformers import AutoModelForCausalLM, AutoTokenizer


LANGUAGE_MAP = {
    "en": "English",
    "fr": "French",
    "es": "Spanish",
    "it": "Italian",
    "de": "German",
}

def load_prompt_config(path):
    with open(path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    return config, Template(config["template"])


def source_text_id_from_path(path):
    return hashlib.md5(str(path).encode("utf-8")).hexdigest()[:12]


def render_prompt(template, row, words, conditional_tokens=None):
    language = LANGUAGE_MAP.get(row["language"], row["language"])

    return template.render(
        language=language,
        author=row.get("author", ""),
        title=row.get("title", ""),
        century=row.get("century", ""),
        genre=row.get("genre", ""),
        words=words,
        conditional_tokens=conditional_tokens,
    )


def clean_generation(text):
    text = text.strip()

    if "</think>" in text:
        text = text.split("</think>", 1)[-1].strip()

    return text


def build_output_path(row, output_root, setting_name):
    src_path = Path(row["path"])

    language = row.get("language", "unknown")
    genre = row.get("genre", "unknown")

    source_id = source_text_id_from_path(src_path)
    stem = src_path.stem

    output_dir = Path(output_root) / language / genre / setting_name
    output_dir.mkdir(parents=True, exist_ok=True)

    return output_dir / f"{source_id}_{stem}.txt"

def generate_batch(
    model,
    tokenizer,
    prompts,
    max_new_tokens,
    temperature,
    top_p,
    repetition_penalty,
):
    chat_texts = []
    do_sample=True
    if temperature == 0.0 and top_p == 0.0:
        do_sample=False
    for prompt in prompts:
        messages = [
            {
                "role": "user",
                "content": prompt.strip() + "\n/no_think",
            }
        ]

        chat_text = tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True,
            enable_thinking=False,
        )

        chat_texts.append(chat_text)

    inputs = tokenizer(
        chat_texts,
        return_tensors="pt",
        padding=True,
        truncation=True,
    ).to(model.device)

    with torch.no_grad():
        output_ids = model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            do_sample=do_sample,
            temperature=temperature,
            top_p=top_p,
            repetition_penalty=repetition_penalty,
            pad_token_id=tokenizer.pad_token_id
        )

    generations = []
    for i, ids in enumerate(output_ids):
        input_len = inputs["attention_mask"][i].sum().item()
        generated_ids = ids[input_len:]
        text = tokenizer.decode(generated_ids, skip_special_tokens=True)
        generations.append(clean_generation(text))

    return generations


def append_metadata_rows(metadata_csv, rows):
    file_exists = Path(metadata_csv).exists()

    fieldnames = [
        "path",
        "group",
        "language",
        "genre",
        "period",
        "model",
        "prompt_id",
        "temperature",
        "top_p",
        "repetition_penalty",
        "source_text_id",
        "source_title",
        "source_author",
        "source_year",
    ]

    with open(metadata_csv, "a", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)

        if not file_exists:
            writer.writeheader()

        writer.writerows(rows)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--metadata", required=True)
    parser.add_argument("--prompt", required=True)
    parser.add_argument("--output_root", default="texts/machine")
    parser.add_argument("--metadata_output", default="metadata_machine.csv")
    parser.add_argument("--model", default="Qwen/Qwen3-4B-Instruct-2507")
    parser.add_argument("--prompt_id", default="instruction")
    parser.add_argument("--group", default="machine")
    parser.add_argument("--words", type=int, default=1000)
    parser.add_argument("--max_new_tokens", type=int, default=16384)
    parser.add_argument("--batch_size", type=int, default=8)
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--temperatures", nargs="+", type=float, default=[0.5, 0.7, 0.9])
    parser.add_argument("--top_ps", nargs="+", type=float, default=[0.8, 0.9, 0.95])
    parser.add_argument("--top_ks", nargs="+", type=int, default=None)
    parser.add_argument("--repetition_penalties", nargs="+", type=float, default=[1.0, 1.05, 1.1])
    parser.add_argument("--conditional_tokens_col", default=None)
    parser.add_argument("--skip_existing", action="store_true")
    args = parser.parse_args()

    df = pd.read_csv(args.metadata,
                     sep='\t',
                     engine="python")
    df = df.fillna("")

    if args.limit is not None:
        df = df.head(args.limit)

    prompt_config, template = load_prompt_config(args.prompt)

    tokenizer = AutoTokenizer.from_pretrained(
        args.model,
        trust_remote_code=True,
    )

    tokenizer.padding_side = "left"

    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    model = AutoModelForCausalLM.from_pretrained(
        args.model,
        torch_dtype=torch.bfloat16 if torch.cuda.is_available() else torch.float32,
        device_map="auto",
        trust_remote_code=True,
    )

    model.eval()

    max_new_tokens = args.max_new_tokens or int(args.words * 2)

    hyperparams_grid = {
        "temperature": args.temperatures,
        "top_p": args.top_ps,
        "repetition_penalty": args.repetition_penalties,
    }

    keys = list(hyperparams_grid.keys())
    combinations = list(itertools.product(*hyperparams_grid.values()))

    rows = list(df.iterrows())

    for values in combinations:
        params = dict(zip(keys, values))

        setting_name = (
            f"temp_{params['temperature']}"
            f"_topp_{params['top_p']}"
            f"_rep_{params['repetition_penalty']}"
        )
        if (float(params["temperature"]) == 0.0 and float(params["top_p"]) != 0.0) \
           or (float(params["temperature"]) != 0.0 and float(params["top_p"]) == 0.0):
            continue

        for start in tqdm(
            range(0, len(rows), args.batch_size),
            desc=setting_name,
        ):
            batch_rows = rows[start:start + args.batch_size]

            prompts = []
            output_files = []
            metadata_rows = []

            for idx, row in batch_rows:
                output_file = build_output_path(
                    row=row,
                    output_root=args.output_root,
                    setting_name=setting_name,
                )

                if args.skip_existing and output_file.exists():
                    continue

                conditional_tokens = None

                if args.conditional_tokens_col:
                    value = row.get(args.conditional_tokens_col, None)
                    if pd.notna(value):
                        conditional_tokens = value

                prompt = render_prompt(
                    template=template,
                    row=row,
                    words=args.words,
                    conditional_tokens=conditional_tokens,
                )

                source_path = row.get("path", "")
                source_id = source_text_id_from_path(source_path)

                prompts.append(prompt)
                output_files.append(output_file)

                metadata_rows.append(
                    {
                        "path": str(output_file),
                        "group": args.group,
                        "language": row.get("language", ""),
                        "genre": row.get("genre", ""),
                        "period": row.get("century", ""),
                        "model": args.model,
                        "prompt_id": args.prompt_id,
                        "temperature": params["temperature"],
                        "top_p": params["top_p"],
                        "repetition_penalty": params["repetition_penalty"],
                        "source_text_id": source_id,
                        "source_title": row.get("title", ""),
                        "source_author": row.get("author", ""),
                        "source_year": row.get("century", ""),
                    }
                )

            if not prompts:
                continue
            generations = generate_batch(
                model=model,
                tokenizer=tokenizer,
                prompts=prompts,
                max_new_tokens=max_new_tokens,
                temperature=params["temperature"],
                top_p=params["top_p"],
                repetition_penalty=params["repetition_penalty"],
            )

            for output_file, generated_text in zip(output_files, generations):
                output_file.write_text(generated_text, encoding="utf-8")

            append_metadata_rows(args.metadata_output, metadata_rows)

    print(f"Done. Metadata saved to: {args.metadata_output}")


if __name__ == "__main__":
    main()

