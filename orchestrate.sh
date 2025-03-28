#!/bin/bash

run_dbt=True

# inputs
public_affairs_dir=/projects/cel/2022-028-public-affairs-analysis
chicago_shp=$public_affairs_dir/data/shapefiles_and_geocodes/chicago/chicago_communities_SHP/geo_export_29d5f5d1-d63c-4386-9d89-76ae473eea7d.shp

# scripts
py_config=./python/config.yml
visualization_script=./python/citywide_aggregation.py
db_query_script=./python/query_table_from_db.py

geocoder_script=./geocoder/geocode.py
garfield_park_visualization_script=./geocoder/garfield_park.py

# output dir
output_dir=./output

# Materialize SQL models onto db.
source ~/.bashrc
conda activate dbt_env # ./requirements.yml

if [[ $run_dbt == "True" ]]; then
    dbt run && dbt test
fi

# Query and visualize materialized citywide_aggregation model from db.
python $visualization_script \
    --config_file=$py_config \
    --output_dir=$output_dir
    
python $visualization_script \
    --config_file=$py_config \
    --start_year=2010 \
    --max_y=45000 \
    --y_ticks=2500 \
    --output_dir=$output_dir
    
python $visualization_script \
    --config_file=$py_config \
    --start_year=2016 \
    --max_y=16000 \
    --y_ticks=1000 \
    --output_dir=$output_dir

python $visualization_script \
    --config_file=$py_config \
    --start_year=2020 \
    --max_y=10000 \
    --y_ticks=1000 \
    --output_dir=$output_dir

# Query materialized analytical_table model from db and export to .csv in preparation for geocoding.
python $db_query_script \
    --config_file=$py_config \
    --table=analytical_table \
    --output_dir=$output_dir

# Geocode, then map point coordinates to the community area.
conda deactivate
conda activate geocoder_env # ./requirements_geocoder.yml

python $geocoder_script \
    --input_path=$output_dir/analytical_table.csv \
    --address_col=arrest_address \
    --output_dir=$output_dir \
    --batch_size=10000

python $garfield_park_visualization_script \
    --start_year=2010 \
    --analytical_table=$output_dir/analytical_table.csv \
    --analytical_table_geocoded=$output_dir/analytical_table_geocoded.csv \
    --chi_shp=$chicago_shp \
    --output_dir=$output_dir
