from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, Any
from models.enums import RequirementStatus, Priority


@dataclass
class Requirement:
    """Requirement domain model"""
    id: str
    title: str
    description: str
    status: RequirementStatus
    priority: Priority
    category: str
    parent_id: Optional[str] = None
    verification_criteria: str = ""
    design_ids: list = field(default_factory=list)  # Linked design IDs
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def validate(self) -> bool:
        """Validate requirement data"""
        if not self.id or not self.id.startswith("REQ-"):
            return False
        if not self.title or len(self.title.strip()) == 0:
            return False
        if len(self.title) > 200:
            return False
        if self.category and len(self.category) > 50:
            return False
        return True

    def to_dict(self) -> Dict[str, Any]:
        """Convert requirement to dictionary"""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'status': self.status.value,
            'priority': self.priority.value,
            'category': self.category,
            'parent_id': self.parent_id,
            'verification_criteria': self.verification_criteria,
            'design_ids': self.design_ids,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Requirement':
        """Create requirement from dictionary"""
        return cls(
            id=data['id'],
            title=data['title'],
            description=data.get('description', ''),
            status=RequirementStatus(data.get('status', 'Draft')),
            priority=Priority(data.get('priority', 'Medium')),
            category=data.get('category', ''),
            parent_id=data.get('parent_id'),
            verification_criteria=data.get('verification_criteria', ''),
            design_ids=data.get('design_ids', []),
            created_at=datetime.fromisoformat(data['created_at'])
                if isinstance(data.get('created_at'), str)
                else data.get('created_at', datetime.now()),
            updated_at=datetime.fromisoformat(data['updated_at'])
                if isinstance(data.get('updated_at'), str)
                else data.get('updated_at', datetime.now())
        )

    def __str__(self) -> str:
        return f"{self.id}: {self.title} [{self.status.value}]"

    def __repr__(self) -> str:
        return (f"Requirement(id='{self.id}', title='{self.title}', "
                f"status={self.status.value}, priority={self.priority.value})")
