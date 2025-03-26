#!/bin/bash

output_dir=./test_output

py_config=./python/config.yml
visualization_script=./python/visualize_citywide_stats.py
db_query_script=./python/query_table_from_db.py

source ~/.bashrc
conda activate dbt_env # ./requirements.yml

# Materialize SQL models onto db.
dbt run
dbt test

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

# Geocode.
conda deactivate
conda activate geocoder_env # ./requirements_geocoder.yml

python geocoder/geocode.py \
    --input_path=$output_dir/analytical_table.csv \
    --address_col=arrest_address \
    --output_dir=$output_dir \
    --batch_size=10000
