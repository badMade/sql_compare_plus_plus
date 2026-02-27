# Usage

## GUI

- Run `python sql_compare.py` with no arguments.
- Pick files, choose **Mode**, toggle **Ignore whitespace** and **Join reordering** options.
- Click **Compare** to view results; **Save Report…** to export HTML/TXT.

## CLI

```txt
python sql_compare.py FILE1.sql FILE2.sql [options]
```

Key options:

- `--mode exact|canonical|both`
- `--ignore-whitespace`
- `--join-reorder` / `--no-join-reorder`
- `--allow-left-reorder` / `--allow-full-outer-reorder`
- `--strings "SQL1" "SQL2"` or `--stdin`
- `--report out.html --report-format html|txt`

**Exit codes** integrate well with CI. See `docs/CI.md` for examples.
