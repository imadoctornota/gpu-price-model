"""Copy the notebook and its summary outputs into this repo folder, then check for private info.

Usage (from inside this folder):
    python prepare_repo.py --src "C:/path/to/the/folder/you/ran/the/notebook/in"

What it copies:
    gpu_price_model_v7.ipynb             (home-folder paths scrubbed from outputs)
    outputs/*.csv and results_summary.md (summary tables)
    figs/*.png                           (the charts)

What it leaves out:
    data/                                 raw archived PassMark pages and price caches
    outputs/model_prices_monthly.csv      per-card monthly PassMark prices (add --include-card-prices to copy it)

It ends with "privacy check: clean" or a list of what it found. Nothing is pushed anywhere.
"""
import argparse
import json
import re
import shutil
import sys
from pathlib import Path

NOTEBOOK = "gpu_price_model_v7.ipynb"
CARD_PRICES = "model_prices_monthly.csv"
HERE = Path(__file__).resolve().parent

# Home folders in any form: C:\Users\name, C:\\Users\\name, C:/Users/name, /Users/name, /home/name
HOME_RE = re.compile(r"(?i)([a-z]:(?:\\+|/)users(?:\\+|/)|/users/|/home/)([^\\/\s\"':]+)")
EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
# Emails that are fine to publish (none expected; add one here if you want it kept)
EMAIL_OK = set()


def scrub(text):
    return HOME_RE.sub(lambda m: m.group(1) + "you", text)


def copy_notebook(src, dst):
    nb = json.loads((src / NOTEBOOK).read_text(encoding="utf-8"))
    raw = json.dumps(nb, ensure_ascii=False, indent=1)
    cleaned = scrub(raw)
    json.loads(cleaned)  # still valid JSON
    (dst / NOTEBOOK).write_text(cleaned + "\n", encoding="utf-8")
    return raw != cleaned


def copy_dir(src_dir, dst_dir, patterns, skip=()):
    copied = []
    if not src_dir.exists():
        print(f"  (no {src_dir.name}/ folder in the source, skipped)")
        return copied
    dst_dir.mkdir(exist_ok=True)
    for pat in patterns:
        for f in sorted(src_dir.glob(pat)):
            if f.name in skip:
                continue
            if f.suffix in (".csv", ".md"):
                (dst_dir / f.name).write_text(scrub(f.read_text(encoding="utf-8")), encoding="utf-8")
            else:
                shutil.copy2(f, dst_dir / f.name)
            copied.append(f.name)
    return copied


def privacy_check(root):
    problems = []
    for f in root.rglob("*"):
        if not f.is_file() or f.suffix not in (".ipynb", ".csv", ".md", ".py", ".txt"):
            continue
        if f.name == "prepare_repo.py":
            continue
        text = f.read_text(encoding="utf-8", errors="ignore")
        for m in HOME_RE.finditer(text):
            if m.group(2).lower() != "you":
                problems.append(f"{f.relative_to(root)}: home path ...{m.group(0)}")
        for m in EMAIL_RE.finditer(text):
            if m.group(0) not in EMAIL_OK and not m.group(0).endswith("@example.com"):
                problems.append(f"{f.relative_to(root)}: email {m.group(0)}")
    return problems


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", required=True, help="folder where you ran the notebook")
    ap.add_argument("--include-card-prices", action="store_true", help=f"also copy outputs/{CARD_PRICES}")
    a = ap.parse_args()
    src = Path(a.src).expanduser().resolve()
    if not (src / NOTEBOOK).exists():
        sys.exit(f"Can't find {NOTEBOOK} in {src}")

    print(f"Copying from {src}")
    changed = copy_notebook(src, HERE)
    print(f"  {NOTEBOOK}" + (" (home paths scrubbed)" if changed else ""))
    skip = () if a.include_card_prices else (CARD_PRICES,)
    outs = copy_dir(src / "outputs", HERE / "outputs", ["*.csv", "results_summary.md"], skip)
    print(f"  outputs/: {len(outs)} files" + ("" if a.include_card_prices else f" ({CARD_PRICES} left out)"))
    figs = copy_dir(src / "figs", HERE / "figs", ["*.png"])
    print(f"  figs/: {len(figs)} files")

    problems = privacy_check(HERE)
    if problems:
        print("\nprivacy check: FOUND SOMETHING. Fix these before pushing:")
        for p in problems:
            print("  " + p)
        sys.exit(1)
    print("\nprivacy check: clean")


if __name__ == "__main__":
    main()
