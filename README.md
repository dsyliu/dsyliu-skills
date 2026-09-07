# dsyliu-skills

A collection of [Claude Skills](https://docs.claude.com/en/docs/agents-and-tools/agent-skills/overview) — self-contained methodology documents that teach Claude to do a specific task well, plus any scripts that task needs.

## Skills

| Skill | What it does |
|---|---|
| [dsyliu-book-study-guide](dsyliu-book-study-guide/) | Turns a book, textbook, or long PDF into a study guide: chapter TL;DRs plus a selective, page-cited highlight list that mimics disciplined underlining. |

## Repository layout

Each skill is one top-level directory, self-contained and independently installable:

```
<skill-name>/
├── SKILL.md      # the methodology, with YAML frontmatter Claude uses to decide when to load it
├── README.md     # human-facing docs
├── LICENSE
└── scripts/      # optional standalone helpers
```

## Installing a skill

Package the directory and install the resulting file via the Claude app, or drop the directory straight into your skills folder:

```bash
python -m zipfile -c <skill-name>.skill <skill-name>/
```

The packaged `*.skill` files are build artifacts and are not committed — rebuild them with the command above.

## Using these outside Claude

Each `SKILL.md` is plain markdown. You can feed one to another model as a prompt or follow it yourself as a checklist. The only Claude-specific piece is the YAML frontmatter at the top, which other tools ignore harmlessly. Bundled scripts are standalone and have no dependency on any assistant.

## License

MIT — see each skill's `LICENSE`.

Licenses cover the skills and their scripts only. Anything you generate with them is derived from whatever source you supply, and that source's copyright is unaffected.
