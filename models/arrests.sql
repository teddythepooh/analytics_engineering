WITH arrests AS (
    SELECT
        arrest_id,
        cel_birth_date::date AS dob,
        race_code_cd AS race,
        sex_code_cd AS sex,

        CONCAT(o_street_no, ' ', o_street_nme, ' ', o_city, ' ', o_state_cd, ' ', o_zip_cd) AS home_address,
        CONCAT(street_no, ' ', street_nme, ' ', city, ' ', o_state_cd, ' ' , zip_cd) AS arrest_address,

        cel_arrest_date::date AS arrest_date,
        DATE_PART('month', cel_arrest_date) AS arrest_month,
        DATE_PART('year', cel_arrest_date) AS arrest_year,
        arr_district AS arrest_district,
        stat_descr,
        charge_code_id,

        la.fbi_code,
        lcc.statute AS charge_code_statute,
        lcc.descr AS charge_code_descr,

        CASE WHEN
            la.fbi_code IN {{ parse_yml_list_as_tuple(var('index_crime_fbi_codes')) }} 
        THEN 1 ELSE 0 END AS index_crime_ind,

        CASE WHEN la.fbi_code = '{{ var("drug_crime_fbi_code") }}'
        THEN 1 ELSE 0 END AS drug_related_crime_ind
    FROM cleaned.living_arrest la
    LEFT JOIN cleaned.living_charge_code lcc ON la.charge_code_id = lcc.id
)
SELECT * FROM arrests
WHERE
    1 = 1
    AND (index_crime_ind = 1 OR drug_related_crime_ind = 1)
    AND arrest_year >= '{{ var("start_year") }}'
    AND arrest_year <= '{{ var("end_year") }}'
