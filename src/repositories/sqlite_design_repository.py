import sqlite3
from datetime import datetime
from typing import List, Optional
from models.design import Design


class SQLiteDesignRepository:
    """SQLite implementation of design repository"""

    def __init__(self, db_path: str):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """Initialize database tables"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS designs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    description TEXT NOT NULL,
                    type TEXT NOT NULL,
                    status TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS design_requirements (
                    design_id INTEGER NOT NULL,
                    requirement_id INTEGER NOT NULL,
                    PRIMARY KEY (design_id, requirement_id),
                    FOREIGN KEY (design_id) REFERENCES designs(id) ON DELETE CASCADE,
                    FOREIGN KEY (requirement_id) REFERENCES requirements(id) ON DELETE CASCADE
                )
            """)
            conn.commit()

    def create(self, design: Design) -> Design:
        """Create a new design"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                INSERT INTO designs (name, description, type, status, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (design.name, design.description, design.type, design.status,
                  design.created_at.isoformat(), design.updated_at.isoformat()))
            design.id = cursor.lastrowid

            # Insert requirement links
            if design.requirement_ids:
                conn.executemany("""
                    INSERT INTO design_requirements (design_id, requirement_id)
                    VALUES (?, ?)
                """, [(design.id, req_id) for req_id in design.requirement_ids])

            conn.commit()
        return design

    def get(self, design_id: int) -> Optional[Design]:
        """Get a design by ID"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            row = conn.execute("""
                SELECT * FROM designs WHERE id = ?
            """, (design_id,)).fetchone()

            if not row:
                return None

            # Get linked requirements
            req_rows = conn.execute("""
                SELECT requirement_id FROM design_requirements WHERE design_id = ?
            """, (design_id,)).fetchall()
            requirement_ids = [r['requirement_id'] for r in req_rows]

            return Design(
                id=row['id'],
                name=row['name'],
                description=row['description'],
                type=row['type'],
                status=row['status'],
                created_at=datetime.fromisoformat(row['created_at']),
                updated_at=datetime.fromisoformat(row['updated_at']),
                requirement_ids=requirement_ids
            )

    def get_all(self) -> List[Design]:
        """Get all designs"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute("SELECT * FROM designs ORDER BY id").fetchall()
            designs = []
            for row in rows:
                req_rows = conn.execute("""
                    SELECT requirement_id FROM design_requirements WHERE design_id = ?
                """, (row['id'],)).fetchall()
                requirement_ids = [r['requirement_id'] for r in req_rows]

                designs.append(Design(
                    id=row['id'],
                    name=row['name'],
                    description=row['description'],
                    type=row['type'],
                    status=row['status'],
                    created_at=datetime.fromisoformat(row['created_at']),
                    updated_at=datetime.fromisoformat(row['updated_at']),
                    requirement_ids=requirement_ids
                ))
            return designs

    def update(self, design: Design) -> Design:
        """Update an existing design"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                UPDATE designs SET name = ?, description = ?, type = ?, status = ?, updated_at = ?
                WHERE id = ?
            """, (design.name, design.description, design.type, design.status,
                  design.updated_at.isoformat(), design.id))

            # Update requirement links
            conn.execute("DELETE FROM design_requirements WHERE design_id = ?", (design.id,))
            if design.requirement_ids:
                conn.executemany("""
                    INSERT INTO design_requirements (design_id, requirement_id)
                    VALUES (?, ?)
                """, [(design.id, req_id) for req_id in design.requirement_ids])

            conn.commit()
        return design

    def delete(self, design_id: int) -> bool:
        """Delete a design"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM designs WHERE id = ?", (design_id,))
            conn.commit()
        return True
