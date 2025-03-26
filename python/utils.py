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

class Postgres:
    '''
    This is an interface to query my materialized dbt models from CPD Infra onto Python as pandas dataframes.
    '''
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
        table: desired table in schema
        cols_to_query (optional): desired columns in table
        
        Queries table in schema. pandas returns a UserWarning if I pass a direct db connection (psycopg2), 
        hence why I am using a SQLAlchemy engine here.
        '''
        select_clause = ", ".join(cols_to_query) if cols_to_query else "*"
        
        query = f"SELECT {select_clause} FROM {self.schema}.{table}"
        
        result = pd.read_sql(query, 
                             con = self.create_sqlalchemy_engine())
        
        return result
    
    def query_table_expanded(self, table: str, col_filter: list, row_filter: dict) -> pd.DataFrame:
        '''
        table: desired table in schema
        col_filter: list [c_i] of relevant cols c in table
        row_filter: one-element dict {'k': [v_i]} with the key as a column in table and the value is a list of desired values
        
        If [v_i] is a list of strings, each element must be single-quoted.
        
        Queries a table in schema as such:
        
        SELECT c_1, c_2, . . . 
        FROM table
        WHERE k IN (v_1, v2, . . .)
        '''
        select_clause = ", ".join(col_filter) if col_filter else "*"

        col = list(row_filter.keys())[0]
        values_comma_separated = ", ".join(f"{i}" for i in row_filter[col])
        where_clause = f"{col} IN ({values_comma_separated})"

        query = f'''
            SELECT {select_clause}
            FROM {self.schema}.{table}
            WHERE ({where_clause})
        '''
        
        result = pd.read_sql(query, 
                             con = self.create_sqlalchemy_engine())

        return result
