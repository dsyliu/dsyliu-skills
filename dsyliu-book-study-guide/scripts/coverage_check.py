#!/usr/bin/env python3
"""
Measure how much of the source the study guide's highlights cover.

Over-marking defeats the purpose of a study guide: if everything is marked,
nothing stands out, and the guide stops being faster to re-read than the book.
This enforces the ceiling. A good guide lands near 10%; 25% is the hard limit.

Counts only highlight prose -- section headings and page citations are
navigational scaffolding, not marked content, so they're excluded.

Usage:
    # Whole guide against a page range of the book:
    python coverage_check.py --guide guide.md --text /tmp/fulltext.txt \
        --offset 21 --pages 1-257

    # Per-chapter breakdown (chapter -> book page range):
    python coverage_check.py --guide guide.md --text /tmp/fulltext.txt \
        --offset 21 --pages 1-257 --per-chapter
"""

import argparse
import re
import sys

CEILING = 25.0
TARGET = 10.0


def book_word_count(textfile, offset, first, last, strip_headers=True):
    with open(textfile, encoding="utf-8", errors="replace") as f:
        sheets = f.read().split("\f")
    words = 0
    for p in range(first, last + 1):
        idx = p + offset
        if 0 <= idx < len(sheets):
            t = sheets[idx]
            if strip_headers:
                # drop all-caps running titles so headers don't inflate the source
                t = re.sub(r"^\s*\d{0,4}\s*[A-Z][A-Z .,'’-]{5,}\s*$", "", t,
                           flags=re.MULTILINE)
            words += len(t.split())
    return words


def parse_guide(guide_path):
    """
    Return (total_highlight_words, {chapter_heading: words}).

    Counts bullets and numbered items after the 'Part 2' marker. Skips
    headings, tables, and page citations.
    """
    with open(guide_path, encoding="utf-8", errors="replace") as f:
        lines = f.readlines()

    start = 0
    for i, l in enumerate(lines):
        if re.match(r"^#+\s*Part 2", l, re.I):
            start = i
            break

    chapters = {}
    current = None
    total = 0
    for l in lines[start:]:
        s = l.strip()
        if not s:
            continue
        if s.startswith("## "):
            current = s.lstrip("# ").strip()
            chapters.setdefault(current, 0)
            continue
        if s.startswith("#") or s.startswith("|"):
            continue
        if not re.match(r"^(-|\*|\d+\.)\s", s):
            continue
        s = re.sub(r"\((?:pp?\.)[^)]*\)", "", s)   # page citations
        s = re.sub(r"^(-|\*|\d+\.)\s*", "", s)     # bullet marker
        s = re.sub(r"[*_`#]", "", s)               # markdown emphasis
        n = len(s.split())
        total += n
        if current:
            chapters[current] += n
    return total, chapters


def verdict(pct):
    if pct > CEILING:
        return "OVER LIMIT — cut the least load-bearing bullets"
    if pct > TARGET * 1.6:
        return "ok, but on the heavy side"
    return "good"


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--guide", required=True, help="the study guide markdown file")
    ap.add_argument("--text", required=True, help="output of `pdftotext -layout`")
    ap.add_argument("--offset", type=int, required=True,
                    help="sheet->page offset (from page_map.py --detect)")
    ap.add_argument("--pages", required=True, metavar="FIRST-LAST",
                    help="printed page range of the book body, e.g. 1-257")
    ap.add_argument("--per-chapter", action="store_true",
                    help="also show a per-chapter word breakdown")
    args = ap.parse_args()

    m = re.fullmatch(r"(\d+)-(\d+)", args.pages.strip())
    if not m:
        sys.exit("--pages must look like 1-257")
    first, last = int(m.group(1)), int(m.group(2))

    book = book_word_count(args.text, args.offset, first, last)
    total, chapters = parse_guide(args.guide)

    if book == 0:
        sys.exit("No source words found — check --offset and --pages.")

    pct = total / book * 100
    print(f"Book body (pp. {first}-{last}): {book:,} words")
    print(f"Highlight prose:              {total:,} words")
    print(f"Coverage:                     {pct:.1f}%   [{verdict(pct)}]")
    print(f"(target ~{TARGET:.0f}%, hard ceiling {CEILING:.0f}%)")

    if args.per_chapter and chapters:
        print("\nPer-chapter highlight volume:")
        widest = max(len(c) for c in chapters)
        for name, words in chapters.items():
            share = words / total * 100 if total else 0
            print(f"  {name:<{widest}}  {words:>5} words  ({share:4.1f}% of highlights)")
        print("\nNote: chapter shares are of total highlights, not of the book. "
              "To get a true per-chapter ratio, rerun with --pages set to that "
              "chapter's page range.")


if __name__ == "__main__":
    main()
