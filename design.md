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
          | ID | Title | Status | Priority | Category |
          | REQ-001 | User Authentication | Approved | High | Security |
          | REQ-002 | Data Persistence | Draft | Medium | Core |
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
        Linked Items:
        - DES-001: Authentication Module
        - DES-002: Login UI
        ---
        [Edit] [Delete] [Link] [Version History]
      }
    }
  }
  [Status Bar: 125 Requirements | 87 Designs | 203 Implementations | DB: project.db]
}
@enduml
```

### 5.2 Traceability View

```plantuml
@startuml
!theme plain

rectangle "Traceability View" {
  rectangle "Filter Panel" as filter {
    (Status)
    (Priority)
    (Date Range)
    (Entity Type)
  }

  rectangle "Visualization Panel" as viz {
    rectangle "REQ-001\nAuthentication" as req1 #lightblue
    rectangle "REQ-002\nData Layer" as req2 #lightblue

    rectangle "DES-001\nAuth Module" as des1 #lightgreen
    rectangle "DES-002\nDB Schema" as des2 #lightgreen

    rectangle "IMP-001\nauth.py" as imp1 #lightyellow
    rectangle "IMP-002\ndb.py" as imp2 #lightyellow

    req1 --> des1
    req2 --> des2
    des1 --> imp1
    des2 --> imp2
  }

  rectangle "Statistics Panel" as stats {
    - Total Requirements: 125
    - Requirements with Design: 98 (78%)
    - Designs with Implementation: 65 (75%)
    - Orphaned Requirements: 27
    - Orphaned Implementations: 15
  }
}

filter -down-> viz
viz -down-> stats

@enduml
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

### 6.3 Version History
- **Strategy**: Snapshot-based versioning with JSON serialization
- **Triggers**: Manual tagging and automatic change detection
- **Storage**: Compressed JSON in TEXT column
- **Rationale**: Simple implementation, full history retention, easy restore

### 6.4 Search and Filter
- **Implementation**: In-memory filtering with SQLite FTS5 extension for full-text search
- **Indexing**: Strategic indexes on frequently queried columns (status, dates, IDs)
- **Performance**: Query optimization for 1000+ items

### 6.5 Export Formats
- **CSV**: Simple tabular data for spreadsheet tools
- **Markdown**: Documentation-friendly format with links
- **JSON**: Full data export for backup and migration
- **DOT/GraphML**: Graph visualization for traceability

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
| Coverage | Percentage of items with trace links |
