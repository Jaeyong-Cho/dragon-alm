from typing import List, Optional, Dict, Any, Callable
from managers.requirement_manager import RequirementManager
from models.requirement import Requirement
from exceptions import ValidationError, DatabaseError, EntityNotFoundError


class RequirementController:
    """Controller for requirement operations"""

    def __init__(self, manager: RequirementManager):
        """
        Initialize controller

        Args:
            manager: Requirement manager
        """
        self.manager = manager
        self._observers: List[Callable] = []

    def add_observer(self, observer: Callable):
        """Add observer for data changes"""
        self._observers.append(observer)

    def notify_observers(self):
        """Notify all observers of data changes"""
        for observer in self._observers:
            observer()

    def create_requirement(self, data: Dict[str, Any]) -> tuple[bool, str, Optional[Requirement]]:
        """
        Create new requirement

        Args:
            data: Requirement data

        Returns:
            Tuple of (success, message, requirement)
        """
        try:
            requirement = self.manager.create_requirement(data)
            self.notify_observers()
            return True, f"Requirement {requirement.id} created successfully", requirement
        except ValidationError as e:
            return False, str(e), None
        except DatabaseError as e:
            return False, f"Database error: {str(e)}", None
        except Exception as e:
            return False, f"Unexpected error: {str(e)}", None

    def update_requirement(self, req_id: str, data: Dict[str, Any]) -> tuple[bool, str, Optional[Requirement]]:
        """
        Update requirement

        Args:
            req_id: Requirement ID
            data: Updated data

        Returns:
            Tuple of (success, message, requirement)
        """
        try:
            requirement = self.manager.update_requirement(req_id, data)
            self.notify_observers()
            return True, f"Requirement {req_id} updated successfully", requirement
        except EntityNotFoundError as e:
            return False, str(e), None
        except ValidationError as e:
            return False, str(e), None
        except DatabaseError as e:
            return False, f"Database error: {str(e)}", None
        except Exception as e:
            return False, f"Unexpected error: {str(e)}", None

    def delete_requirement(self, req_id: str) -> tuple[bool, str]:
        """Delete requirement"""
        try:
            success = self.manager.delete_requirement(req_id)
            if success:
                self.notify_observers()
                return True, f"Requirement {req_id} deleted successfully"
            return False, f"Requirement {req_id} not found"
        except DatabaseError as e:
            return False, f"Database error: {str(e)}"
        except Exception as e:
            return False, f"Unexpected error: {str(e)}"

    def get_all_requirements(self) -> List[Requirement]:
        """Get all requirements"""
        return self.manager.get_all_requirements()

    def search_requirements(self, query: str) -> List[Requirement]:
        """Search requirements"""
        return self.manager.search_requirements(query)
