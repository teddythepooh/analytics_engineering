SELECT
    {% if var('include_ir_no_in_analytical_table') %}
    la.ir_no,
    {% endif %}

    {% if var('include_arrestee_names_in_analytical_table') %}
    la.first_nme AS first,
    la.last_nme as last,
    {% endif %}
    
    al.arrest_id,
    al.arrest_date,
    al.arrest_month,
    al.arrest_year,
    
    DATE_PART('year', AGE(al.arrest_date, la.cel_birth_date)) AS age_at_arrest_date,
    
    la.arr_district AS arrest_district,
    la.cel_birth_date::date AS dob,
    la.race_code_cd AS race,
    la.sex_code_cd AS sex,
    CONCAT(la.o_street_no, ' ', la.o_street_nme, ' ', la.o_city, ' ', la.o_state_cd, ' ', la.o_zip_cd) AS home_address,
    CONCAT(la.street_no, ' ', la.street_nme, ' ', la.city, ' ', la.o_state_cd, ' ' , la.zip_cd) AS arrest_address,

    al.num_index_crime_charges,
    al.num_drug_related_charges,
    al.num_opioid_related_charges,
    al.num_marijuana_related_charges,
    al.num_drug_poss_charges,
    al.num_unknown_poss_charges,
    al.num_opioid_poss_charges,
    al.num_marijuana_poss_charges
FROM {{ ref('arrest_level_charges') }} al
LEFT JOIN cleaned.living_arrest la ON al.arrest_id = la.arrest_id
