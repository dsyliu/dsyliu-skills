#!/usr/bin/env python3
"""
Map PDF sheet index -> printed page number, and locate phrases by printed page.

Books rarely start printed page 1 on PDF sheet 1 (front matter, covers, scan
artifacts). Citations are the study guide's main value, so derive the offset
mechanically from running headers instead of estimating it.

Usage:
    # Extract text first:
    pdftotext -layout book.pdf /tmp/fulltext.txt

    # Infer the offset and check that it's stable:
    python page_map.py /tmp/fulltext.txt --detect

    # Find which printed page a phrase appears on:
    python page_map.py /tmp/fulltext.txt --find "break-even point"

    # Dump one printed page (to read it or verify a citation):
    python page_map.py /tmp/fulltext.txt --page 42

    # If auto-detection fails, supply the offset yourself:
    python page_map.py /tmp/fulltext.txt --find "phrase" --offset 21
"""

import argparse
import re
import sys
from collections import Counter


def load_sheets(path):
    """Split extracted text into sheets on form feeds (pdftotext page breaks)."""
    with open(path, encoding="utf-8", errors="replace") as f:
        return f.read().split("\f")


def candidate_page_numbers(sheet):
    """
    Pull plausible printed page numbers from a sheet's running headers/footers.

    Looks only at the first and last few lines, where headers and folios live.
    Body text is full of numbers that would otherwise create false positives.
    """
    lines = [ln.strip() for ln in sheet.splitlines() if ln.strip()]
    if not lines:
        return []
    edges = lines[:3] + lines[-3:]
    nums = []
    for ln in edges:
        # bare folio, e.g. "42"
        m = re.fullmatch(r"(\d{1,4})", ln)
        if m:
            nums.append(int(m.group(1)))
            continue
        # "42  RUNNING TITLE"  /  "Running Title   42"
        m = re.match(r"^(\d{1,4})\s+\D{3,}", ln)
        if m:
            nums.append(int(m.group(1)))
        m = re.search(r"\D{3,}\s+(\d{1,4})$", ln)
        if m:
            nums.append(int(m.group(1)))
    return nums


def detect_offset(sheets, verbose=False):
    """
    Infer offset where: printed_page = sheet_index - offset.

    Takes the most common offset across all sheets. A dominant single value
    means a clean, stable mapping; a scattered distribution means the book
    has multiple numbering sequences (or OCR is mangling the folios).
    """
    votes = Counter()
    for idx, sheet in enumerate(sheets):
        for n in candidate_page_numbers(sheet):
            if 0 < n < len(sheets) + 50:
                votes[idx - n] += 1
    if not votes:
        return None, votes
    if verbose:
        print("Top offset candidates (offset: votes):")
        for off, count in votes.most_common(5):
            print(f"  {off:>4}: {count}")
    return votes.most_common(1)[0][0], votes


def normalize(text):
    return re.sub(r"\s+", " ", text).strip().lower()


def find_phrase(sheets, offset, phrase):
    """Return printed page numbers where a phrase occurs (whitespace-insensitive)."""
    needle = normalize(phrase)
    hits = []
    for idx, sheet in enumerate(sheets):
        if needle in normalize(sheet):
            hits.append(idx - offset)
    return hits


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("textfile", help="output of `pdftotext -layout`")
    ap.add_argument("--detect", action="store_true",
                    help="infer and report the sheet->page offset")
    ap.add_argument("--find", metavar="PHRASE",
                    help="report printed page(s) containing PHRASE")
    ap.add_argument("--page", type=int, metavar="N",
                    help="print the text of printed page N")
    ap.add_argument("--offset", type=int,
                    help="override auto-detected offset")
    args = ap.parse_args()

    sheets = load_sheets(args.textfile)

    offset = args.offset
    if offset is None:
        offset, votes = detect_offset(sheets, verbose=args.detect)
        if offset is None:
            sys.exit("Could not detect page numbering. Pass --offset explicitly "
                     "after checking a known page by eye.")
        if args.detect:
            total = sum(votes.values())
            share = votes[offset] / total * 100
            print(f"\nDetected offset: {offset}  "
                  f"(printed_page = sheet_index - {offset})")
            print(f"Confidence: {share:.0f}% of {total} header votes agree.")
            if share < 60:
                print("WARNING: low agreement — the book may have multiple "
                      "numbering sequences, or OCR is mangling folios. "
                      "Spot-check before trusting citations.")
            print(f"Sheet count: {len(sheets)}  ->  "
                  f"printed pages ~{-offset} to {len(sheets) - offset - 1}")

    if args.find:
        hits = find_phrase(sheets, offset, args.find)
        if hits:
            print(f"'{args.find}' -> printed page(s): "
                  f"{', '.join(str(h) for h in hits)}")
        else:
            print(f"'{args.find}' not found. Try a shorter or distinctive "
                  f"fragment; OCR may differ from what you expect.")

    if args.page is not None:
        idx = args.page + offset
        if 0 <= idx < len(sheets):
            print(sheets[idx])
        else:
            sys.exit(f"Printed page {args.page} is outside this document.")


if __name__ == "__main__":
    try:
        main()
    except BrokenPipeError:
        # piping into `head` closes stdout early; not an error worth reporting
        sys.stderr.close()
