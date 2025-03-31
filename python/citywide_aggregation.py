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
    
    # Step 2: Plot.
    if set(config["color_map"].keys()) != set(config["column_map"].keys()):
        raise ValueError(f"Invalid column_map and color_map in {args.config_file}. "
                         "Their keys must be the same. No, I don't know why I "
                         "set this up differently in ./geocoder/garfield_park.py.")
    else:
        citywide_agg_for_plot = citywide_agg.copy()
        if args.start_year:
            citywide_agg_for_plot.query(f"arrest_year >= {args.start_year}", inplace = True)
            
        citywide_agg_for_plot.rename(columns = config["column_map"], inplace = True)

        plt.figure(figsize = (10, 6))
        for original_colname, plot_label in config["column_map"].items():
            plt.plot(citywide_agg_for_plot["arrest_year"], citywide_agg_for_plot[plot_label], 
                     marker = "o", label = plot_label, color = config["color_map"][original_colname])

        plt.title("Citywide Drug Arrests Over Time", fontsize = 15, fontweight = "bold")
        plt.yticks(range(0, args.max_y + args.y_ticks, args.y_ticks))
        plt.xticks(range(min(citywide_agg_for_plot["arrest_year"]), max(citywide_agg_for_plot["arrest_year"]) + 1), rotation = 30)
        plt.legend(loc = "upper right", fontsize = 9)
        plt.tight_layout()
    
    
    # Step 3: Export.
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents = True, exist_ok = True)
    
    base_name = "citywide_arrests"
    plot_name = f"{base_name}_{citywide_agg_for_plot.arrest_year.min()}-{citywide_agg_for_plot.arrest_year.max()}.png"
    
    citywide_agg.to_csv(output_dir.joinpath(f"{base_name}.csv"), index = False)
    plt.savefig(output_dir.joinpath(f"{plot_name}.png"))
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser("Queries and visualizes the citywide_aggregation model from CPD Infra.")
    parser.add_argument("--config_file", 
                        help = ".yml file with db_credentials, column_map, and color_map keys", 
                        default = "./python/config.yml")
    
    parser.add_argument("--start_year", help = "beginning year of plot", type = int, required = False)
    parser.add_argument("--max_y", help = "max y axis of plot", type = int, default = 65000)
    parser.add_argument("--y_ticks", help = "y axis tick of plot", type = int, default = 5000)
    
    parser.add_argument("--output_dir", default = "output")
    
    args = parser.parse_args()
    
    main(args)
