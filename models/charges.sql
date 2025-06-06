WITH charges AS (
    SELECT
        lc.cel_ingested_on::date AS ingestion_date,
        DATE_PART('year', lc.cel_ingested_on) AS ingestion_year,
        lc.arrest_id,
        lc.cel_arrest_date::date AS arrest_date,
        DATE_PART('month', lc.cel_arrest_date) AS arrest_month,
        DATE_PART('year', lc.cel_arrest_date) AS arrest_year,
        lc.id AS charge_id,
        lc.charge_code_id,

        lcc.fbi_code AS charge_code_fbi_code,
        lcc.statute AS charge_code_statute,
        lcc.descr AS charge_code_descr,

        CASE WHEN
            lcc.fbi_code IN {{ parse_yml_list_as_tuple(var('index_crime_fbi_codes')) }} 
        THEN 1 ELSE 0 END AS index_crime_ind,

        CASE WHEN
            lcc.fbi_code = '{{ var("drug_crime_fbi_code") }}'
        THEN 1 ELSE 0 END AS drug_related_crime_ind
    FROM {{ source('cpd_infra_tables', 'living_charge') }} lc
    LEFT JOIN {{ source('cpd_infra_tables', 'living_charge_code') }} lcc ON lc.charge_code_id = lcc.id
)
SELECT * FROM charges
WHERE 
    1 = 1
    AND (index_crime_ind = 1 OR drug_related_crime_ind = 1)
    AND arrest_year >= '{{ var("start_year") }}'
    AND arrest_year <= '{{ var("end_year") }}'
