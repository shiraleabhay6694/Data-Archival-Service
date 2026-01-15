from pydantic import BaseModel
from typing import List


class ArchivalDataResponse(BaseModel):
    table_name: str
    total_records: int
    records: List[dict]
