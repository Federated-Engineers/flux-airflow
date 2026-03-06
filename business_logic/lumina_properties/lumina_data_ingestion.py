import os

import pandas as pd
from airflow.models import Variable
from plugins.utils.database import get_db_connection


def extract_lumina_data():
    credentials = Variable.get("postgres_conn_string")
    conn=get_db_connection(credentials)
    
    temp_dir = "/opt/airflow/temp"
    os.makedirs(temp_dir, exist_ok=True)

    tables= [
        "ay_test.airflow",
        "ay_test.property",
        "ay_test.renovation_legders"
    ]

    for table_name in tables:
        query =  f"SELECT * FROM {table_name}"

        try:
            chunk_filter = pd.read_sql(query, con=conn, chunksize=40000)
            
            for i, chunk_df in enumerate(chunk_filter):
                local_file = os.path.join(temp_dir, f"{table_name}_batch_{i}.parquet")

                
                # to local
                chunk_df.to_parquet(local_file)


                # os.remove(local_file)

        except Exception as e:
            raise ValueError(
                f"Could not read {table_name}. Error: {str(e)}"
                )



    return "Extraction was Successful"


# import os
# print(dir(os))