import sqlite3
from typing import List, Optional, Dict, Any
from datetime import datetime
from models.requirement import Requirement
from models.enums import RequirementStatus, Priority
from exceptions import DatabaseError, EntityNotFoundError
from repositories.repository_interface import IRepository


class SQLiteRequirementRepository(IRepository[Requirement]):
    """SQLite implementation of requirement repository"""

    def __init__(self, db_path: str):
        """
        Initialize repository

        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self._init_database()

    def _init_database(self):
        """Initialize database schema"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # Create requirements table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS requirements (
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
                        FOREIGN KEY (parent_id) REFERENCES requirements(id)
                            ON DELETE SET NULL
                    )
                ''')

                # Create requirement-design link table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS requirement_designs (
                        requirement_id VARCHAR(20) NOT NULL,
                        design_id INTEGER NOT NULL,
                        PRIMARY KEY (requirement_id, design_id),
                        FOREIGN KEY (requirement_id) REFERENCES requirements(id) ON DELETE CASCADE,
                        FOREIGN KEY (design_id) REFERENCES designs(id) ON DELETE CASCADE
                    )
                ''')

                # Create indexes
                cursor.execute('''
                    CREATE INDEX IF NOT EXISTS idx_req_status
                    ON requirements(status)
                ''')
                cursor.execute('''
                    CREATE INDEX IF NOT EXISTS idx_req_parent
                    ON requirements(parent_id)
                ''')

                conn.commit()
        except sqlite3.Error as e:
            raise DatabaseError(f"Failed to initialize database: {str(e)}")

    def _get_connection(self) -> sqlite3.Connection:
        """Get database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def create(self, entity: Requirement) -> str:
        """Create new requirement"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO requirements
                    (id, title, description, status, priority, category,
                     parent_id, verification_criteria, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    entity.id,
                    entity.title,
                    entity.description,
                    entity.status.value,
                    entity.priority.value,
                    entity.category,
                    entity.parent_id,
                    entity.verification_criteria,
                    entity.created_at.isoformat(),
                    entity.updated_at.isoformat()
                ))
                
                # Insert design links
                if entity.design_ids:
                    cursor.executemany('''
                        INSERT INTO requirement_designs (requirement_id, design_id)
                        VALUES (?, ?)
                    ''', [(entity.id, design_id) for design_id in entity.design_ids])
                
                conn.commit()
                return entity.id
        except sqlite3.IntegrityError as e:
            raise DatabaseError(f"Requirement with ID {entity.id} already exists")
        except sqlite3.Error as e:
            raise DatabaseError(f"Failed to create requirement: {str(e)}")

    def read(self, entity_id: str) -> Optional[Requirement]:
        """Read requirement by ID"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    'SELECT * FROM requirements WHERE id = ?',
                    (entity_id,)
                )
                row = cursor.fetchone()

                if row is None:
                    return None

                # Get linked design IDs
                cursor.execute(
                    'SELECT design_id FROM requirement_designs WHERE requirement_id = ?',
                    (entity_id,)
                )
                design_rows = cursor.fetchall()
                design_ids = [r['design_id'] for r in design_rows]

                return self._row_to_requirement(row, design_ids)
        except sqlite3.Error as e:
            raise DatabaseError(f"Failed to read requirement: {str(e)}")

    def update(self, entity: Requirement) -> bool:
        """Update existing requirement"""
        try:
            entity.updated_at = datetime.now()
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE requirements
                    SET title = ?, description = ?, status = ?, priority = ?,
                        category = ?, parent_id = ?, verification_criteria = ?,
                        updated_at = ?
                    WHERE id = ?
                ''', (
                    entity.title,
                    entity.description,
                    entity.status.value,
                    entity.priority.value,
                    entity.category,
                    entity.parent_id,
                    entity.verification_criteria,
                    entity.updated_at.isoformat(),
                    entity.id
                ))
                
                # Update design links
                cursor.execute('DELETE FROM requirement_designs WHERE requirement_id = ?', (entity.id,))
                if entity.design_ids:
                    cursor.executemany('''
                        INSERT INTO requirement_designs (requirement_id, design_id)
                        VALUES (?, ?)
                    ''', [(entity.id, design_id) for design_id in entity.design_ids])
                
                conn.commit()
                return cursor.rowcount > 0
        except sqlite3.Error as e:
            raise DatabaseError(f"Failed to update requirement: {str(e)}")

    def delete(self, entity_id: str) -> bool:
        """Delete requirement by ID"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM requirements WHERE id = ?', (entity_id,))
                conn.commit()
                return cursor.rowcount > 0
        except sqlite3.Error as e:
            raise DatabaseError(f"Failed to delete requirement: {str(e)}")

    def find_all(self) -> List[Requirement]:
        """Get all requirements"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM requirements ORDER BY id')
                rows = cursor.fetchall()
                
                requirements = []
                for row in rows:
                    # Get linked design IDs for each requirement
                    cursor.execute(
                        'SELECT design_id FROM requirement_designs WHERE requirement_id = ?',
                        (row['id'],)
                    )
                    design_rows = cursor.fetchall()
                    design_ids = [r['design_id'] for r in design_rows]
                    requirements.append(self._row_to_requirement(row, design_ids))
                
                return requirements
        except sqlite3.Error as e:
            raise DatabaseError(f"Failed to fetch requirements: {str(e)}")

    def find_by_criteria(self, criteria: Dict[str, Any]) -> List[Requirement]:
        """Find requirements matching criteria"""
        try:
            conditions = []
            params = []

            for key, value in criteria.items():
                if key in ['status', 'priority', 'category', 'parent_id']:
                    conditions.append(f"{key} = ?")
                    params.append(value)

            query = 'SELECT * FROM requirements'
            if conditions:
                query += ' WHERE ' + ' AND '.join(conditions)
            query += ' ORDER BY id'

            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, params)
                rows = cursor.fetchall()
                
                requirements = []
                for row in rows:
                    # Get linked design IDs for each requirement
                    cursor.execute(
                        'SELECT design_id FROM requirement_designs WHERE requirement_id = ?',
                        (row['id'],)
                    )
                    design_rows = cursor.fetchall()
                    design_ids = [r['design_id'] for r in design_rows]
                    requirements.append(self._row_to_requirement(row, design_ids))
                
                return requirements
        except sqlite3.Error as e:
            raise DatabaseError(f"Failed to search requirements: {str(e)}")

    def _row_to_requirement(self, row: sqlite3.Row, design_ids: list = None) -> Requirement:
        """Convert database row to Requirement object"""
        return Requirement(
            id=row['id'],
            title=row['title'],
            description=row['description'] or '',
            status=RequirementStatus(row['status']),
            priority=Priority(row['priority']),
            category=row['category'] or '',
            parent_id=row['parent_id'],
            verification_criteria=row['verification_criteria'] or '',
            design_ids=design_ids or [],
            created_at=datetime.fromisoformat(row['created_at']),
            updated_at=datetime.fromisoformat(row['updated_at'])
        )

    def get_next_id(self) -> str:
        """Generate next requirement ID"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT id FROM requirements
                    WHERE id LIKE 'REQ-%'
                    ORDER BY id DESC
                    LIMIT 1
                ''')
                row = cursor.fetchone()

                if row is None:
                    return "REQ-001"

                last_id = row['id']
                number = int(last_id.split('-')[1]) + 1
                return f"REQ-{number:03d}"
        except sqlite3.Error as e:
            raise DatabaseError(f"Failed to generate ID: {str(e)}")
