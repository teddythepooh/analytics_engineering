### Requirements
1. `requirements_geocoder.yml` for `./geocoder/` and `requirements.yml` for everything else
2. `cpd_infra_dev`, the Chicago PD Data Infrastructure (CPD Infra) dev database

### About
These data models aim to systematically increase the granularity of drug violation arrests in CPD Infra. Presently, this fulfills a data request from the Above and Beyond Family Recovery Center: identify historical opioid possession arrests in Chicago at the citywide and community area levels (East and West Garfield Park). See `./models/schema.yml` for context on the models. Additionally, do `dbt docs generate --static` for the official dbt documentation. Open the file in your browser, then click the blue icon on the lower right corner to visualize the underlying DAG.

### Instructions
1. Declare your CNet ID and password as environment variables called `DBT_USER` and `DBT_PASSWORD`, respectively. 
    - For QA, create your own schema in `cpd_infra_dev` (e.g, `ted_work_QA`); then, replace the `schema` key in `profiles.yml` accordingly. In `./python/config.yml`, make sure that the values under the `db_credentials` key match `profiles.yml`. I should really load `profiles.yml` into scripts in `./python/` to avoid rewriting credentials, but this works for now.
1. Do `bash orchestrate.sh` (or run it as an executable) to orchestrate the materialization of SQL models in `./models/`, the citywide visualizations & geocoding preparation in `./python/`, and the geocoder in `./geocoder/`. The geocoding preparation simply consists of querying/exporting the materialized `analytical_table` model from the db; filtering for relevant columns; and filtering for arrests that took place in Chicago PD's 11th and 12th districts. These two districts patrol East and West Garfield Park, our two neighborhoods of interest. 
    - Recall that `./geocoder/` requires a different environment than everything else: among other reasons, it use our internal geocoder (`ul_geocoder`). Such is why I am activating/deactivating two different environments in `orchestrate.sh`.

### QA Instructions for dbt
![](images/dbt_run.png)
1. `dbt debug` will check if you configured dbt correctly.
1. `dbt compile` will compile the data models in `./models/` to `./target/compiled/`, showing how dbt expands the Jinja commands before execution. In that regard, for my ad-hoc queries in `analyses/`, run the compiled query directly on psql.
1. `dbt test` will run the tests outlined in `./models/schema.yml`.

![](images/dbt_test.png)
