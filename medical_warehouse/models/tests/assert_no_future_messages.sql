select *
from {{ ref('fct_messages') }}
where date_key > to_char(current_date, 'YYYYMMDD')::int;
