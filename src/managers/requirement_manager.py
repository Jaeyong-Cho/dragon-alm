from typing import List, Optional, Dict, Any
from datetime import datetime
from models.requirement import Requirement
from models.enums import RequirementStatus, Priority
from repositories.sqlite_repository import SQLiteRequirementRepository
from services.validation_service import ValidationService
from exceptions import ValidationError, EntityNotFoundError


class RequirementManager:
    """Manager for requirement business logic"""

    def __init__(self, repository: SQLiteRequirementRepository):
        """
        Initialize manager

        Args:
            repository: Requirement repository
        """
        self.repository = repository
        self.validation_service = ValidationService()

    def create_requirement(self, data: Dict[str, Any]) -> Requirement:
        """
        Create new requirement

        Args:
            data: Requirement data dictionary

        Returns:
            Created requirement

        Raises:
            ValidationError: If validation fails
        """
        # Generate ID if not provided
        if 'id' not in data or not data['id']:
            data['id'] = self.repository.get_next_id()

        # Set defaults
        if 'status' not in data:
            data['status'] = RequirementStatus.DRAFT
        elif isinstance(data['status'], str):
            data['status'] = RequirementStatus(data['status'])

        if 'priority' not in data:
            data['priority'] = Priority.MEDIUM
        elif isinstance(data['priority'], str):
            data['priority'] = Priority(data['priority'])

        # Create requirement object
        requirement = Requirement(
            id=data['id'],
            title=data.get('title', ''),
            description=data.get('description', ''),
            status=data['status'],
            priority=data['priority'],
            category=data.get('category', ''),
            parent_id=data.get('parent_id'),
            verification_criteria=data.get('verification_criteria', ''),
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

        # Validate
        validation_result = self.validation_service.validate_requirement(requirement)
        if not validation_result.valid:
            raise ValidationError(
                f"Validation failed: {', '.join(validation_result.errors)}"
            )

        # Save to repository
        self.repository.create(requirement)

        return requirement

    def update_requirement(self, req_id: str, data: Dict[str, Any]) -> Requirement:
        """
        Update existing requirement

        Args:
            req_id: Requirement ID
            data: Updated data

        Returns:
            Updated requirement

        Raises:
            EntityNotFoundError: If requirement not found
            ValidationError: If validation fails
        """
        requirement = self.repository.read(req_id)
        if requirement is None:
            raise EntityNotFoundError(f"Requirement {req_id} not found")

        # Update fields
        if 'title' in data:
            requirement.title = data['title']
        if 'description' in data:
            requirement.description = data['description']
        if 'status' in data:
            requirement.status = RequirementStatus(data['status']) \
                if isinstance(data['status'], str) else data['status']
        if 'priority' in data:
            requirement.priority = Priority(data['priority']) \
                if isinstance(data['priority'], str) else data['priority']
        if 'category' in data:
            requirement.category = data['category']
        if 'parent_id' in data:
            requirement.parent_id = data['parent_id']
        if 'verification_criteria' in data:
            requirement.verification_criteria = data['verification_criteria']

        requirement.updated_at = datetime.now()

        # Validate
        validation_result = self.validation_service.validate_requirement(requirement)
        if not validation_result.valid:
            raise ValidationError(
                f"Validation failed: {', '.join(validation_result.errors)}"
            )

        # Update in repository
        self.repository.update(requirement)

        return requirement

    def delete_requirement(self, req_id: str) -> bool:
        """Delete requirement by ID"""
        return self.repository.delete(req_id)

    def get_requirement(self, req_id: str) -> Optional[Requirement]:
        """Get requirement by ID"""
        return self.repository.read(req_id)

    def get_all_requirements(self) -> List[Requirement]:
        """Get all requirements"""
        return self.repository.find_all()

    def search_requirements(self, query: str) -> List[Requirement]:
        """Search requirements by title or description"""
        all_reqs = self.repository.find_all()
        query_lower = query.lower()
        return [
            req for req in all_reqs
            if query_lower in req.title.lower()
            or query_lower in req.description.lower()
            or query_lower in req.id.lower()
        ]

    def get_children(self, parent_id: str) -> List[Requirement]:
        """Get child requirements"""
        return self.repository.find_by_criteria({'parent_id': parent_id})
