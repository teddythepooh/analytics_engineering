{% docs __overview__ %}
These data models aim to systematically increase the granularity of drug violation arrests observed in the CPD Data Infrastructure (CPD Infra). For now, this fulfills a data request from the Above and Beyond Family Recovery Center: identify historical opioid possession arrests in Chicago at the citywide and community area levels (East and West Garfield Park).

1. `charge_level_table` takes the charge codes and charges tables from CPD Infra, then filters for index crime and drug abuse violation charges using the `fbi_code` column. I am starting with the charges table because it records all charges associated with each arrest; in contrast, the arrests table logs the *first* charge that the officer enters into the system.
2. `charge_lookup` is a customized lookup table for drug abuse violation charges in `charge_level_table`, creating different indicators based on the `charge_code_descr` column. This is by far the most critical model here: it offers a formal mechanism to delineate across over 400 different drug charges.
3. `arrest_level_charges` collapses `charge_level_table` to the arrest level and counts the number of charges per arrest.
4. `analytical_table` simply takes `arrest_level_charges` and integrates demographic information from CPD Infra's arrests table.
5. `citywide_aggregation` collapses `analytical_table` to the citywide level. In this model, I also tally the number of drug-related and drug possession arrests where they were the primary charge. There does not exist an established hierarchy of non-index crimes, so the primary charge designation is dependent strictly on whether the arrest has an associated index crime charge.

{% enddocs %}
