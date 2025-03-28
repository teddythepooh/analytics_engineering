WITH drug_charges AS (
    SELECT charge_code_descr, COUNT(*) as num_charges
    FROM {{ ref('all_charges') }}
    WHERE drug_related_crime_ind = 1
    GROUP BY charge_code_descr
    ORDER BY num_charges DESC
)
SELECT
    *,
    CASE WHEN 
        charge_code_descr ILIKE ANY (ARRAY['%MAN/DEL%', '%MFG%', '%DEL%', '%SELL%', '%SALE%', '%MANU%', '%DISTRIB%', '%PRODUCE%'])
    THEN 1 ELSE 0 END AS intent_to_sell_manuf_deliv_or_distrib_ind,
    
    CASE WHEN
        charge_code_descr ILIKE '%PARAPHERNALIA%' OR charge_code_descr = 'POSSESS HYPO/SYRINGE/NEEDLES'
    THEN 1 ELSE 0 END AS paraphernalia_ind,
    
    CASE WHEN
        charge_code_descr ILIKE ANY (ARRAY['%PCS%', '%POSS%', 'POSESS'])
    THEN 1 ELSE 0 END AS possession_ind,
    
    CASE WHEN
        charge_code_descr in {{ parse_yml_list_as_tuple(var('unknown_drug_poss_charges')) }}
    THEN 1 ELSE 0 END AS unknown_substance_possession_ind,

    CASE WHEN
        charge_code_descr ILIKE ANY (ARRAY['%OPIUM%', '%HEROIN%', '%FENTA%', '%OXY%', '%MORPHINE%'])
    THEN 1 ELSE 0 END AS opioid_ind,

    CASE WHEN
        charge_code_descr ILIKE '%CANNABIS%'
    THEN 1 ELSE 0 END AS marijuana_ind
FROM drug_charges
