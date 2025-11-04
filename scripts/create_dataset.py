import os
import json
import csv
import uuid
from pathlib import Path

RAW_DIR = Path("data/raw")
OUT_FILE = Path("data/sample.jsonl")
CSV_INPUT = Path("data/raw_labels.csv")  # optional CSV with columns: prompt,completion,source


def from_raw_files():
    """
    Read all .txt files from data/raw. Each file becomes one sample where the whole file is the prompt.
    """
    samples = []
    if not RAW_DIR.exists():
        print(f"No {RAW_DIR} directory found. Create it and add .txt files, or provide a CSV at {CSV_INPUT}.")
        return samples

    for p in sorted(RAW_DIR.glob("*.txt")):
        text = p.read_text(encoding="utf-8").strip()
        if not text:
            continue
        sample = {
            "id": str(uuid.uuid4()),
            "prompt": f"Analyze the following contract clause for regulatory compliance and recommend fixes:\n\n{text}",
            "completion": "",
            "metadata": {"source": str(p.name)}
        }
        samples.append(sample)
    return samples


def from_csv(csv_path):
    samples = []
    if not csv_path.exists():
        return samples
    with csv_path.open(encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            prompt = row.get("prompt") or row.get("input") or row.get("text")
            completion = row.get("completion") or row.get("label") or row.get("output")
            if not prompt:
                continue
            sample = {
                "id": row.get("id", str(uuid.uuid4())),
                "prompt": prompt,
                "completion": completion or "",
                "metadata": {"source": str(csv_path)}
            }
            samples.append(sample)
    return samples


def sanitize(sample):
    sample["prompt"] = sample.get("prompt", "").strip()
    sample["completion"] = sample.get("completion", "").strip()
    if "metadata" not in sample:
        sample["metadata"] = {}
    return sample


def validate(samples, max_samples=None):
    valid = []
    for s in samples:
        s = sanitize(s)
        if not s["prompt"]:
            continue
        if len(s["prompt"]) > 50000:
            print(f"Skipping too-long sample {s['id']}")
            continue
        valid.append(s)
        if max_samples and len(valid) >= max_samples:
            break
    return valid


def write_jsonl(samples, out_path=OUT_FILE):
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as fh:
        for s in samples:
            fh.write(json.dumps(s, ensure_ascii=False) + "\n")
    print(f"Wrote {len(samples)} samples to {out_path}")


def main():
    samples = from_csv(CSV_INPUT)
    if not samples:
        samples = from_raw_files()
    if not samples:
        print("No samples found. Add .txt files to data/raw/ or a CSV at data/raw_labels.csv")
        return
    samples = validate(samples)
    write_jsonl(samples)


if __name__ == "__main__":
    main()
