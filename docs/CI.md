# CI/CD Integration

Use canonical mode in PR validation to ensure semantically-equivalent SQL passes, while catching meaningful changes.

## GitHub Actions
```yaml
name: SQL Compare
on: [pull_request]
jobs:
  compare:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - name: Compare SQL
        run: |
          python sql_compare.py sql/queryA.sql sql/queryB.sql \
            --mode canonical \
            --join-reorder --allow-left-reorder --allow-full-outer-reorder \
            --report compare.html --report-format html
      - name: Upload report
        uses: actions/upload-artifact@v4
        if: always()
        with:
          name: sql-compare-report
          path: compare.html
```

## Azure Pipelines
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
