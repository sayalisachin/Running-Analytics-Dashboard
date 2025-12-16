# Running Analytics Dashboard 🏃

Streamlit app for the running analytics challenge: upload a CSV of runs (date, person, miles run, optional minutes) to see validation, metrics, charts, goals, outliers, and exports.

## 1) Project Overview
- Challenge: running-data visualization and metrics with CSV upload.
- What was built: Streamlit dashboard with validation, filters, charts (overall and per-person), weekly/monthly summaries, goal tracking, pace/calorie estimates, outlier detection, and CSV exports.

## 2) Assumptions
- CSV columns: `date`, `person`, `miles run` are required; optional `minutes` for actual pace. Distances are in miles. Dates are UTC-like (no timezone handling).
- Calories use a simple multiplier (default 100 cal/mile) and are approximate.
- Pace fallback uses a user-provided default if `minutes` is missing.
- Weekly goal is compared to the last 7 days ending at the latest date in the filtered data.
- No authentication; data is in-memory only.

## 3) Prerequisites
- Python 3.10+ (tested on 3.13). pip available.
- Node/DB not required.

## 4) Setup
- Install deps (inside repo):
  - `pip install streamlit pandas plotly`
- Env: none required; no secrets. If using a venv: `python -m venv .venv && .venv/Scripts/activate` (Windows).
- Seed data: use provided sample [sample_runs.csv](sample_runs.csv).

## 5) Run & Verify
- Start: `streamlit run app.py` (or `python -m streamlit run app.py` if PATH lacks `streamlit`).
- Upload: use [sample_runs.csv](sample_runs.csv) (has required columns; add `minutes` to test pace).
- Validate acceptance items step-by-step:
  1. Bad CSV (missing a column) → upload edited file; expect clear validation errors.
  2. Good CSV → see success, filtered preview, metrics, charts.
  3. Filters → use sidebar date range and runner multiselect; data updates across metrics/charts.
  4. Metrics → check totals/avg/min/max/run count plus calories for both overall and per-person tables.
  5. Charts → confirm time-series by person, bar totals, histograms, weekly/monthly bars.
  6. Goals → set weekly goal; progress bar updates.
  7. Pace/calories → add `minutes` column; pace recalculates. Without `minutes`, fallback pace is used.
  8. Outliers → extreme values per person are flagged in the outlier table.
  9. Export → download filtered data and per-person stats via the two download buttons.

## 6) Features & Limitations
- Works: validation, filters, metrics (overall and per-person), pace/calories, goals, weekly/monthly summaries, outliers, exports, theme toggle (light/dark), optional `minutes` column.
- Known gaps: no auth, no persistence, simple calorie model, no timezone handling, no automated tests.
- Future: add unit tests, richer goal tracking (per-runner), anomaly tuning, SSO, and saved views.

## 7) Notes on Architecture
- Framework: Streamlit single-page app; all logic in [app.py](app.py).
- Data flow: CSV → pandas DataFrame → validation → filtered DataFrame → derived metrics/aggregations → Plotly charts and tables.
- State: transient in-memory; filters read from sidebar widgets.
- Structure: inline sections for validation, filters, metrics, charts, per-person views, exports. No backend or DB.

## 8) Accessibility & UI
- Labels and helper text on inputs; sidebar groups related controls.
- Color/contrast: Plotly templates (light/dark) to improve contrast; titles and axes labeled.
- Spacing/typography: wide layout, column splits to reduce scroll, tables use container width.
- Focus/keyboard: standard Streamlit components (tabbable inputs/buttons). Use light theme if dark contrast is inadequate for your environment.

## CSV Format

Required columns: `date` (YYYY-MM-DD), `person` (text), `miles run` (positive number). Optional: `minutes` (total minutes for the run).

### Sample CSV (sample_runs.csv)

```csv

2025-12-01,Alice,5.2,52
2025-12-02,Bob,3.1,32
2025-12-02,Alice,4.5,45
2025-12-03,Alice,6.0,58
2025-12-03,Bob,2.8,30
2025-12-04,Charlie,4.2,44
2025-12-04,Alice,5.5,55
2025-12-05,Bob,3.5,36
2025-12-05,Charlie,4.8,50
2025-12-06,Alice,7.1,70
2025-12-07,Bob,3.2,34
2025-12-07,Charlie,5.0,52
2025-12-08,Alice,4.8,48
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Missing required columns | Ensure `date`, `person`, `miles run` exist (and optionally `minutes`). |
| Non-numeric values | `miles run` and `minutes` must be numeric; remove text like "5 miles". |
| Invalid dates | Use YYYY-MM-DD. |
| Empty/filtered-out data | Relax filters or date range in sidebar. |
| `streamlit` not found | Run `pip install streamlit` or use `python -m streamlit run app.py`. |

## License

MIT License.
4. **Explore Per-Person Data**: Select a runner from the dropdown to see their specific metrics and charts
