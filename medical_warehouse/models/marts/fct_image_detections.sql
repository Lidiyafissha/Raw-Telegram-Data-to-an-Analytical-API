{{ config(materialized='table') }}

SELECT
    image_id,
    message_id,
    channel_id,
    detected_object,
    confidence_score,
    detection_count,
    image_category,
    detection_date
FROM {{ ref('stg_yolo_detections') }}
WHERE confidence_score >= 0.5
