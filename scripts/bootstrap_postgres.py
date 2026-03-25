from __future__ import annotations

from financial_transformation_enterprise_data_trust_poc.db import app_engine, load_workbook_to_postgres, test_connection

if __name__ == "__main__":
    engine = app_engine()
    test_connection(engine)
    loaded = load_workbook_to_postgres(engine)
    print("Loaded tables:", loaded)
