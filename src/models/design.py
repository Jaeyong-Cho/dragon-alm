from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Design:
    """Design item model"""
    id: Optional[int]
    name: str
    description: str
    type: str  # e.g., "Architecture", "Component", "Interface", "Database"
    status: str  # e.g., "Draft", "In Review", "Approved", "Implemented"
    created_at: datetime
    updated_at: datetime
    requirement_ids: list[int]  # Linked requirements

    def __post_init__(self):
        if self.requirement_ids is None:
            self.requirement_ids = []
