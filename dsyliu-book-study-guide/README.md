# dsyliu-book-study-guide

A [Claude Skill](https://docs.claude.com/en/docs/agents-and-tools/agent-skills/overview) that turns a book, textbook, or long PDF into a high-yield study guide: chapter TL;DRs plus a selective, page-cited highlight list that mimics disciplined underlining.

## What it produces

A single markdown file in two parts:

- **Part 1 — Chapter TL;DRs.** One to two sentences per chapter, written as the reader's own takeaways rather than reportage about the book. Optionally bilingual.
- **Part 2 — Highlights.** A page-cited bullet list organized under the book's own section headings, so the guide doubles as an index back into the physical book.

## Design principles

The highlight list follows how a disciplined reader actually marks a textbook:

- **Read the full section before marking** — you can't identify the load-bearing sentence until you've seen the whole argument.
- **Be selective.** If everything is marked, nothing stands out. Targets ~10% coverage of the source, hard ceiling 25%.
- **Case studies collapse to their conclusion** — the narrative in a sentence or two, then only the takeaway it exists to prove.
- **One idea per bullet**, each with its own page citation, so every bullet traces back to one specific spot.
- **Source order preserved**, so the guide can be read alongside the book.
- **The author's enumerated lists stay complete** — where the book gives steps, causes, or traps, completeness beats compression.

## Copyright

The skill paraphrases rather than reproducing the source. Quotes are kept under 15 words and used sparingly, only where exact wording carries the meaning. It will not produce verbatim passages or ellipsis-abridged sentences, since an abridged sentence is still reproduction. The intended use is that the guide serves as an index — paraphrase plus exact page — and you mark up your own copy.

## Scripts

Both are standalone and usable outside the skill. They need Python 3 and `pdftotext` (poppler-utils).

```bash
# Extract the text layer first
pdftotext -layout book.pdf /tmp/fulltext.txt
```

**`scripts/page_map.py`** — derives the offset between PDF sheet index and printed page number from running headers, so citations are mechanical rather than estimated.

```bash
python scripts/page_map.py /tmp/fulltext.txt --detect
python scripts/page_map.py /tmp/fulltext.txt --find "break-even point"
python scripts/page_map.py /tmp/fulltext.txt --page 84
```

Reports a confidence score. Books with multiple numbering sequences (roman-numeral front matter, multi-volume works) may need `--offset` supplied manually; the script warns when confidence is low.

**`scripts/coverage_check.py`** — measures highlight coverage against the source to enforce the selectivity ceiling.

```bash
python scripts/coverage_check.py --guide guide.md --text /tmp/fulltext.txt \
    --offset 21 --pages 1-257 --per-chapter
```

## Quality checks the skill runs

- **Thesis-coverage test** — for each chapter, could a reader who read only the highlights explain the chapter's argument? Checked against the book's own chapter checklists and summary sections, which state what the author thinks the chapter taught.
- **Order check** — page numbers ascend within each chapter.
- **Coverage check** — under the ceiling, overall and per chapter.
- **Accuracy check** — every statistic, named framework, and quotation re-verified against the source.

## Installation

Package the folder and install via the Claude app, or drop the directory into your skills folder:

```bash
python -m zipfile -c dsyliu-book-study-guide.skill dsyliu-book-study-guide/
```

## Using this outside Claude

The method and the scripts are tool-agnostic. `SKILL.md` is a plain markdown methodology document — you can feed it to another model as a prompt, or follow it yourself as a checklist, and get the same artifact. The two scripts are standalone Python 3 with no dependency on any assistant.

The only Claude-specific piece is the YAML frontmatter at the top of `SKILL.md`, which is how Claude decides when to load a skill. Other tools ignore it harmlessly.

## License

MIT — see [LICENSE](LICENSE).

Note that this covers the skill and its scripts only. Study guides you generate are derived from whatever source you feed in, and that source's copyright is unaffected by this license.

## Notes

Built and refined against *The First 90 Days* (Watkins, 2013). The scripts are tested against that book; the auto-detected page offset matched a hand-derived value at 78% confidence.
