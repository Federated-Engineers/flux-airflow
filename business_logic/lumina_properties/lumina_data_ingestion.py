import pandas as pd
from airflow.models import Variable
from plugins.utils.database import get_db_connection


def extract_lumina_data():
    credentials = Variable.get("postgres_conn_string")
    test_df = pd.read_sql(
        "select * from ay_test.airflow",
        con=get_db_connection(credentials)
    )
    return test_df
