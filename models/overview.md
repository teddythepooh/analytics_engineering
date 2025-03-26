{% docs __overview__ %}
These data models aim to systematically increase the granularity of drug violation arrests observed in the CPD Data Infrastructure (CPD Infra). Presently, this fulfills a data request from the Above and Beyond Family Recovery Center: identify historical opioid possession arrests in Chicago at the citywide and community area levels (East and West Garfield Park).

1. `arrests` takes relevant columns from CPD Infra's arrests and charge codes tables, then filters for index crime and drug abuse violation charges using the `fbi_code` column.
1. `charges` takes relevant columns from CPD Infra's charges and charge codes tables, then filters for index crime and drug abuse violation charges using the `fbi_code` column.
1. `all_charges` full outer joins the arrests and charges models to obtain a charge-level table of all arrests logged in CPD Infra. In cases of like-columns, they are coalesced accordingly. For arrest IDs that only exist in the arrests model, the `charge_id` is imputed with 'only available in arrests table.' Arrests that only appear in the arrests table are technically defined as one "charge" in this model.
1. `charge_lookup` is a customized lookup table for drug abuse violation charges in `all_charges`, creating different indicators based on the `charge_code_descr` column. This is by far the most critical model here: it offers a mechanism to delineate across 440 different drug charges.
1. `arrest_level_table` takes `all_charges`, then collapses it to the arrest-level and counts the number of charges per arrest using the indicators produced in `charge_lookup`.
1. `analytical_table` simply takes `arrest_level_table` and integrates demographic information from the `arrests` model.
1. `citywide_aggregation` collapses `analytical_table` to the citywide level. In this model, I also tally the number of drug-related and drug possession arrests where they were the primary charge. There does not exist an established hierarchy of non-index crimes, so the primary charge designation is dependent strictly on whether the arrest has an associated index crime charge.


{% enddocs %}
