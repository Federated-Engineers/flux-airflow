import pandas as pd
from plugins.utils.database import get_db_connection


def extract_lumina_data():
    test_df = pd.read_sql(
        "select * from ay_test.airflow",
        con=get_db_connection(
            "postgresql://postgres.lksygmgwphnbbvdbgzaw:pd0S4b4DwgE0IH6L63lq@aws-1-eu-west-1.pooler.supabase.com/postgres"
        )
    )
    return test_df
