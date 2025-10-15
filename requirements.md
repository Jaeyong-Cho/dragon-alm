# Dragon Application Lifecycle Management - Requirements Specification

## 1. Overview

### 1.1 Purpose
The goal of this project is to develop a lightweight, standalone **Application Lifecycle Management (ALM)** tool that allows individual developers to manage and maintain traceability among **Requirements**, **Design**, and **Implementation (Code)** elements.

### 1.2 Scope
- Desktop-based ALM tool for individual developers or small teams
- Built with Python (GUI framework such as PyQt)
- Local database using SQLite
- Fully offline operation (no network dependency)

---

## 2. Functional Requirements

### 2.1 Requirements Management
- [REQ-001] The user can create, edit, and delete requirement items.
- [REQ-002] Each requirement has a unique ID (e.g., `REQ-001`).
- [REQ-003] Each requirement includes: title, description, creation date, status (Draft, Approved, etc.), category, and priority.
- [REQ-004] Requirements can have parent-child relationships.
- [REQ-005] Requirements can be linked to design items and implementation items.
- [REQ-006] Each item (requirement, design, implementation) shall include verification criteria or test properties to validate correctness and completeness.

### 2.2 Design Management
- [DES-001] The user can create, edit, and delete design items.
- [DES-002] Each design item has a unique ID (e.g., `DES-001`).
- [DES-003] Each design item maintains trace links to related requirements.
- [DES-004] Each design item includes: title, detailed description, author, creation/modification date, and status.
- [DES-005] Each design item can be linked to multiple implementation items.

### 2.3 Implementation (Code) Management
- [IMP-001] The user can register and manage implementation items (code modules or functions).
- [IMP-003] Each implementation item includes: file path, class/function name, and description.
- [IMP-004] Implementation items can be linked to one or more design items.
- [IMP-005] The system can store source code version history (commit ID, date, message).

### 2.4 Traceability Management
- [TRC-001] The tool visualizes relationships among requirements, design, and implementation.
- [TRC-002] The user can generate and export a Traceability Matrix (CSV or Markdown format).
- [TRC-003] The user can trace forward from requirements to design and implementation.
- [TRC-004] The user can trace backward (e.g., from implementation to requirements).
- [TRC-005] Any change in trace relationships is automatically updated in the database.

### 2.5 Database Management
- [DB-001] The system uses a local SQLite database.
- [DB-002] The database schema includes:
  - Requirements Table
  - Design Table
  - Implementation Table
  - Trace Table (relationships among requirement–design–implementation)
- [DB-003] The system supports both auto-save and manual save.
- [DB-004] Database export and backup functions are provided (`.db` or `.json`).

### 2.6 User Interface (GUI)
- [UI-001] The main window contains tabs for Requirements, Design, and Implementation.
- [UI-002] Each tab displays items in a table view with a detail panel for editing.
- [UI-003] The Traceability view shows linked items as a visual graph.
- [UI-004] The interface supports searching and filtering (by ID, title, or status).
- [UI-005] Optional dark mode support.

### 2.7 File I/O and Versioning
- [IO-001] Data can be exported in CSV, JSON, or Markdown format.
- [IO-002] The system supports importing data from external files.
- [IO-003] The user can save and load data as a project (folder-based structure).
- [IO-004] The user can tag versions and restore historical data snapshots.

---

## 3. Non-Functional Requirements

- [NFR-001] The application must run on Python 3.10 or later.
- [NFR-002] The GUI should remain responsive even with 1,000+ items.
- [NFR-003] The SQLite database file must be directly accessible outside the tool.
- [NFR-004] All data must remain local; no network transmission is allowed.
- [NFR-005] The software architecture should follow MVC or MVVM for maintainability.

---

## 4. Future Enhancements

- [FUT-001] Integration with Git repositories for automatic code trace mapping.
- [FUT-002] Multi-user collaboration with change tracking.
- [FUT-003] Web-based version using Flask or FastAPI with React frontend.
- [FUT-004] AI-assisted trace suggestion between requirements and design.
- [FUT-005] Test case management module (Trace linkage between Test ↔ Requirement).

---

## 5. Example Database Schema

| Table | Main Columns |
|--------|---------------|
| requirements | id, title, description, priority, status, category |
| design | id, title, description, related_req_ids |
| implementation | id, file_path, function_name, related_design_ids |
| trace | req_id, des_id, imp_id |

---

## 6. Example Project Structure
