import matplotlib.pyplot as plt
import pandas as pd
import geopandas as gp
from shapely.geometry import Point
import argparse
from pathlib import Path
import yaml

from utils import create_logger

garfield_park = ["WEST GARFIELD PARK", "EAST GARFIELD PARK"]

def plot_by_year(table: pd.DataFrame, 
                 column_map: dict, 
                 color_map: dict, 
                 max_y: int,
                 y_ticks: int,
                 year_col: str = "arrest_year",
                 title: str = "Drug Arrests in Garfield Park Over Time"):
    '''
    table: table to plot with a year column
    column_map: key:value pair where key is a column in table and value is the desired name in plot
    color_map: key:value pair where key is the value in column_map and value is the desired color in plot
    max_y: maximum of y axis
    y_ticks: y axis ticks
    year_col: column in table that refers to the year
    title: title of plot
    
    creates a multi-line plot, one line for each element in column_map
    '''
    summary_for_plot = table.copy()
    
    if set(color_map.keys()) != set(column_map.values()):
        raise ValueError("Invalid column_map and color_map.")
    
    summary_for_plot.rename(columns = column_map, inplace = True)
    
    plt.figure(figsize = (10, 6))
    for col in column_map.values():
        plt.plot(summary_for_plot[year_col], summary_for_plot[col], 
                 marker = "o", label = col, color = color_map[col])
    
    plt.title(title, fontsize = 15, fontweight = "bold")
    plt.yticks(range(0, max_y + y_ticks, y_ticks))
    plt.xticks(range(min(summary_for_plot[year_col]), max(summary_for_plot[year_col]) + 1), rotation = 30)
    plt.legend(loc = "upper right", fontsize = 9)
    plt.tight_layout()

def main(args: argparse.Namespace):
    logging = create_logger(log_file = Path(args.output_dir).joinpath(f"{Path(__file__).stem}.log"))

    chicago_shp = gp.read_file(args.chi_shp)
    analytical_table = pd.read_csv(args.analytical_table)
    analytical_table_geocoded = pd.read_csv(
        args.analytical_table_geocoded, usecols = ["arrest_id", "ul_rating", "ul_lon", "ul_lat"]
    )
    
    logging.info("% missing geometry: "
                f"{round(analytical_table_geocoded.ul_rating.isna().sum() / len(analytical_table_geocoded) * 100, 2)}%"
                )
    
    
    # Step 1: Spatially join point coordinates to community area shapefile.
    table = pd.merge(analytical_table, analytical_table_geocoded, on = "arrest_id", how = "left")
    
    geo_table = gp.GeoDataFrame(
        table, geometry = [Point(x, y) for x, y in zip(table['ul_lon'], table['ul_lat'])], crs = chicago_shp.crs
    )

    logging.info(f"% uniqueness in address: {round(geo_table.arrest_address.nunique() / len(geo_table) * 100, 2)}%")
    logging.info(f"% uniqueness in geometry: {round(geo_table.geometry.nunique() / len(geo_table) * 100, 2)}%")
    
    map_table_to_shp = gp.sjoin(geo_table, chicago_shp, how = "left", predicate = "within")

    logging.info("% mapped to Garfield Park: "
                 f"{round(len(map_table_to_shp.query('community in @garfield_park')) / len(map_table_to_shp) * 100, 2)}%"
                )

    if len(map_table_to_shp) != len(geo_table):
        logging.warning(f"Spatial join resulted in {len(map_table_to_shp) - len(geo_table)} duplicated records.")
    
    
    # Step 2: Aggregate to the year level, tallying the number of opioid related and opioid possession arrests in East and West Garfield Park.
    table_out = pd.DataFrame(map_table_to_shp).query("community in @garfield_park")

    summary = (table_out
               .groupby("arrest_year")
               .agg(
                   num_drug_poss = ("num_drug_poss_charges", lambda x: (x > 0).sum()),
                   num_marijuana_poss = ("num_marijuana_poss_charges", lambda x: (x > 0).sum()),
                   num_opioid_poss = ("num_opioid_poss_charges", lambda x: (x > 0).sum()),
                   num_unknown_drug_poss = ("num_unknown_poss_charges", lambda x: (x > 0).sum()),
                   num_drug_poss_ex_marijuana_opioid_and_unknown_substances = (
                       "num_drug_poss_charges",
                       lambda x: ((x > 0) & 
                                  (table_out["num_marijuana_poss_charges"] == 0) & 
                                  (table_out["num_opioid_poss_charges"] == 0) & 
                                  (table_out["num_unknown_poss_charges"] == 0)).sum()
                   )
               )
               .reset_index()
              )

    summary["arrest_year"] = summary["arrest_year"].astype(int)
    
    
    # Step 3: Visualize.
    summary_for_plot = summary.copy()

    if args.start_year:
        summary_for_plot.query(f"arrest_year >= {args.start_year}", inplace = True)
        
    with open(args.config_file, "r") as file:
        config = yaml.safe_load(file)

    plot_by_year(summary_for_plot, column_map = config["column_map"], color_map = config["color_map"],
                 max_y = args.max_y, y_ticks = args.y_ticks)
    
    
    # Step 4: Export arrest-level table, year-level table, and year-level visualization.
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents = True, exist_ok = True)
    
    table_out_relevant_cols = [
        i for i in table_out.columns if i in \
        list(analytical_table.columns) + \
        ["ul_lon", "ul_lat", "geometry", "community"]
    ]
    
    base_name = "garfield_park_arrests"
    plot_name = f"{base_name}_{summary_for_plot.arrest_year.min()}-{summary_for_plot.arrest_year.max()}.png"
    
    table_out[table_out_relevant_cols].to_csv(output_dir.joinpath(f"{base_name}.csv"), index = False)
    summary.to_csv(output_dir.joinpath(f"{base_name}_summary.csv"), index = False)
    plt.savefig(output_dir.joinpath(f"{plot_name}.png"))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        "Takes the analytical table from ./python/query_table_from_db.py and "
        "geocoding results from ./geocoder/geocoder.py, then maps the point coordinates "
        "to Chicago's community area shapefile. Finally, an arrest-level table; year-level "
        "table; and year-level visualization are exported."
    )
    parser.add_argument("--start_year", help = "beginning year of plot", type = int, required = False)

    parser.add_argument("--max_y", help = "max y axis of plot", type = int, default = 4000)
    parser.add_argument("--y_ticks", help = "y axis tick of plot", type = int, default = 400)
    
    parser.add_argument("--config_file",
                        help = ".yml file with column_map and color_map keys",
                        default = "./geocoder/config.yml")
    
    parser.add_argument("--analytical_table", "-a",
                        help = ".csv file from ./python/query_table_from_db.py --table=analytical_table")
    
    parser.add_argument("--analytical_table_geocoded", "-b",
                        help = ".csv file from geocoding analytical_table through ./geocoder/geocode.py")
    
    parser.add_argument("--chi_shp", "-c",
                        help = ".shp file of Chicago at the community area level")
    
    parser.add_argument("--output_dir", default = "output")

    args = parser.parse_args()
    
    main(args)
