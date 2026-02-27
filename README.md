# SQL Compare (GUI + CLI) — Pure Python, Notepad++ Friendly

A portable, standard‑library only tool to compare two SQL statements:

- **GUI** (Tkinter) file picker and diff viewer
- **CLI** for automation and CI/CD
- **Color‑coded HTML/TXT reports** with summaries
- **Canonical comparison** that ignores harmless reordering:
  - Order‑insensitive **SELECT list**
  - Order‑insensitive **WHERE AND** terms
  - Optional **JOIN reordering** (INNER/CROSS/NATURAL by default). You can globally disable join reordering or optionally include **FULL OUTER** and **LEFT** JOINs.
- **Whitespace‑only mode**

> ⚠️ JOIN reordering for **LEFT** and **FULL OUTER** is **heuristic** and not always semantics‑preserving. Use the flags only if this matches your expectations.

---

## Requirements

- **Python 3.8+**
- Tkinter available (default on most Windows Python installers). If Tkinter is missing, use CLI mode.

No third‑party packages are required.

---

## Quick Start

### Run the GUI

```bash
python sql_compare.py
```

Use **Browse…** to pick two `.sql` files → choose **Mode** → toggles as needed → **Compare** → **Save Report…**.

### Run from Notepad++

1. **Save** `sql_compare.py` somewhere on disk.
2. In Notepad++: **Run → Run…**
3. Enter:

   ```txt
   python "C:\\path\\to\\sql_compare.py"
   ```

4. Click **Save…** to bind a shortcut (optional).

### CLI Examples

```bash
# Canonical compare with HTML report (color diff)
python sql_compare.py A.sql B.sql --mode canonical --report compare.html --report-format html

# Exact compare; treat whitespace-only diffs as equal
python sql_compare.py --strings "select a,b from t" "select a ,  b from t" --mode exact --ignore-whitespace

# Pipe two statements separated by a line containing only '---'
type examples/two_queries.txt | python sql_compare.py --stdin --mode both --report out.txt --report-format txt
```

---

## Options (CLI)

- `--mode exact|canonical|both` — which diffs to render and which equality to enforce for exit code.
- `--ignore-whitespace` — consider whitespace‑only differences equal (useful with `--mode exact`).
- **Join reordering controls**:
  - `--join-reorder` / `--no-join-reorder` — globally enable/disable join reordering (default: enabled).
  - `--allow-left-reorder` — also reorder LEFT JOIN runs (heuristic).
  - `--allow-full-outer-reorder` — also reorder FULL OUTER JOIN runs (heuristic).
- Inputs:
  - `file1 file2` — two paths
  - `--strings "SQL1" "SQL2"`
  - `--stdin` — read two parts separated by a line `---`
- Reports:
  - `--report <path>` — write a report
- `--report-format html|txt`

### Exit codes

- `--mode exact`: success if **whitespace‑equal** (when `--ignore-whitespace`) otherwise **exact‑token equal**.
- `--mode canonical|both`: success if **canonical equal**.

---

## What “Canonical” means

The tool transforms both SQL statements before comparison by:

- Removing comments, collapsing whitespace, uppercasing **outside quotes**, removing trailing semicolon.
- Sorting **top‑level SELECT** item list.
- Sorting **top‑level WHERE** `AND` terms.
- (If enabled) Reordering **contiguous, top‑level runs** of reorderable JOINs:
  - Always reorder: `INNER`, `CROSS`, `NATURAL`
  - Optional: `LEFT` (with `--allow-left-reorder`) and `FULL` (with `--allow-full-outer-reorder`)

> No deep SQL parsing—robust heuristics only. Nested subqueries and vendor specifics are compared as written.

---

## Reports

- **HTML** (recommended): Color‑coded inline diffs for normalized and canonical forms + a **summary of differences** (SELECT, WHERE, JOINs, token counts) and a legend.
- **TXT**: Unified diffs + summary.

---

## CI/CD Examples

### GitHub Actions

```yaml
name: SQL Compare
on: [pull_request]
jobs:
  compare:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: '3.11' }
      - name: Compare SQL (canonical)
        run: |
          python sql_compare.py sql/queryA.sql sql/queryB.sql \
            --mode canonical \
            --join-reorder --allow-left-reorder --allow-full-outer-reorder \
            --report compare.html --report-format html
      - name: Upload report artifact
        uses: actions/upload-artifact@v4
        if: always()
        with:
          name: sql-compare-report
          path: compare.html
```

### Azure Pipelines

```yaml
pool: { vmImage: 'windows-latest' }
steps:
  - task: UsePythonVersion@0
    inputs: { versionSpec: '3.11' }
  - powershell: |
      python sql_compare.py sql/queryA.sql sql/queryB.sql `
        --mode canonical `
        --join-reorder --allow-left-reorder --allow-full-outer-reorder `
        --report compare.html --report-format html
    displayName: Run SQL Compare
  - task: PublishBuildArtifacts@1
    inputs:
      PathtoPublish: 'compare.html'
      ArtifactName: 'sql-compare-report'
      publishLocation: 'Container'
```

---

## License

MIT — see [LICENSE](LICENSE).

## Acknowledgements

Built with Python standard library: `tkinter`, `difflib`, `argparse`, `re`.
