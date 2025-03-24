SELECT
    a.arrest_id,
    a.arrest_date,
    a.arrest_month,
    a.arrest_year,
    b.dob,

    DATE_PART('year', AGE(a.arrest_date, b.dob)) AS age_at_arrest_date,
    
    b.arrest_district,
    b.race,
    b.sex,
    b.home_address,
    b.arrest_address,
    
    a.num_index_crime_charges,
    a.num_drug_related_charges,
    a.num_opioid_related_charges,
    a.num_marijuana_related_charges,
    a.num_drug_poss_charges,
    a.num_unknown_poss_charges,
    a.num_opioid_poss_charges,
    a.num_marijuana_poss_charges
FROM {{ ref('arrest_level_table') }} a
LEFT JOIN {{ ref('arrests') }} b ON a.arrest_id = b.arrest_id
ORDER BY arrest_year
