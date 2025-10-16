from datetime import datetime
from typing import List, Optional
from models.design import Design
from repositories.sqlite_design_repository import SQLiteDesignRepository


class DesignManager:
    """Manager for design operations"""

    def __init__(self, repository: SQLiteDesignRepository):
        self.repository = repository

    def create_design(self, name: str, description: str, type: str,
                     status: str = "Draft", requirement_ids: Optional[List[int]] = None) -> Design:
        """Create a new design"""
        now = datetime.now()
        design = Design(
            id=None,
            name=name,
            description=description,
            type=type,
            status=status,
            created_at=now,
            updated_at=now,
            requirement_ids=requirement_ids or []
        )
        return self.repository.create(design)

    def get_design(self, design_id: int) -> Optional[Design]:
        """Get a design by ID"""
        return self.repository.get(design_id)

    def get_all_designs(self) -> List[Design]:
        """Get all designs"""
        return self.repository.get_all()

    def update_design(self, design: Design) -> Design:
        """Update an existing design"""
        design.updated_at = datetime.now()
        return self.repository.update(design)

    def delete_design(self, design_id: int) -> bool:
        """Delete a design"""
        return self.repository.delete(design_id)

    def get_design_types(self) -> List[str]:
        """Get available design types"""
        return ["Architecture", "Component", "Interface", "Database", "Algorithm", "Security"]
