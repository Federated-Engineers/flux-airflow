from plugins.lumina_utils.db_utils import get_lumina_db_connection
import pandas as pd

test_df = pd.read_sql(
    "select * from ay_test.airflow",
    con=get_lumina_db_connection()
)
print(test_df.head())
