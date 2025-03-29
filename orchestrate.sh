#!/bin/bash

run_dbt=False
run_geocoder=False

shapefiles_dir=/projects/cel/2022-028-public-affairs-analysis/data/shapefiles_and_geocodes/chicago/chicago_communities_SHP
chicago_shp=$shapefiles_dir/geo_export_29d5f5d1-d63c-4386-9d89-76ae473eea7d.shp

python_dir=./python/
py_config=$python_dir/config.yml
visualization_script=$python_dir/citywide_aggregation.py
db_query_script=$python_dir/query_table_from_db.py

geocoder_dir=./geocoder/
geocoder_script=$geocoder_dir/geocode.py
garfield_park_script=$geocoder_dir/garfield_park.py

output_dir=./output

# Step 1: Materialize SQL models onto CPD Infra.
source ~/.bashrc
conda activate dbt_env # ./requirements.yml

if [[ $run_dbt == "True" ]]; then
    dbt run && dbt test
fi


# Step 2: Query and visualize materialized citywide_aggregation model.
start_years=(2000 2010 2016 2020)

# https://phoenixnap.com/kb/bash-associative-array
declare -A max_y=([2000]=65000 [2010]=45000 [2016]=16000 [2020]=10000)
declare -A y_ticks=([2000]=5000 [2010]=2500 [2016]=1000 [2020]=1000)

for start_year in ${start_years[@]}; do
    python $visualization_script \
        --config_file=$py_config \
        --start_year=$start_year \
        --max_y=${max_y[$start_year]} \
        --y_ticks=${y_ticks[$start_year]} \
        --output_dir=$output_dir
done


# Step 3: Query materialized analytical_table model and export to .csv in preparation for geocoding.
python $db_query_script \
    --config_file=$py_config \
    --table=analytical_table \
    --output_dir=$output_dir


# Step 4. Geocode, then map point coordinates to the community area.
if [[ $run_geocoder == "True" ]]; then
    conda deactivate
    conda activate geocoder_env # ./requirements_geocoder.yml

    python $geocoder_script \
        --input_path=$output_dir/analytical_table.csv \
        --address_col=arrest_address \
        --output_dir=$output_dir \
        --batch_size=10000

    python $garfield_park_script \
        --start_year=2010 \
        --analytical_table=$output_dir/analytical_table.csv \
        --analytical_table_geocoded=$output_dir/analytical_table_geocoded.csv \
        --chi_shp=$chicago_shp \
        --output_dir=$output_dir
fi
