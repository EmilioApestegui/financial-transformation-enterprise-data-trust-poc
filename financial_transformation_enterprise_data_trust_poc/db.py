from __future__ import annotations

import os
import numpy as np
import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

from .config import WORKBOOK_PATH, export_paths


def app_engine():
    database_url = os.getenv("DATABASE_URL")
    if database_url:
        return create_engine(database_url)
    return create_engine(
        "postgresql+psycopg2://postgres:postgres@localhost:5432/financial_transformation_enterprise_data_trust_poc"
    )


def test_connection(engine: Engine):
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))


def load_workbook_to_postgres(engine: Engine, workbook_path=None):
    workbook = pd.read_excel(workbook_path or WORKBOOK_PATH, sheet_name=None)
    loaded = {}

    for table_name, df in workbook.items():
        for col in df.columns:
            if (
                "date" in col
                or "month_start" in col
                or col.endswith("_at")
                or col.endswith("_time")
            ):
                try:
                    df[col] = pd.to_datetime(df[col])
                except Exception:
                    pass

        df.to_sql(table_name, engine, if_exists="replace", index=False)
        loaded[table_name] = len(df)

    return loaded


def run_certified_pipeline(engine: Engine):
    actuals = pd.read_sql("sales_actuals", engine)
    plan = pd.read_sql("sales_plan", engine)

    summary = (
        actuals.groupby(
            ["month_start", "region", "product_category"],
            as_index=False
        )
        .agg(
            actual_revenue=("net_revenue", "sum"),
            gross_sales=("gross_sales", "sum"),
            adjustments=("returns_amount", "sum"),
            transaction_count=("units_sold", "sum"),
            open_balance_items=("inventory_on_hand", "sum"),
            missing_feeds=("feed_received_flag", lambda s: int((s != "Y").sum()))
        )
        .merge(
            plan[
                [
                    "month_start",
                    "region",
                    "product_category",
                    "plan_revenue",
                    "plan_units",
                ]
            ],
            on=["month_start", "region", "product_category"],
            how="left"
        )
    )

    summary["variance"] = summary["actual_revenue"] - summary["plan_revenue"].fillna(0)

    summary["variance_pct"] = np.where(
        summary["plan_revenue"].fillna(0) != 0,
        summary["variance"] / summary["plan_revenue"].fillna(0),
        np.nan
    )

    summary["kpi_status"] = np.where(
        summary["plan_revenue"].isna() | (summary["missing_feeds"] > 0),
        "Pending Review",
        "Certified"
    )

    summary["owner"] = "Head of Finance Transformation"
    summary["definition"] = "Finance revenue after approved close adjustments and policy-aligned exclusions"

    summary.to_sql(
        "certified_sales_summary",
        engine,
        if_exists="replace",
        index=False
    )

    return summary


def get_before_state(engine):
    df = pd.read_sql("kpi_submissions", engine)
    if df.empty:
        return df

    pivot = (
        df.pivot_table(
            index=["report_month", "kpi_name"],
            columns="function_name",
            values="reported_value",
            aggfunc="first"
        )
        .reset_index()
    )

    dept_cols = [c for c in pivot.columns if c not in ["report_month", "kpi_name"]]
    pivot["spread"] = pivot[dept_cols].max(axis=1) - pivot[dept_cols].min(axis=1)
    return pivot.sort_values(["report_month", "kpi_name"]).reset_index(drop=True)


def get_kpi_registry(engine):
    return pd.read_sql("kpi_registry", engine)


def get_feed_monitor(engine):
    return pd.read_sql("feed_monitor", engine)


def get_incidents(engine):
    return pd.read_sql("integration_incidents", engine)


def get_dq_results(engine):
    return pd.read_sql("data_quality_results", engine)


def get_issue_log(engine):
    return pd.read_sql("issue_log", engine)


def get_adoption(engine):
    return pd.read_sql("analytics_adoption", engine)


def export_summary_to_desktop(df):
    paths = export_paths()
    df.to_excel(paths["xlsx"], index=False)
    df.to_csv(paths["csv"], index=False)
    return paths
