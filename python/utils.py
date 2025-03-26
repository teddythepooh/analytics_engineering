import pandas as pd
import sqlalchemy
import psycopg2
import os
from pathlib import Path
import yaml
from getpass import getpass

def load_yaml(file: Path) -> dict:
    try:
        with open(file, "r") as file:
            return yaml.safe_load(file)
    except FileNotFoundError:
        raise FileNotFoundError(f"{file} not found.")

def build_db_credentials(port, host, database) -> dict:
    return {
        "port": port,
        "host": host,
        "database": database
    }

class Postgres:
    def __init__(self, 
                 credentials: dict, 
                 schema: list, 
                 configure_secrets_interactively: bool = False) -> None:
        '''
        credentials: a dictionary with port, host, and database keys
        schema: the schema where the materialized dbt models are stored
        configure_secrets_interactively: whether to pull your db user/pw interactively or as env vars
        '''
        self.credentials = credentials
        self.schema = schema
        self.configure_secrets_interactively = configure_secrets_interactively

    def _build_sqlalchemy_url(self) -> sqlalchemy.URL:
        if self.configure_secrets_interactively:
            db_user = getpass("Enter CNet ID:")
            db_password = getpass("Enter CNet password:")
        else:
            db_user = os.environ["DBT_USER"]
            db_password = os.environ["DBT_PASSWORD"]
            
        credentials = self.credentials
        url = sqlalchemy.URL.create(
            "postgresql+psycopg2",
            port = credentials["port"],
            host = credentials["host"],
            database = credentials["database"],
            username = db_user,
            password = db_password
        )
        
        return url

    def create_sqlalchemy_engine(self) -> sqlalchemy.Engine:
        engine = sqlalchemy.create_engine(self._build_sqlalchemy_url())
        
        return engine
    
    def query_table(self, table: str, cols_to_query: list = "*") -> pd.DataFrame:
        '''
        table: desired table in schema.
        cols_to_query (optional): desired columns in table
        
        Queries table in schema. pandas returns a UserWarning if I pass a direct db connection (psycopg2), 
        hence why I am using a SQLAlchemy engine here.
        '''
        if cols_to_query == "*":
            cols = cols_to_query
        else:
            cols = ", ".join(cols_to_query)
        
        result = pd.read_sql(f"SELECT {cols} FROM {self.schema}.{table}", 
                             con = self.create_sqlalchemy_engine())
        
        return result