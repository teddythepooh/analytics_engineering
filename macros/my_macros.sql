{% macro parse_yml_list_as_tuple(list) %}
{# parses a_i in a given .yml list as ('a_1', 'a_2', . . . ) #}
    ({% for element in list %}
     '{{ element }}'{% if not loop.last %}, {% endif %}
     {% endfor %}
    )
{% endmacro %}


{% macro divide(numerator, denominator, num_decimals = 3) %}
{# divides numerator by denominator to the nearest num_decimals places #}
    ROUND({{ numerator }}::NUMERIC / {{ denominator }}::NUMERIC, {{ num_decimals }})
{% endmacro %}
