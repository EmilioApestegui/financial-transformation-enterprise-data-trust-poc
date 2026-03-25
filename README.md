# Financial Transformation Enterprise Data Trust Workbench

A static Streamlit PoC designed to demonstrate enterprise finance transformation pain points:

1. **Data trust** — competing KPI definitions and no single source of truth across trading, finance, and regulatory functions.
2. **Integration reliability** — late / failed feeds and incident visibility across finance source systems.
3. **Analytics adoption** — trusted KPIs and measurable manual work reduction.

## What is included

- `app.py` — Streamlit app
- `data/financial_transformation_data_trust_poc_data.xlsx` — downloadable static sample workbook
- `scripts/bootstrap_postgres.py` — loads all workbook sheets into Postgres
- `scripts/create_static_data.py` — confirms where the packaged static data lives
- `notebooks/01_data_setup.ipynb` — lightweight notebook walkthrough
- `financial_transformation_enterprise_data_trust_poc/` — shared config and database logic

## Business context

This finance version includes:
- 15 enterprise finance KPIs in the KPI registry
- 5 deliberate discrepancy areas in KPI submissions
- a wholesale account definition issue tied to SteerCo rules
- feed health, integration incidents, data quality checks, and adoption metrics

## Railway deployment

The application automatically uses the Railway Postgres connection string when `DATABASE_URL` is present. Local postgres is only a fallback.

## Quick start

```bash
pip install -r requirements.txt
streamlit run app.py
```
