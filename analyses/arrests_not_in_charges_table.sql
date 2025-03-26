SELECT
    arrest_year,
    ingestion_year,
    COUNT(DISTINCT arrest_id) as num_index_crime_and_drug_arrests,
    COUNT(DISTINCT arrest_id) FILTER(WHERE charge_id = 'only available in arrests table') AS num_not_in_charges_table
FROM {{ ref('all_charges') }}
WHERE arrest_year <= 2014
GROUP BY arrest_year, ingestion_year
