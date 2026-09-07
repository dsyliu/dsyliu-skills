---
name: dsyliu-book-study-guide
description: Build a high-yield study guide from a book, textbook, PDF, or long document — chapter TL;DRs plus a selective, page-cited highlight list that mimics disciplined underlining. Use this whenever the user uploads a book or long document and asks for a study guide, chapter summaries, key takeaways, highlights, "the important sentences", notes for studying or retention, or wants to review/re-read a book efficiently. Also use when the user asks to extract main concepts chapter by chapter, or wants a reusable reference to trace ideas back to specific pages.
---

# Book Study Guide

Turn a long source text into a two-part study artifact: **chapter TL;DRs** and a **selective highlight list** with page citations. The goal is a guide the user can re-read instead of the book, and use as an index back into the book.

## Non-negotiable: copyright

The source is almost always an in-copyright book. Reproducing it — even in fragments — is not acceptable, and this constraint shapes the whole format.

- **Paraphrase by default.** Highlights are your own condensed wording, not the author's sentences.
- **Quotes under 15 words**, used sparingly, only where exact wording carries the meaning (coined terms, aphorisms, definitions). Put them in quotation marks.
- **Never** reconstruct passages by chaining short quotes, or by quoting a sentence with words elided ("..."). An abridged sentence is still reproduction.
- Aim well under **25% coverage** by word count (see `scripts/coverage_check.py`). In practice a good guide lands near 10%.

If the user asks for verbatim sentences, "the actual underlined text", or ellipsis-abridged quotes, explain the limit and offer the alternative: the guide acts as an index (paraphrase + exact page), and they mark up their own copy.

## Workflow

### 1. Read the whole source

Read it properly — don't summarize from prior familiarity with the title, even for a well-known book. Extract the full text before writing anything, and check the extraction actually worked before relying on it.

For PDFs, extract the text layer once and work from it:

```bash
pdftotext -layout source.pdf /tmp/fulltext.txt
```

Check `pdffonts` first. Archive scans often carry an invisible OCR layer (a "GlyphLessFont") — usable, but expect garbled tables and rotated figures. **Flag OCR corruption rather than guessing at it**; inventing a table's contents is worse than omitting them.

### 2. Build the page map

Page citations are the guide's main value, so derive them mechanically rather than estimating.

```bash
python scripts/page_map.py /tmp/fulltext.txt --detect
python scripts/page_map.py /tmp/fulltext.txt --find "phrase to locate"
```

The script infers the offset between PDF sheet index and printed page number from running headers, then locates any phrase's printed page. Verify the offset holds across the whole book before trusting it.

### 3. Write Part 1 — chapter TL;DRs

One to two sentences per chapter, plus preface/introduction if substantive.

Write these as **the reader's own condensed takeaways**, not as reportage about the book. Drop "Watkins argues that..." and "the chapter explains..." — state the lesson directly. If the user wants a first-person feel without the word "I", phrase as imperative or declarative insight:

- Weak: "Watkins explains that leaders should diagnose their situation before acting."
- Strong: "Diagnose the honest STARS mix before picking an approach. The situation dictates the playbook, not whichever style feels most natural."

Ask whether they want a second language alongside. If so, translate for a native ear — idiomatic phrasing, not literal correspondence — and confirm script/regional variant (e.g. Traditional vs Simplified Chinese, and Taiwan vs mainland vocabulary).

### 4. Write Part 2 — the highlights

This is the bulk of the work. Apply these principles, which come from how a disciplined reader actually marks a textbook:

**Read the full section before deciding what matters.** You can't know the load-bearing sentence until you've seen the whole argument.

**Target the author's core claims** — the thesis of each section, defined terms, named frameworks, and direct answers to the questions the headings raise.

**Be selective.** If everything is marked, nothing stands out. Aim ~10% coverage, hard ceiling 25%.

**Case studies collapse to their conclusion.** Give the narrative in one or two plain sentences, then mark only the takeaway it exists to prove. Don't highlight the plot beats.

**One idea per bullet.** Never fuse several of the author's points into a single bullet — the user needs each bullet to trace back to one specific spot. Split them.

**Every bullet gets a page citation.** Single page where the point sits on one page; a two-page range only when it genuinely straddles a break.

**Preserve source order.** Bullets follow the order ideas appear in the book, so the guide can be read alongside it. Verify this — it's easy to break while editing.

**Keep the author's enumerated lists as numbered lists.** When the book gives steps, causes, traps, or characteristics, completeness matters more than compression there; don't thin them.

**Don't repeat yourself.** If adjacent bullets say substantially the same thing, keep the one that states the principle best.

### 5. Verify before delivering

Run these checks and report what they found — they routinely surface real gaps.

**Thesis-coverage test.** For each chapter, ask: could a reader who read *only* these highlights explain the chapter's main argument? Check against the book's own signals — chapter checklists, "closing the loop" sections, summary paragraphs. Those state what the author thinks the chapter taught. Anything a checklist item asks about that no highlight covers is a genuine gap; add a bullet. Balance this against over-marking: add the missing point, don't top up thin-looking chapters.

**Order check.** Confirm page numbers ascend within each chapter.

**Coverage check.** `python scripts/coverage_check.py` — confirm under 25% overall and per chapter.

**Accuracy check.** Re-verify every statistic, named framework, and quotation against the source before delivering. Numbers and framework components are where confabulation creeps in.

## Output format

Deliver a single markdown file, and share it with the user however your environment does that.

```markdown
# [Title] — Study Guide
**[Author]** · [edition, publisher, year] · ISBN

## How to use this guide
- **Part 1** — one-to-two-sentence TL;DR per chapter.
- **Part 2** — the highlight list, organized by chapter and the book's own section headings, with page references.

# Part 1 — Chapter TL;DRs
**Chapter N — [Title] (pp. X–Y)**
[1–2 sentence takeaway.]

# Part 2 — Highlights
## Chapter N — [Title] (pp. X–Y)

**Case: [Name] (pp. X–Y)**
[One or two sentences of narrative.]
- [The takeaway it proves.] (p. X)

### [Book's own section heading] (pp. X–Y)
- [Single idea.] (p. X)
- **[Named framework]** — [what it is]. (p. X)

**[Enumerated list from the book]:**
1. **[Item].** [Gloss.] (p. X)
```

Keep the book's own section headings as the guide's structure — that's what makes it navigable against the physical book.

## Working with the user

Expect iteration; this format has a lot of dials. Common adjustments: bilingual output, tighter or looser selectivity, per-bullet vs per-section citations, voice of the TL;DRs.

When a request conflicts with the copyright constraint or with the selectivity principle, say so directly and offer the closest workable alternative rather than silently complying or flatly refusing.

Save the file to disk after each chapter on long books — it protects the work if the session runs long or is interrupted.
