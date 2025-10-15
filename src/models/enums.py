from enum import Enum


class RequirementStatus(Enum):
    """Requirement lifecycle status"""
    DRAFT = "Draft"
    UNDER_REVIEW = "Under Review"
    APPROVED = "Approved"
    IMPLEMENTED = "Implemented"
    OBSOLETE = "Obsolete"


class DesignStatus(Enum):
    """Design lifecycle status"""
    DRAFT = "Draft"
    UNDER_REVIEW = "Under Review"
    APPROVED = "Approved"
    IMPLEMENTED = "Implemented"


class ImplementationStatus(Enum):
    """Implementation lifecycle status"""
    NOT_STARTED = "Not Started"
    IN_PROGRESS = "In Progress"
    COMPLETED = "Completed"
    TESTED = "Tested"


class Priority(Enum):
    """Priority levels"""
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    CRITICAL = "Critical"


class LinkType(Enum):
    """Trace link types"""
    REQ_TO_DES = "req_to_des"
    DES_TO_IMP = "des_to_imp"


class EntityType(Enum):
    """Entity types for version history"""
    REQUIREMENT = "requirement"
    DESIGN = "design"
    IMPLEMENTATION = "implementation"
