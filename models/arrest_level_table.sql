WITH charge_level AS (
    SELECT
        cl.arrest_id,
        cl.arrest_date,
        cl.arrest_month,
        cl.arrest_year,
    
        cl.charge_code_descr,
        cl.drug_related_crime_ind,
        cl.index_crime_ind,

        /*
        The all_charges model includes both index crime and drug charge, while the charge_lookup
        model only comprises of drug charges. I am filling in nulls below with zero, for cases where
        the charge_code_descr does not point to a drug charge.
        */
        COALESCE(cc.intent_to_sell_manuf_deliv_or_distrib_ind, 0) AS intent_to_sell_manuf_deliv_or_distrib_ind,
        COALESCE(cc.paraphernalia_ind, 0) AS paraphernalia_ind,
        COALESCE(cc.possession_ind, 0) AS possession_ind,
        COALESCE(cc.unknown_substance_possession_ind, 0) AS unknown_substance_possession_ind,
        COALESCE(cc.opioid_ind, 0) AS opioid_ind,
        COALESCE(cc.marijuana_ind, 0) AS marijuana_ind
    FROM {{ ref('all_charges') }} cl
    LEFT JOIN {{ ref('charge_lookup') }} cc ON cl.charge_code_descr = cc.charge_code_descr
)
SELECT
    arrest_id, arrest_date, arrest_month, arrest_year,

    SUM(index_crime_ind) AS num_index_crime_charges,
    
    SUM(drug_related_crime_ind) AS num_drug_related_charges,
    SUM(opioid_ind) AS num_opioid_related_charges,
    SUM(marijuana_ind) AS num_marijuana_related_charges,

    SUM(CASE WHEN 
            possession_ind = 1 
            AND intent_to_sell_manuf_deliv_or_distrib_ind = 0
            AND paraphernalia_ind = 0
        THEN 1 ELSE 0 END) AS num_drug_poss_charges,

    SUM(CASE WHEN 
            unknown_substance_possession_ind = 1
        THEN 1 ELSE 0 END) AS num_unknown_poss_charges,

    SUM(CASE WHEN 
            possession_ind = 1 
            AND opioid_ind = 1
            AND intent_to_sell_manuf_deliv_or_distrib_ind = 0
        THEN 1 ELSE 0 END) AS num_opioid_poss_charges,

    SUM(CASE WHEN 
            possession_ind = 1 
            AND marijuana_ind = 1
            AND intent_to_sell_manuf_deliv_or_distrib_ind = 0 
        THEN 1 ELSE 0 END) AS num_marijuana_poss_charges
FROM charge_level
GROUP BY arrest_id, arrest_date, arrest_month, arrest_year
