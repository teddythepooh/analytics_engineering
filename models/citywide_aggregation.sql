WITH citywide_arrests AS (
    SELECT
        arrest_year,
        COUNT(*) FILTER(WHERE num_drug_related_charges > 0) AS num_drug_related_arrests,
        COUNT(*) FILTER(WHERE num_drug_related_charges > 0 AND num_index_crime_charges = 0) AS num_drug_related_arrests_as_primary_charge,
    
        COUNT(*) FILTER(WHERE num_unknown_poss_charges > 0) AS num_unknown_drug_poss,

        COUNT(*) FILTER(WHERE num_drug_poss_charges > 0) AS num_drug_poss,
        COUNT(*) FILTER(WHERE num_drug_poss_charges > 0 AND num_index_crime_charges = 0) AS num_drug_poss_as_primary_charge,
    
        COUNT(*) FILTER(WHERE num_marijuana_related_charges > 0) AS num_marijuana_related_arrests,
        COUNT(*) FILTER(WHERE num_marijuana_poss_charges > 0) AS num_marijuana_poss,

        COUNT(*) FILTER(WHERE num_opioid_related_charges > 0) AS num_opioid_related_arrests,
        COUNT(*) FILTER(WHERE num_opioid_poss_charges > 0) AS num_opioid_poss,
    
        COUNT(*) FILTER(WHERE num_drug_related_charges > 0 
                        AND num_marijuana_related_charges = 0
                        AND num_opioid_related_charges = 0) AS num_drug_related_arrests_ex_marijuana_and_opioid,

        COUNT(*) FILTER(WHERE num_drug_poss_charges > 0 
                        AND num_marijuana_related_charges = 0
                        AND num_opioid_related_charges = 0) AS num_drug_poss_ex_marijuana_and_opioid
    FROM {{ ref('analytical_table') }}
    GROUP BY arrest_year
)
SELECT
    *,
    {{ divide('num_drug_poss_as_primary_charge', 'num_drug_poss') }} AS pct_drug_poss_as_primary_charge,

    ROUND(
        (num_drug_poss_as_primary_charge - LAG(num_drug_poss_as_primary_charge, 1) OVER (ORDER BY arrest_year))::NUMERIC
        / LAG(num_drug_poss_as_primary_charge, 1) OVER (ORDER BY arrest_year)::NUMERIC, 
        3
    ) AS pct_change_drug_poss_as_primary_charge,
    
    {{ divide('num_marijuana_poss', 'num_drug_poss') }} AS pct_drug_poss_as_marijuana,
    {{ divide('num_opioid_poss', 'num_drug_poss') }} AS pct_drug_poss_as_opioid,
    {{ divide('num_unknown_drug_poss', 'num_drug_poss') }} AS pct_drug_poss_unknown_substance

FROM citywide_arrests
ORDER BY arrest_year
