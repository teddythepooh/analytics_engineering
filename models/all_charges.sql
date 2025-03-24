SELECT
    COALESCE(c.charge_id::text, 'only available in arrests table') AS charge_id,
    COALESCE(c.arrest_id, a.arrest_id) AS arrest_id,
    COALESCE(c.arrest_date, a.arrest_date) AS arrest_date,
    DATE_PART('month', COALESCE(c.arrest_date, a.arrest_date)) AS arrest_month,
    DATE_PART('year', COALESCE(c.arrest_date, a.arrest_date)) AS arrest_year,
    
    COALESCE(c.charge_code_descr, a.charge_code_descr) AS charge_code_descr,
    COALESCE(c.index_crime_ind, a.index_crime_ind) AS index_crime_ind,
    COALESCE(c.drug_related_crime_ind, a.drug_related_crime_ind) AS drug_related_crime_ind
FROM {{ ref('arrests') }} a
FULL OUTER JOIN {{ ref('charges') }} c ON a.arrest_id = c.arrest_id
ORDER BY arrest_id, arrest_date
