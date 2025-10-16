# Dragon Application Lifecycle Management - Design Document

## 1. Overview

### 1.1 Purpose
This document describes the architectural and detailed design of the Dragon ALM system, a desktop-based application lifecycle management tool for individual developers.

### 1.2 Design Principles
- **Modularity**: Clear separation between data, business logic, and presentation layers
- **Maintainability**: MVC pattern with well-defined component responsibilities
- **Extensibility**: Plugin-ready architecture for future enhancements
- **Performance**: Efficient data access and caching strategies
- **Offline-First**: Complete functionality without network dependency

---

## 2. System Architecture

### 2.1 High-Level Architecture

```plantuml
@startuml
!theme plain

package "Presentation Layer" {
  [Main Window] as MainWin
  [Requirements View] as ReqView
  [Design View] as DesView
  [Implementation View] as ImpView
  [Traceability View] as TraceView
  [Settings View] as SettingsView
}

package "Application Layer" {
  [Requirements Controller] as ReqCtrl
  [Design Controller] as DesCtrl
  [Implementation Controller] as ImpCtrl
  [Traceability Controller] as TraceCtrl
  [Import/Export Controller] as IOCtrl
}

package "Business Logic Layer" {
  [Requirements Manager] as ReqMgr
  [Design Manager] as DesMgr
  [Implementation Manager] as ImpMgr
  [Traceability Manager] as TraceMgr
  [Validation Service] as ValSvc
  [Search Service] as SearchSvc
}

package "Data Access Layer" {
  [Repository Interface] as Repo
  [SQLite Repository] as SQLiteRepo
  [File System Repository] as FSRepo
}

database "Data Storage" {
  [SQLite Database] as DB
  [File System] as FS
}

MainWin --> ReqView
MainWin --> DesView
MainWin --> ImpView
MainWin --> TraceView
MainWin --> SettingsView

ReqView --> ReqCtrl
DesView --> DesCtrl
ImpView --> ImpCtrl
TraceView --> TraceCtrl

ReqCtrl --> ReqMgr
DesCtrl --> DesMgr
ImpCtrl --> ImpMgr
TraceCtrl --> TraceMgr

ReqMgr --> Repo
DesMgr --> Repo
ImpMgr --> Repo
TraceMgr --> Repo
ReqMgr --> ValSvc
DesMgr --> ValSvc
ImpMgr --> ValSvc

ReqMgr --> SearchSvc
DesMgr --> SearchSvc
ImpMgr --> SearchSvc

IOCtrl --> Repo

Repo <|-- SQLiteRepo
Repo <|-- FSRepo

SQLiteRepo --> DB
FSRepo --> FS

@enduml
```

### 2.2 Layer Responsibilities

#### 2.2.1 Presentation Layer
- **Responsibility**: User interface rendering and user interaction handling
- **Technology**: PyQt6 or customtkinter
- **Components**:
  - Main Window: Application container with menu bar and tab navigation
  - View Components: Specialized panels for each artifact type
  - Dialog Components: Modal dialogs for create/edit/delete operations
  - Visualization Components: Graph rendering for traceability matrix

#### 2.2.2 Application Layer (Controllers)
- **Responsibility**: Coordinate between views and business logic
- **Pattern**: MVC Controller pattern
- **Functions**:
  - Handle user actions from views
  - Invoke business logic operations
  - Update view state based on business logic results
  - Manage application state and navigation

#### 2.2.3 Business Logic Layer
- **Responsibility**: Core business rules and domain logic
- **Components**:
  - **Managers**: Domain-specific business logic for each artifact type
  - **Services**: Cross-cutting concerns (validation, search, etc.)
  - **Domain Models**: Entity classes with business behavior

#### 2.2.4 Data Access Layer
- **Responsibility**: Abstract data persistence operations
- **Pattern**: Repository pattern
- **Interface**: Generic CRUD operations and query methods
- **Implementations**:
  - SQLiteRepository: Primary data storage
  - FileSystemRepository: Export/import and backup operations

---

## 3. Data Model Design

### 3.1 Entity Relationship Diagram

```plantuml
@startuml
!theme plain

entity "Requirement" as req {
  * id : VARCHAR(20) PK
  --
  * title : VARCHAR(200)
  * description : TEXT
  * status : VARCHAR(20)
  * priority : VARCHAR(20)
  * category : VARCHAR(50)
  parent_id : VARCHAR(20) FK
  * created_at : TIMESTAMP
  * updated_at : TIMESTAMP
  verification_criteria : TEXT
}

entity "Design" as des {
  * id : VARCHAR(20) PK
  --
  * title : VARCHAR(200)
  * description : TEXT
  * status : VARCHAR(20)
  * author : VARCHAR(100)
  * created_at : TIMESTAMP
  * updated_at : TIMESTAMP
  verification_criteria : TEXT
}

entity "Implementation" as imp {
  * id : VARCHAR(20) PK
  --
  * file_path : VARCHAR(500)
  * function_name : VARCHAR(200)
  * description : TEXT
  * status : VARCHAR(20)
  * created_at : TIMESTAMP
  * updated_at : TIMESTAMP
  commit_id : VARCHAR(40)
  commit_message : TEXT
  verification_criteria : TEXT
}

entity "Trace_Req_Des" as trd {
  * req_id : VARCHAR(20) PK,FK
  * des_id : VARCHAR(20) PK,FK
  --
  * created_at : TIMESTAMP
  notes : TEXT
}

entity "Trace_Des_Imp" as tdi {
  * des_id : VARCHAR(20) PK,FK
  * imp_id : VARCHAR(20) PK,FK
  --
  * created_at : TIMESTAMP
  notes : TEXT
}

entity "Version_History" as ver {
  * id : INTEGER PK
  --
  * entity_type : VARCHAR(20)
  * entity_id : VARCHAR(20)
  * version_number : INTEGER
  * snapshot_data : TEXT
  * created_at : TIMESTAMP
  * created_by : VARCHAR(100)
  tag : VARCHAR(50)
}

req ||--o{ req : "parent-child"
req ||--o{ trd
des ||--o{ trd
des ||--o{ tdi
imp ||--o{ tdi
ver }o--|| req : "tracks"
ver }o--|| des : "tracks"
ver }o--|| imp : "tracks"

@enduml
```

### 3.2 Database Schema

#### Requirements Table
```sql
CREATE TABLE requirements (
    id VARCHAR(20) PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    status VARCHAR(20) NOT NULL DEFAULT 'Draft',
    priority VARCHAR(20) NOT NULL DEFAULT 'Medium',
    category VARCHAR(50),
    parent_id VARCHAR(20),
    verification_criteria TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (parent_id) REFERENCES requirements(id) ON DELETE SET NULL
);

CREATE INDEX idx_req_status ON requirements(status);
CREATE INDEX idx_req_parent ON requirements(parent_id);
```

#### Design Table
```sql
CREATE TABLE design (
    id VARCHAR(20) PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    status VARCHAR(20) NOT NULL DEFAULT 'Draft',
    author VARCHAR(100),
    verification_criteria TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_des_status ON design(status);
```

#### Implementation Table
```sql
CREATE TABLE implementation (
    id VARCHAR(20) PRIMARY KEY,
    file_path VARCHAR(500) NOT NULL,
    function_name VARCHAR(200),
    description TEXT,
    status VARCHAR(20) NOT NULL DEFAULT 'Not Started',
    commit_id VARCHAR(40),
    commit_message TEXT,
    verification_criteria TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_imp_file ON implementation(file_path);
CREATE INDEX idx_imp_status ON implementation(status);
```

#### Trace Tables
```sql
CREATE TABLE trace_req_des (
    req_id VARCHAR(20),
    des_id VARCHAR(20),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (req_id, des_id),
    FOREIGN KEY (req_id) REFERENCES requirements(id) ON DELETE CASCADE,
    FOREIGN KEY (des_id) REFERENCES design(id) ON DELETE CASCADE
);

CREATE TABLE trace_des_imp (
    des_id VARCHAR(20),
    imp_id VARCHAR(20),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (des_id, imp_id),
    FOREIGN KEY (des_id) REFERENCES design(id) ON DELETE CASCADE,
    FOREIGN KEY (imp_id) REFERENCES implementation(id) ON DELETE CASCADE
);
```

#### Version History Table
```sql
CREATE TABLE version_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    entity_type VARCHAR(20) NOT NULL,
    entity_id VARCHAR(20) NOT NULL,
    version_number INTEGER NOT NULL,
    snapshot_data TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(100),
    tag VARCHAR(50)
);

CREATE INDEX idx_ver_entity ON version_history(entity_type, entity_id);
CREATE INDEX idx_ver_tag ON version_history(tag);
```

---

## 4. Component Design

### 4.1 Domain Models

```plantuml
@startuml
!theme plain

class Requirement {
  - id: str
  - title: str
  - description: str
  - status: RequirementStatus
  - priority: Priority
  - category: str
  - parent_id: Optional[str]
  - verification_criteria: str
  - created_at: datetime
  - updated_at: datetime
  --
  + validate(): bool
  + get_children(): List[Requirement]
  + get_linked_designs(): List[Design]
  + to_dict(): dict
  + from_dict(data: dict): Requirement
}

class Design {
  - id: str
  - title: str
  - description: str
  - status: DesignStatus
  - author: str
  - verification_criteria: str
  - created_at: datetime
  - updated_at: datetime
  --
  + validate(): bool
  + get_linked_requirements(): List[Requirement]
  + get_linked_implementations(): List[Implementation]
  + to_dict(): dict
  + from_dict(data: dict): Design
}

class Implementation {
  - id: str
  - file_path: str
  - function_name: str
  - description: str
  - status: ImplementationStatus
  - commit_id: str
  - commit_message: str
  - verification_criteria: str
  - created_at: datetime
  - updated_at: datetime
  --
  + validate(): bool
  + get_linked_designs(): List[Design]
  + to_dict(): dict
  + from_dict(data: dict): Implementation
}

class TraceLink {
  - source_id: str
  - target_id: str
  - link_type: LinkType
  - notes: str
  - created_at: datetime
  --
  + validate(): bool
  + to_dict(): dict
}

enum RequirementStatus {
  DRAFT
  UNDER_REVIEW
  APPROVED
  IMPLEMENTED
  OBSOLETE
}

enum DesignStatus {
  DRAFT
  UNDER_REVIEW
  APPROVED
  IMPLEMENTED
}

enum ImplementationStatus {
  NOT_STARTED
  IN_PROGRESS
  COMPLETED
  TESTED
}

enum Priority {
  LOW
  MEDIUM
  HIGH
  CRITICAL
}

enum LinkType {
  REQ_TO_DES
  DES_TO_IMP
}

Requirement --> RequirementStatus
Requirement --> Priority
Design --> DesignStatus
Implementation --> ImplementationStatus
TraceLink --> LinkType

@enduml
```

### 4.2 Manager Classes

```plantuml
@startuml
!theme plain

interface IRepository {
  + create(entity): str
  + read(id: str): Entity
  + update(entity): bool
  + delete(id: str): bool
  + find_all(): List[Entity]
  + find_by_criteria(criteria): List[Entity]
}

class RequirementManager {
  - repository: IRepository
  - validation_service: ValidationService
  --
  + create_requirement(data: dict): Requirement
  + update_requirement(id: str, data: dict): Requirement
  + delete_requirement(id: str): bool
  + get_requirement(id: str): Requirement
  + get_all_requirements(): List[Requirement]
  + search_requirements(query: str): List[Requirement]
  + get_children(parent_id: str): List[Requirement]
  + link_to_design(req_id: str, des_id: str): bool
  + unlink_from_design(req_id: str, des_id: str): bool
}

class DesignManager {
  - repository: IRepository
  - validation_service: ValidationService
  --
  + create_design(data: dict): Design
  + update_design(id: str, data: dict): Design
  + delete_design(id: str): bool
  + get_design(id: str): Design
  + get_all_designs(): List[Design]
  + search_designs(query: str): List[Design]
  + link_to_requirement(des_id: str, req_id: str): bool
  + link_to_implementation(des_id: str, imp_id: str): bool
  + unlink_from_requirement(des_id: str, req_id: str): bool
  + unlink_from_implementation(des_id: str, imp_id: str): bool
}

class ImplementationManager {
  - repository: IRepository
  - validation_service: ValidationService
  --
  + create_implementation(data: dict): Implementation
  + update_implementation(id: str, data: dict): Implementation
  + delete_implementation(id: str): bool
  + get_implementation(id: str): Implementation
  + get_all_implementations(): List[Implementation]
  + search_implementations(query: str): List[Implementation]
  + link_to_design(imp_id: str, des_id: str): bool
  + unlink_from_design(imp_id: str, des_id: str): bool
  + update_version_info(id: str, commit_id: str, message: str): bool
}

class TraceabilityManager {
  - repository: IRepository
  --
  + get_trace_matrix(): TraceMatrix
  + get_forward_trace(req_id: str): TraceResult
  + get_backward_trace(imp_id: str): TraceResult
  + get_orphaned_items(): OrphanedItems
  + export_trace_matrix(format: str): str
  + visualize_traces(): Graph
}

class ValidationService {
  + validate_requirement(req: Requirement): ValidationResult
  + validate_design(des: Design): ValidationResult
  + validate_implementation(imp: Implementation): ValidationResult
  + validate_trace_link(link: TraceLink): ValidationResult
}

class SearchService {
  + search_all(query: str): SearchResult
  + search_by_type(type: str, query: str): List[Entity]
  + filter_by_status(entities: List[Entity], status: str): List[Entity]
  + filter_by_date_range(entities: List[Entity], start: date, end: date): List[Entity]
}

RequirementManager --> IRepository
DesignManager --> IRepository
ImplementationManager --> IRepository
TraceabilityManager --> IRepository

RequirementManager --> ValidationService
DesignManager --> ValidationService
ImplementationManager --> ValidationService

RequirementManager --> SearchService
DesignManager --> SearchService
ImplementationManager --> SearchService

@enduml
```

### 4.3 Traceability Visualization

```plantuml
@startuml
!theme plain

class TraceMatrix {
  - requirements: List[Requirement]
  - designs: List[Design]
  - implementations: List[Implementation]
  - traces: List[TraceLink]
  --
  + build_matrix(): Matrix
  + get_coverage_statistics(): CoverageStats
  + find_gaps(): List[GapInfo]
  + export_to_csv(): str
  + export_to_markdown(): str
}

class TraceGraph {
  - nodes: List[Node]
  - edges: List[Edge]
  --
  + add_node(entity): Node
  + add_edge(source: Node, target: Node): Edge
  + render(): Image
  + export_to_dot(): str
  + get_connected_components(): List[Component]
}

class Node {
  - id: str
  - type: NodeType
  - label: str
  - metadata: dict
  --
  + get_neighbors(): List[Node]
}

class Edge {
  - source: Node
  - target: Node
  - type: LinkType
  --
  + get_weight(): float
}

enum NodeType {
  REQUIREMENT
  DESIGN
  IMPLEMENTATION
}

TraceMatrix --> TraceGraph
TraceGraph --> Node
TraceGraph --> Edge
Node --> NodeType

@enduml
```

---

## 5. User Interface Design

### 5.1 Main Window Layout

```plantuml
@startuml
salt
{+
  {/ <b>Dragon ALM | File | Edit | View | Tools | Help}
  {T+
    + Requirements | Design | Implementation | Traceability | Settings
    Requirements Tab
    {
      {
        {T
          | ID | Title | Status | Priority | Traces |
          | REQ-001 | User Authentication | Approved | High | ✓ 2 Designs |
          | REQ-002 | Data Persistence | Draft | Medium | ⚠ 0 Designs |
        }
      } | {
        <b>Details
        ---
        ID: REQ-001
        Title: User Authentication
        Status: Approved
        Priority: High
        Category: Security
        ---
        Description:
        { . }
        ---
        Verification Criteria:
        { . }
        ---
        <b>Traceability
        <b>Linked Designs (2):
        ↓ DES-001: Authentication Module [Notes] [×]
        ↓ DES-002: Login UI [Notes] [×]
        [+ Add Design Link]

        <b>Complete Trace Paths:
        REQ-001 → DES-001 → IMP-001 (auth.py)
        REQ-001 → DES-002 → IMP-003 (ui/login.py)
        ---
        [Edit] [Delete] [Version History]
      }
    }
  }
  [Status Bar: 125 Requirements | 87 Designs | 203 Implementations | Coverage: 78% | DB: project.db]
}
@enduml
```

### 5.2 Design View with Traceability

```plantuml
@startuml
salt
{+
  {T+
    + Requirements | Design | Implementation | Traceability | Settings
    Design Tab
    {
      {
        {T
          | ID | Title | Status | Req ↔ Imp |
          | DES-001 | Auth Module | Approved | ✓ 1 ↔ 2 |
          | DES-002 | DB Schema | Draft | ✓ 1 ↔ 0 |
        }
      } | {
        <b>Details
        ---
        ID: DES-001
        Title: Authentication Module
        Status: Approved
        Author: Dev Team
        ---
        Description:
        { . }
        ---
        <b>Traceability
        <b>Backward Traces - Linked Requirements (1):
        ↑ REQ-001: User Authentication [Notes] [×]
        [+ Add Requirement Link]

        <b>Forward Traces - Linked Implementations (2):
        ↓ IMP-001: auth.py::authenticate() [Notes] [×]
        ↓ IMP-002: auth.py::validate_token() [Notes] [×]
        [+ Add Implementation Link]

        <b>Complete Trace Paths:
        REQ-001 → DES-001 → IMP-001
        REQ-001 → DES-001 → IMP-002

        <b>Coverage Status:
        Requirements: ✓ Complete (1/1)
        Implementations: ✓ Complete (2 linked)
        ---
        [Edit] [Delete] [Version History]
      }
    }
  }
}
@enduml
```

### 5.3 Implementation View with Traceability

```plantuml
@startuml
salt
{+
  {T+
    + Requirements | Design | Implementation | Traceability | Settings
    Implementation Tab
    {
      {
        {T
          | ID | File Path | Function | Status | Traces |
          | IMP-001 | auth.py | authenticate() | Tested | ✓ Path |
          | IMP-002 | db.py | connect() | In Progress | ⚠ No Design |
        }
      } | {
        <b>Details
        ---
        ID: IMP-001
        File: src/auth.py
        Function: authenticate()
        Status: Tested
        Commit: abc123
        ---
        Description:
        { . }
        ---
        <b>Traceability
        <b>Backward Traces - Linked Designs (1):
        ↑ DES-001: Authentication Module [Notes] [×]
        [+ Add Design Link]

        <b>Indirect Requirements (via designs):
        ↑↑ REQ-001: User Authentication (via DES-001)

        <b>Complete Trace Path:
        REQ-001 → DES-001 → IMP-001

        <b>Coverage Status:
        Design Links: ✓ Complete (1/1 expected)
        Requirement Traceability: ✓ Complete
        ---
        [Edit] [Delete] [Version History] [View Code]
      }
    }
  }
}
@enduml
```

### 5.4 Traceability View (Global)

```plantuml
@startuml
!theme plain

rectangle "Traceability View" {
  rectangle "Filter Panel" as filter {
    (Status)
    (Priority)
    (Date Range)
    (Entity Type)
    (Coverage Filter)
  }

  rectangle "Visualization Panel" as viz {
    rectangle "REQ-001\nAuthentication\n✓ Complete" as req1 #lightblue
    rectangle "REQ-002\nData Layer\n⚠ No Design" as req2 #lightyellow

    rectangle "DES-001\nAuth Module\n✓ Complete" as des1 #lightgreen
    rectangle "DES-002\nDB Schema\n⚠ No Impl" as des2 #lightyellow

    rectangle "IMP-001\nauth.py\n✓ Complete" as imp1 #lightgreen
    rectangle "IMP-002\ndb.py\n⚠ No Design" as imp2 #lightyellow

    req1 --> des1 : "Trace note:\nCore feature"
    req2 ..> des2 : "Missing\nlink"
    des1 --> imp1
    des2 ..> imp2 : "Missing\nlink"
  }

  rectangle "Statistics Panel" as stats {
    <b>Coverage Statistics:
    - Total Requirements: 125
    - Requirements with Design: 98 (78%) ✓
    - Designs with Implementation: 65 (75%) ✓
    - Complete Trace Paths: 60 (48%)

    <b>Issues:
    - Orphaned Requirements: 27 ⚠
    - Orphaned Designs: 12 ⚠
    - Orphaned Implementations: 15 ⚠

    [Export Matrix] [Show Gaps] [Fix Orphans]
  }

  rectangle "Actions Panel" as actions {
    [Create Links] [Bulk Link] [Validate All]
  }
}

filter -down-> viz
viz -down-> stats
stats -down-> actions

@enduml
```

### 5.5 Trace Link Dialog

```plantuml
@startuml
salt
{
  <b>Create Trace Link
  {
    Source: | REQ-001: User Authentication
    Target Type: | ^Design^
    Available Targets:
    {T
      | ID | Title | Status |
      | DES-001 | Auth Module | Approved |
      | DES-002 | Login UI | Draft |
      | DES-003 | Session Management | Draft |
    }
    Notes:
    { . Core security feature implementation }
    [Create Link] | [Cancel]
  }
}
@enduml
```

### 5.6 Traceability Panel Component (Reusable)

The traceability panel is a reusable component that appears in all artifact detail views:

```python
class TraceabilityPanel(QWidget):
    """
    Reusable traceability panel for artifact views.
    Shows backward and forward traces with inline actions.
    """
    def __init__(self, artifact_type: str):
        self.artifact_type = artifact_type  # 'requirement', 'design', 'implementation'
        self.backward_section = TraceLinkSection("backward")
        self.forward_section = TraceLinkSection("forward")
        self.coverage_indicator = CoverageIndicator()
        self.trace_path_view = TracePathView()

    def display_traces(self, artifact_id: str):
        """Display all traces for the given artifact"""
        pass

    def add_link_action(self, direction: str):
        """Handle adding a new trace link"""
        pass

    def remove_link_action(self, link_id: str):
        """Handle removing a trace link"""
        pass

    def navigate_to_linked_artifact(self, artifact_id: str):
        """Navigate to the linked artifact"""
        pass

class TraceLinkSection(QWidget):
    """
    Section showing trace links in one direction.
    Displays: icon, artifact_id, title, [notes] [×]
    """
    pass

class CoverageIndicator(QWidget):
    """
    Visual indicator of traceability coverage.
    Shows: ✓ Complete, ⚠ Partial, × Missing
    """
    pass

class TracePathView(QWidget):
    """
    Displays complete trace paths.
    Example: REQ-001 → DES-001 → IMP-001
    """
    pass
```

---

## 6. Key Design Decisions

### 6.1 ID Generation Strategy
- **Format**: `{PREFIX}-{NUMBER}` (e.g., REQ-001, DES-001, IMP-001)
- **Implementation**: Auto-increment with prefix based on entity type
- **Rationale**: Human-readable, sortable, and supports easy referencing

### 6.2 Trace Link Management
- **Approach**: Separate junction tables for each trace relationship type
- **Benefits**:
  - Explicit relationship modeling
  - Easy query and navigation
  - Support for relationship metadata (notes, dates)
- **Trade-off**: More tables but clearer semantics

### 6.3 In-View Traceability Display
- **Strategy**: Embed traceability information directly in artifact detail panels
- **Benefits**:
  - Immediate visibility of relationships
  - Reduced context switching
  - Faster link management
  - Better understanding of artifact context
- **Implementation**: Reusable TraceabilityPanel component
- **Performance**: Lazy loading of trace data when artifact is selected

### 6.4 Trace Link Notes
- **Purpose**: Provide context for why artifacts are linked
- **Storage**: TEXT field in trace junction tables
- **Display**: Inline with trace links, expandable for long notes
- **Edit**: Quick edit action without modal dialog

### 6.5 Coverage Indicators
- **Visual Design**: Color-coded badges (green ✓, yellow ⚠, red ×)
- **Levels**:
  - ✓ Complete: All expected traces exist
  - ⚠ Partial: Some traces exist but incomplete
  - × Missing: No traces exist
- **Display**: In table columns, detail panels, and statistics

### 6.6 Version History
- **Strategy**: Snapshot-based versioning with JSON serialization
- **Triggers**: Manual tagging and automatic change detection
- **Storage**: Compressed JSON in TEXT column
- **Rationale**: Simple implementation, full history retention, easy restore

### 6.7 Search and Filter
- **Implementation**: In-memory filtering with SQLite FTS5 extension for full-text search
- **Indexing**: Strategic indexes on frequently queried columns (status, dates, IDs)
- **Performance**: Query optimization for 1000+ items

### 6.8 Export Formats
- **CSV**: Simple tabular data for spreadsheet tools
- **Markdown**: Documentation-friendly format with links
- **JSON**: Full data export for backup and migration
- **DOT/GraphML**: Graph visualization for traceability
```

```markdown path=/Users/jaeyong/workspace/dragon/dragon-alm/design.md start_line=325 end_line=440
---

## 4. Component Design

### 4.1 Domain Models

```plantuml
@startuml
!theme plain

class Requirement {
  - id: str
  - title: str
  - description: str
  - status: RequirementStatus
  - priority: Priority
  - category: str
  - parent_id: Optional[str]
  - verification_criteria: str
  - created_at: datetime
  - updated_at: datetime
  --
  + validate(): bool
  + get_children(): List[Requirement]
  + get_linked_designs(): List[Design]
  + get_trace_paths(): List[TracePath]
  + get_coverage_status(): CoverageStatus
  + to_dict(): dict
  + from_dict(data: dict): Requirement
}

class Design {
  - id: str
  - title: str
  - description: str
  - status: DesignStatus
  - author: str
  - verification_criteria: str
  - created_at: datetime
  - updated_at: datetime
  --
  + validate(): bool
  + get_linked_requirements(): List[Requirement]
  + get_linked_implementations(): List[Implementation]
  + get_trace_paths(): List[TracePath]
  + get_coverage_status(): CoverageStatus
  + to_dict(): dict
  + from_dict(data: dict): Design
}

class Implementation {
  - id: str
  - file_path: str
  - function_name: str
  - description: str
  - status: ImplementationStatus
  - commit_id: str
  - commit_message: str
  - verification_criteria: str
  - created_at: datetime
  - updated_at: datetime
  --
  + validate(): bool
  + get_linked_designs(): List[Design]
  + get_indirect_requirements(): List[Requirement]
  + get_trace_paths(): List[TracePath]
  + get_coverage_status(): CoverageStatus
  + to_dict(): dict
  + from_dict(data: dict): Implementation
}

class TraceLink {
  - source_id: str
  - target_id: str
  - link_type: LinkType
  - notes: str
  - created_at: datetime
  --
  + validate(): bool
  + get_source_artifact(): Entity
  + get_target_artifact(): Entity
  + to_dict(): dict
}

class TracePath {
  - requirement: Requirement
  - design: Optional[Design]
  - implementation: Optional[Implementation]
  - is_complete: bool
  --
  + get_path_string(): str
  + get_gaps(): List[str]
}

class CoverageStatus {
  - has_forward_links: bool
  - has_backward_links: bool
  - complete_path_count: int
  - status_level: CoverageLevel
  --
  + get_status_icon(): str
  + get_status_color(): str
}

enum RequirementStatus {
  DRAFT
  UNDER_REVIEW
  APPROVED
  IMPLEMENTED
  OBSOLETE
}

enum DesignStatus {
  DRAFT
  UNDER_REVIEW
  APPROVED
  IMPLEMENTED
}

enum ImplementationStatus {
  NOT_STARTED
  IN_PROGRESS
  COMPLETED
  TESTED
}

enum Priority {
  LOW
  MEDIUM
  HIGH
  CRITICAL
}

enum LinkType {
  REQ_TO_DES
  DES_TO_IMP
}

enum CoverageLevel {
  COMPLETE
  PARTIAL
  MISSING
}

Requirement --> RequirementStatus
Requirement --> Priority
Requirement --> TracePath
Requirement --> CoverageStatus
Design --> DesignStatus
Design --> TracePath
Design --> CoverageStatus
Implementation --> ImplementationStatus
Implementation --> TracePath
Implementation --> CoverageStatus
TraceLink --> LinkType
TracePath --> Requirement
TracePath --> Design
TracePath --> Implementation
CoverageStatus --> CoverageLevel

@enduml
```

### 4.2 Manager Classes

```plantuml
@startuml
!theme plain

interface IRepository {
  + create(entity): str
  + read(id: str): Entity
  + update(entity): bool
  + delete(id: str): bool
  + find_all(): List[Entity]
  + find_by_criteria(criteria): List[Entity]
}

class RequirementManager {
  - repository: IRepository
  - validation_service: ValidationService
  - trace_service: TraceService
  --
  + create_requirement(data: dict): Requirement
  + update_requirement(id: str, data: dict): Requirement
  + delete_requirement(id: str): bool
  + get_requirement(id: str): Requirement
  + get_all_requirements(): List[Requirement]
  + search_requirements(query: str): List[Requirement]
  + get_children(parent_id: str): List[Requirement]
  + get_linked_designs(req_id: str): List[Design]
  + get_trace_paths(req_id: str): List[TracePath]
  + get_coverage_status(req_id: str): CoverageStatus
  + link_to_design(req_id: str, des_id: str, notes: str): bool
  + unlink_from_design(req_id: str, des_id: str): bool
  + update_trace_notes(req_id: str, des_id: str, notes: str): bool
}

class DesignManager {
  - repository: IRepository
  - validation_service: ValidationService
  - trace_service: TraceService
  --
  + create_design(data: dict): Design
  + update_design(id: str, data: dict): Design
  + delete_design(id: str): bool
  + get_design(id: str): Design
  + get_all_designs(): List[Design]
  + search_designs(query: str): List[Design]
  + get_linked_requirements(des_id: str): List[Requirement]
  + get_linked_implementations(des_id: str): List[Implementation]
  + get_trace_paths(des_id: str): List[TracePath]
  + get_coverage_status(des_id: str): CoverageStatus
  + link_to_requirement(des_id: str, req_id: str, notes: str): bool
  + link_to_implementation(des_id: str, imp_id: str, notes: str): bool
  + unlink_from_requirement(des_id: str, req_id: str): bool
  + unlink_from_implementation(des_id: str, imp_id: str): bool
  + update_trace_notes(des_id: str, target_id: str, notes: str): bool
}

class ImplementationManager {
  - repository: IRepository
  - validation_service: ValidationService
  - trace_service: TraceService
  --
  + create_implementation(data: dict): Implementation
  + update_implementation(id: str, data: dict): Implementation
  + delete_implementation(id: str): bool
  + get_implementation(id: str): Implementation
  + get_all_implementations(): List[Implementation]
  + search_implementations(query: str): List[Implementation]
  + get_linked_designs(imp_id: str): List[Design]
  + get_indirect_requirements(imp_id: str): List[Requirement]
  + get_trace_paths(imp_id: str): List[TracePath]
  + get_coverage_status(imp_id: str): CoverageStatus
  + link_to_design(imp_id: str, des_id: str, notes: str): bool
  + unlink_from_design(imp_id: str, des_id: str): bool
  + update_trace_notes(imp_id: str, des_id: str, notes: str): bool
  + update_version_info(id: str, commit_id: str, message: str): bool
}

class TraceabilityManager {
  - repository: IRepository
  --
  + get_trace_matrix(): TraceMatrix
  + get_forward_trace(req_id: str): TraceResult
  + get_backward_trace(imp_id: str): TraceResult
  + get_trace_paths(artifact_id: str): List[TracePath]
  + get_orphaned_items(): OrphanedItems
  + calculate_coverage(): CoverageStatistics
  + export_trace_matrix(format: str): str
  + visualize_traces(): Graph
}

class TraceService {
  - repository: IRepository
  --
  + get_linked_artifacts(artifact_id: str, direction: str): List[Entity]
  + create_trace_link(source_id: str, target_id: str, notes: str): TraceLink
  + delete_trace_link(source_id: str, target_id: str): bool
  + update_trace_notes(source_id: str, target_id: str, notes: str): bool
  + get_trace_link_details(source_id: str, target_id: str): TraceLink
  + build_trace_paths(artifact_id: str): List[TracePath]
  + calculate_coverage_status(artifact_id: str, artifact_type: str): CoverageStatus
  + validate_trace_link(source_id: str, target_id: str): ValidationResult
}

class ValidationService {
  + validate_requirement(req: Requirement): ValidationResult
  + validate_design(des: Design): ValidationResult
  + validate_implementation(imp: Implementation): ValidationResult
  + validate_trace_link(link: TraceLink): ValidationResult
}

class SearchService {
  + search_all(query: str): SearchResult
  + search_by_type(type: str, query: str): List[Entity]
  + filter_by_status(entities: List[Entity], status: str): List[Entity]
  + filter_by_date_range(entities: List[Entity], start: date, end: date): List[Entity]
  + filter_by_coverage(entities: List[Entity], level: CoverageLevel): List[Entity]
}

RequirementManager --> IRepository
DesignManager --> IRepository
ImplementationManager --> IRepository
TraceabilityManager --> IRepository

RequirementManager --> ValidationService
DesignManager --> ValidationService
ImplementationManager --> ValidationService

RequirementManager --> TraceService
DesignManager --> TraceService
ImplementationManager --> TraceService

RequirementManager --> SearchService
DesignManager --> SearchService
ImplementationManager --> SearchService

@enduml
```
```

These updates provide:

1. **In-View Traceability**: Each artifact view (requirement, design, implementation) now displays its trace relationships directly in the detail panel
2. **Bidirectional Navigation**: Users can see both forward and backward traces without leaving the current view
3. **Quick Actions**: Add/remove trace links directly from artifact views
4. **Coverage Indicators**: Visual status badges showing traceability completeness
5. **Complete Trace Paths**: Shows the full requirement → design → implementation chain
6. **Reusable Components**: TraceabilityPanel component can be embedded in all artifact views
7. **Enhanced Domain Models**: Added methods for getting trace paths and coverage status
8. **New TraceService**: Centralized service for trace link operations used across all managers

The design maintains separation of concerns while providing rich traceability features directly in the context where users need them.

---

## 7. Sequence Diagrams

### 7.1 Create Requirement Flow

```plantuml
@startuml
!theme plain

actor User
participant "Requirements\nView" as View
participant "Requirements\nController" as Ctrl
participant "Requirements\nManager" as Mgr
participant "Validation\nService" as Val
participant "Repository" as Repo
database "SQLite DB" as DB

User -> View: Click "New Requirement"
View -> View: Show Create Dialog
User -> View: Enter requirement data
View -> Ctrl: create_requirement(data)
Ctrl -> Mgr: create_requirement(data)
Mgr -> Val: validate_requirement(req)
Val -> Mgr: ValidationResult(valid=True)
Mgr -> Mgr: Generate ID
Mgr -> Repo: create(requirement)
Repo -> DB: INSERT INTO requirements
DB -> Repo: Success
Repo -> Mgr: req_id
Mgr -> Ctrl: Requirement object
Ctrl -> View: Update view
View -> User: Display new requirement

@enduml
```

### 7.2 Trace Link Creation Flow

```plantuml
@startuml
!theme plain

actor User
participant "Traceability\nView" as View
participant "Traceability\nController" as Ctrl
participant "Traceability\nManager" as Mgr
participant "Repository" as Repo
database "SQLite DB" as DB

User -> View: Select REQ-001 and DES-001
User -> View: Click "Create Link"
View -> Ctrl: create_trace_link(req_id, des_id)
Ctrl -> Mgr: link_requirement_to_design(req_id, des_id)
Mgr -> Repo: create_trace(req_id, des_id)
Repo -> DB: INSERT INTO trace_req_des
DB -> Repo: Success
Repo -> Mgr: True
Mgr -> Mgr: Invalidate cache
Mgr -> Ctrl: Success
Ctrl -> View: Refresh visualization
View -> User: Show updated trace graph

@enduml
```

### 7.3 Export Traceability Matrix Flow

```plantuml
@startuml
!theme plain

actor User
participant "Traceability\nView" as View
participant "Export\nController" as Ctrl
participant "Traceability\nManager" as Mgr
participant "Repository" as Repo
participant "File System" as FS

User -> View: Click "Export Matrix"
View -> View: Show format selection (CSV/MD)
User -> View: Select CSV format
View -> Ctrl: export_matrix(format='csv')
Ctrl -> Mgr: get_trace_matrix()
Mgr -> Repo: get_all_requirements()
Mgr -> Repo: get_all_designs()
Mgr -> Repo: get_all_implementations()
Mgr -> Repo: get_all_traces()
Mgr -> Mgr: Build matrix
Mgr -> Ctrl: TraceMatrix object
Ctrl -> Ctrl: Format as CSV
Ctrl -> FS: Write to file
FS -> Ctrl: File path
Ctrl -> View: Export complete
View -> User: Show success message

@enduml
```

---

## 8. Error Handling Strategy

### 8.1 Error Categories
1. **Validation Errors**: Invalid input data
2. **Database Errors**: Connection, constraint violations
3. **File I/O Errors**: Import/export failures
4. **Business Logic Errors**: Circular dependencies, orphaned links

### 8.2 Error Handling Pattern
```python
class ALMException(Exception):
    """Base exception for ALM system"""
    pass

class ValidationError(ALMException):
    """Raised when validation fails"""
    pass

class DatabaseError(ALMException):
    """Raised on database operations"""
    pass

class TraceError(ALMException):
    """Raised on trace link operations"""
    pass
```

### 8.3 User Feedback
- **Error Messages**: Clear, actionable messages in dialog boxes
- **Logging**: Comprehensive logging to file for debugging
- **Rollback**: Transaction-based operations with automatic rollback on failure

---

## 9. Performance Considerations

### 9.1 Caching Strategy
- **Entity Cache**: LRU cache for frequently accessed entities
- **Trace Cache**: In-memory graph structure for traceability queries
- **Search Index**: Materialized view for full-text search

### 9.2 Database Optimization
- **Indexes**: Strategic indexes on foreign keys and filter columns
- **Batch Operations**: Bulk inserts/updates for import operations
- **Connection Pooling**: Reuse database connections

### 9.3 UI Responsiveness
- **Lazy Loading**: Load data on-demand for large datasets
- **Pagination**: Display limited rows with pagination controls
- **Background Tasks**: Long-running operations in separate threads

---

## 10. Testing Strategy

### 10.1 Unit Tests
- Test each manager class independently
- Mock repository layer
- Test validation logic thoroughly

### 10.2 Integration Tests
- Test end-to-end flows with real database
- Test trace link integrity
- Test import/export operations

### 10.3 UI Tests
- Manual testing of all UI interactions
- Test responsiveness with large datasets
- Test error handling and user feedback

---

## 11. Implementation Phases

### Phase 1: Core Foundation
- Database schema setup
- Domain models
- Repository implementation
- Basic CRUD operations

### Phase 2: Business Logic
- Manager classes
- Validation service
- Search service
- Trace link management

### Phase 3: User Interface
- Main window and tabs
- Requirements view
- Design view
- Implementation view

### Phase 4: Traceability
- Trace matrix generation
- Visualization
- Export functionality

### Phase 5: Advanced Features
- Version history
- Import/export
- Backup/restore
- Settings and preferences

---

## 12. Glossary

| Term | Definition |
|------|------------|
| Entity | Base abstraction for Requirement, Design, or Implementation |
| Trace Link | Relationship between two entities |
| Trace Matrix | Tabular view showing all trace relationships |
| Forward Trace | Navigation from requirements to implementation |
| Backward Trace | Navigation from implementation to requirements |
| Orphaned Item | Entity with no trace links |
