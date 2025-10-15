from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any, TypeVar, Generic

T = TypeVar('T')


class IRepository(ABC, Generic[T]):
    """Generic repository interface for data access"""

    @abstractmethod
    def create(self, entity: T) -> str:
        """
        Create new entity

        Args:
            entity: Entity to create

        Returns:
            Entity ID
        """
        pass

    @abstractmethod
    def read(self, entity_id: str) -> Optional[T]:
        """
        Read entity by ID

        Args:
            entity_id: Entity identifier

        Returns:
            Entity or None if not found
        """
        pass

    @abstractmethod
    def update(self, entity: T) -> bool:
        """
        Update existing entity

        Args:
            entity: Entity to update

        Returns:
            True if successful
        """
        pass

    @abstractmethod
    def delete(self, entity_id: str) -> bool:
        """
        Delete entity by ID

        Args:
            entity_id: Entity identifier

        Returns:
            True if successful
        """
        pass

    @abstractmethod
    def find_all(self) -> List[T]:
        """
        Get all entities

        Returns:
            List of all entities
        """
        pass

    @abstractmethod
    def find_by_criteria(self, criteria: Dict[str, Any]) -> List[T]:
        """
        Find entities matching criteria

        Args:
            criteria: Search criteria

        Returns:
            List of matching entities
        """
        pass
