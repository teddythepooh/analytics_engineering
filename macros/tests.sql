{% test positive(model, column_name) %}
    SELECT *
    FROM {{ model }}
    WHERE {{ column_name }} < 0 AND {{ column_name }} IS NOT NULL
{% endtest %}
