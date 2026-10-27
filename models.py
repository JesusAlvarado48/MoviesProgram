from dataclasses import dataclass
from typing import Optional

@dataclass
class Category:
    id: int
    name: str

@dataclass
class Movie:
    id: Optional[int]
    title: str
    year: int
    duration: int
    category_id: int
    category_name: Optional[str] = None