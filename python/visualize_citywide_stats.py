import matplotlib.pyplot as plt
from pathlib import Path
import argparse

from utils import Postgres, load_yaml

def main(args: argparse.Namespace):
    config = load_yaml(Path(args.config_file))
    
    # Step 1: Query materialized citywide_aggregation model in db.
    db_config = config["db_credentials"]
    db = Postgres(credentials = {k: v for k, v in db_config.items() if k != "schema"}, 
                  schema = db_config["schema"])

    citywide_agg = db.query_table("citywide_aggregation")
    citywide_agg["arrest_year"] = citywide_agg["arrest_year"].astype(int)
    
    num_cols = [cols for cols in citywide_agg.columns if cols in config["desired_counts"]]
    plot_labels = [(cols.replace("num", "").replace("_", " ").replace("poss", "possession arrests")
                    .strip().title()) 
                   for cols in num_cols
                  ]
    citywide_agg.rename(columns = {old: new for old, new in zip(num_cols, plot_labels)}, inplace = True)
    
    if args.start_year:
        citywide_agg.query(f"arrest_year >= {args.start_year}", inplace = True)


    # Step 2: Plot.
    plt.figure(figsize = (10, 6))
    for col, original_colname in zip(plot_labels, num_cols):
        plt.plot(citywide_agg["arrest_year"], citywide_agg[col], 
                 marker = 'o', label = col, color = config["color_map"][original_colname]
                )

    plt.title("Drug Arrests Over Time", fontsize = 15, fontweight = "bold")
    plt.yticks(range(0, args.max_y + args.y_ticks, args.y_ticks))
    plt.xticks(range(min(citywide_agg["arrest_year"]), max(citywide_agg["arrest_year"]) + 1), rotation = 30)
    plt.legend(loc = "upper right", fontsize = 9)
    plt.tight_layout()
    
    
    # Step 3: Export.
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents = True, exist_ok = True)
    
    citywide_agg.to_csv(output_dir.joinpath("citywide_aggregation.csv"), index = False)
    plt.savefig(
        output_dir.joinpath(
        f"drug_arrests_over_time_{citywide_agg.arrest_year.min()}-{citywide_agg.arrest_year.max()}.png"
        )
    )
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser("Queries and visualizes the citywide_aggregation model from the CPD Infra.")
    parser.add_argument("--config_file", help = ".yml file with db_credentials, color_map, and desired_counts keys", default = "./python/config.yml")
    
    parser.add_argument("--start_year", help = "beginning year of plot", type = int, required = False)
    parser.add_argument("--max_y", help = "max y axis of plot", type = int, default = 50000)
    parser.add_argument("--y_ticks", help = "y axis tick of plot", type = int, default = 5000)
    
    parser.add_argument("--output_dir", default = "output")
    
    args = parser.parse_args()
    
    main(args)