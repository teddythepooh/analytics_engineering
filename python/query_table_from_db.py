from pathlib import Path
import pandas as pd
import argparse

from utils import Postgres, load_yaml

def main(args: argparse.Namespace) -> pd.DataFrame:
    config = load_yaml(Path(args.config_file))
    db_config = config["db_credentials"]
    db = Postgres(credentials = {k: v for k, v in db_config.items() if k != "schema"}, 
                  schema = db_config["schema"])
    
    if args.all:
        table = db.query(args.table)
    else:
        query_params = config["expanded_query_params"][args.table]

        select_clause = query_params["col_filter"]
        where_clause = {query_params["row_filter"]["key"]: query_params["row_filter"]["values"]}
        
        table = db.query_table_expanded(
            args.table, 
            col_filter = select_clause,
            row_filter = where_clause
        )
    
    return table

if __name__ == "__main__":
    parser = argparse.ArgumentParser("Queries a table in CPD Infra and exports it to .csv.")

    parser.add_argument("--table", 
                        help = "name of dbt model materialized on schema specified in config_file",
                        default = "analytical_table")
    
    parser.add_argument("--all", action = "store_true",
                        help = "whether to query the entire table or apply filters beforehand")

    parser.add_argument("--config_file", 
                        help = (".yml file with db_credentials and expanded_query_params keys;"
                                "table must be present under expanded_query_params when --all is not passed"
                               ), 
                        default = "./python/config.yml")

    parser.add_argument("--output_dir", default = "output")
    
    args = parser.parse_args()
    
    table = main(args)
    
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents = True, exist_ok = True)
    
    table.to_csv(output_dir.joinpath(f"{args.table}.csv"), index = False)
