from typing import List, Optional
from models.design import Design
from managers.design_manager import DesignManager


class DesignController:
    """Controller for design operations"""

    def __init__(self, manager: DesignManager):
        self.manager = manager

    def create_design(self, name: str, description: str, type: str,
                     status: str = "Draft", requirement_ids: Optional[List[int]] = None) -> Design:
        """Create a new design"""
        return self.manager.create_design(name, description, type, status, requirement_ids)

    def get_design(self, design_id: int) -> Optional[Design]:
        """Get a design by ID"""
        return self.manager.get_design(design_id)

    def get_all_designs(self) -> List[Design]:
        """Get all designs"""
        return self.manager.get_all_designs()

    def update_design(self, design: Design) -> Design:
        """Update an existing design"""
        return self.manager.update_design(design)

    def delete_design(self, design_id: int) -> bool:
        """Delete a design"""
        return self.manager.delete_design(design_id)
