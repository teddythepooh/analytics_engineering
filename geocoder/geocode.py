import argparse
from pathlib import Path

from ul_geocoder.geocoders import ChicagoCacheGeocoder

def main(args: argparse.Namespace):
    geocoder = ChicagoCacheGeocoder(batch_size = args.batch_size)

    geocoder.run(
        args.input_path,
        Path(args.output_dir).joinpath(f"{Path(args.input_path).stem}_geocoded.csv"),
        full_address_col = args.address_col,    
        validate = False,                 # validate flag
        validate_skip = False,            # validate and skip flag
        clean = True,                     # clean flag
        impute_street_type_thresh = None, # flag for imputing street type
    ) 

if __name__ == "__main__":
    parser = argparse.ArgumentParser("Geocodes a .csv file with a full address column.")
    parser.add_argument("--input_path", help = "path to .csv file to geocode")
    parser.add_argument("--address_col", help = "full address column in input_path")
    parser.add_argument("--batch_size", type = int, default = 5000)
    parser.add_argument("--output_dir", default = "output")

    args = parser.parse_args()
    
    main(args)
