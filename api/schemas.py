# api/schemas.py

from pydantic import BaseModel
from typing import List, Optional

class TopProduct(BaseModel):
    term: str
    count: int

class ChannelActivity(BaseModel):
    date: str
    total_messages: int

class MessageResult(BaseModel):
    message_id: int
    channel_name: str
    message_text: str
    message_date: str

class VisualContentStats(BaseModel):
    channel_name: str
    total_messages: int
    image_messages: int
    image_percentage: float
