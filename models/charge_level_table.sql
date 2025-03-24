WITH full_universe_of_charges AS (
    SELECT
        lc.cel_arrest_date::date as arrest_date,
        DATE_PART('month', lc.cel_arrest_date) as arrest_month,
        DATE_PART('year', lc.cel_arrest_date) as arrest_year,
        lc.arrest_id,
        lc.id AS charge_id,
        lc.charge_code_id,

        lcc.fbi_code AS charge_code_fbi_code,
        lcc.statute AS charge_code_statute,
        lcc.descr AS charge_code_descr,

        CASE WHEN
            lcc.fbi_code IN
            ('01A', '01B', '2', '3', '04A', '04B', '5', '6', '7', '08A', '08B', '9')
        THEN 1 ELSE 0 END AS index_crime_ind,

        CASE WHEN
            lcc.fbi_code = '18'
        THEN 1 ELSE 0 END AS drug_related_crime_ind

    FROM cleaned.living_charge lc
    LEFT JOIN cleaned.living_charge_code lcc ON lc.charge_code_id = lcc.id
)
SELECT * FROM full_universe_of_charges
WHERE 
    1 = 1
    AND (index_crime_ind = 1 OR drug_related_crime_ind = 1)
    AND arrest_year >= '{{ var("start_year") }}'
    AND arrest_year <= '{{ var("end_year") }}'
