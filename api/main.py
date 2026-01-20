# api/main.py

from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List

from api.database import get_db
from api.schemas import (
    TopProduct,
    ChannelActivity,
    MessageResult,
    VisualContentStats
)

app = FastAPI(
    title="Medical Telegram Analytical API",
    description="Analytics API built on dbt data marts",
    version="1.0.0"
)

# -------------------------------
# Endpoint 1: Top Products
# -------------------------------
@app.get("/api/reports/top-products", response_model=List[TopProduct])
def top_products(limit: int = Query(10, gt=0), db: Session = Depends(get_db)):
    query = text("""
        SELECT term, COUNT(*) AS count
        FROM marts.fct_messages,
             regexp_split_to_table(lower(message_text), '\\s+') AS term
        GROUP BY term
        ORDER BY count DESC
        LIMIT :limit
    """)
    result = db.execute(query, {"limit": limit}).fetchall()
    return result


# -------------------------------
# Endpoint 2: Channel Activity
# -------------------------------
@app.get("/api/channels/{channel_name}/activity", response_model=List[ChannelActivity])
def channel_activity(channel_name: str, db: Session = Depends(get_db)):
    query = text("""
        SELECT d.full_date::text AS date,
               COUNT(*) AS total_messages
        FROM marts.fct_messages f
        JOIN marts.dim_channels c ON f.channel_key = c.channel_key
        JOIN marts.dim_dates d ON f.date_key = d.date_key
        WHERE c.channel_name = :channel
        GROUP BY d.full_date
        ORDER BY d.full_date
    """)
    rows = db.execute(query, {"channel": channel_name}).fetchall()

    if not rows:
        raise HTTPException(status_code=404, detail="Channel not found")

    return rows


# -------------------------------
# Endpoint 3: Message Search
# -------------------------------
@app.get("/api/search/messages", response_model=List[MessageResult])
def search_messages(
    query: str,
    limit: int = Query(20, gt=0),
    db: Session = Depends(get_db)
):
    sql = text("""
        SELECT message_id,
               channel_name,
               message_text,
               message_date::text
        FROM marts.fct_messages f
        JOIN marts.dim_channels c ON f.channel_key = c.channel_key
        WHERE message_text ILIKE :q
        LIMIT :limit
    """)
    rows = db.execute(sql, {"q": f"%{query}%", "limit": limit}).fetchall()
    return rows


# -------------------------------
# Endpoint 4: Visual Content Stats
# -------------------------------
@app.get("/api/reports/visual-content", response_model=List[VisualContentStats])
def visual_content(db: Session = Depends(get_db)):
    query = text("""
        SELECT c.channel_name,
               COUNT(*) AS total_messages,
               SUM(CASE WHEN has_image THEN 1 ELSE 0 END) AS image_messages,
               ROUND(
                   100.0 * SUM(CASE WHEN has_image THEN 1 ELSE 0 END) / COUNT(*),
                   2
               ) AS image_percentage
        FROM marts.fct_messages f
        JOIN marts.dim_channels c ON f.channel_key = c.channel_key
        GROUP BY c.channel_name
    """)
    return db.execute(query).fetchall()
