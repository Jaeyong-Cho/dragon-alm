from dataclasses import dataclass
from typing import List, Optional
from models.requirement import Requirement
from exceptions import ValidationError


@dataclass
class ValidationResult:
    """Validation result with errors"""
    valid: bool
    errors: List[str]

    def __bool__(self) -> bool:
        return self.valid


class ValidationService:
    """Service for validating domain entities"""

    def validate_requirement(self, req: Requirement) -> ValidationResult:
        """
        Validate requirement entity

        Args:
            req: Requirement to validate

        Returns:
            ValidationResult with validation status and errors
        """
        errors = []

        # Validate ID format
        if not req.id or not req.id.startswith("REQ-"):
            errors.append("ID must start with 'REQ-'")

        if req.id and len(req.id) > 20:
            errors.append("ID must not exceed 20 characters")

        # Validate title
        if not req.title or len(req.title.strip()) == 0:
            errors.append("Title is required")

        if req.title and len(req.title) > 200:
            errors.append("Title must not exceed 200 characters")

        # Validate category
        if req.category and len(req.category) > 50:
            errors.append("Category must not exceed 50 characters")

        # Validate status
        try:
            if req.status not in [status for status in req.status.__class__]:
                errors.append(f"Invalid status: {req.status}")
        except:
            errors.append("Invalid status value")

        # Validate priority
        try:
            if req.priority not in [priority for priority in req.priority.__class__]:
                errors.append(f"Invalid priority: {req.priority}")
        except:
            errors.append("Invalid priority value")

        return ValidationResult(
            valid=len(errors) == 0,
            errors=errors
        )
