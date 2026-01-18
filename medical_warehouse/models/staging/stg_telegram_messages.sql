with source as (

    select *
    from raw.telegram_messages

),

cleaned as (

    select
        cast(message_id as bigint) as message_id,
        lower(trim(channel_name)) as channel_name,
        cast(message_date as timestamp) as message_date,
        trim(message_text) as message_text,
        coalesce(views, 0) as view_count,
        coalesce(forwards, 0) as forward_count,
        coalesce(has_media, false) as has_image,
        length(message_text) as message_length
    from source
    where message_text is not null
)

select * from cleaned;
