from sqlalchemy import create_engine
import pandas as pd


def get_db_connection(connection_string: str):
    """
    The connection string should be in the format:
    "postgresql://username:password@host:port/database"

    params:
           connection_string: The connection string for the database
    """
    
    conn = create_engine(connection_string)

    return conn
        
        
        
        
# "postgresql://postgres.lksygmgwphnbbvdbgzaw:pd0S4b4DwgE0IH6L63lq@aws-1-eu-west-1.pooler.supabase.com/postgres"
        
