"""
Database module for storing and managing job listings.
Uses SQLite for zero-cost local storage.
"""

import sqlite3
import json
import os
from typing import List, Dict

class JobDatabase:
    def __init__(self, db_path: str = "data/jobs.db"):
        """Initialize database connection and create tables if needed."""
        # Ensure data directory exists
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.db_path = db_path
        self.init_db()
    
    def init_db(self):
        """Create tables if they don't exist."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Updated schema to match the new Scraper fields
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS jobs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                job_id TEXT UNIQUE,
                title TEXT NOT NULL,
                company TEXT,
                location TEXT,
                stipend TEXT,
                equity TEXT,
                description TEXT,          -- Stores the full_description
                short_description TEXT,    -- Stores the short_description
                skills TEXT,               -- Stores combined skills as JSON
                ui_skills TEXT,            -- Stores UI tags as JSON
                apply_url TEXT NOT NULL,
                match_score INTEGER DEFAULT 0,
                notified BOOLEAN DEFAULT 0,
                cover_letter TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        conn.close()
    
    def save_jobs(self, jobs: List[Dict]) -> int:
        """
        Save jobs to database, avoiding duplicates.
        Returns count of newly inserted jobs.
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        inserted = 0
        
        for job in jobs:
            try:
                # Map scraper keys to DB columns
                cursor.execute("""
                    INSERT INTO jobs (
                        job_id, title, company, location, 
                        stipend, equity, description, short_description,
                        skills, ui_skills, apply_url, match_score
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    job.get('id'),                      # Mapped from scraper 'id' -> DB 'job_id'
                    job.get('title'),
                    job.get('company'),
                    job.get('location'),
                    job.get('stipend', "Not disclosed"),
                    job.get('equity', "None"),
                    job.get('full_description', ""),    # Mapped to description
                    job.get('short_description', ""),
                    json.dumps(job.get('skills', [])),  # List -> JSON String
                    json.dumps(job.get('ui_skills', [])), # List -> JSON String
                    job.get('apply_url'),
                    job.get('match_score', 0)
                ))
                inserted += 1
            except sqlite3.IntegrityError:
                # Job ID (hash) already exists, skip
                continue
            except Exception as e:
                print(f"Error saving job {job.get('title')}: {e}")
        
        conn.commit()
        conn.close()
        return inserted
    
    def get_unnotified_jobs(self, min_score: int = 0) -> List[Dict]:
        """Get jobs that haven't been notified yet, above minimum score."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row # Allows accessing columns by name
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM jobs
            WHERE notified = 0 AND match_score >= ?
            ORDER BY match_score DESC, created_at DESC
        """, (min_score,))
        
        rows = cursor.fetchall()
        jobs = []

        # Convert Row objects to dicts and parse JSON fields
        for row in rows:
            job_dict = dict(row)
            try:
                if job_dict.get('skills'):
                    job_dict['skills'] = json.loads(job_dict['skills'])
                if job_dict.get('ui_skills'):
                    job_dict['ui_skills'] = json.loads(job_dict['ui_skills'])
            except json.JSONDecodeError:
                job_dict['skills'] = []
                job_dict['ui_skills'] = []
            
            jobs.append(job_dict)
        
        conn.close()
        return jobs
    
    def mark_as_notified(self, job_ids: List[int]):
        """Mark jobs as notified by their internal DB ID."""
        if not job_ids:
            return
            
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        placeholders = ','.join('?' * len(job_ids))
        cursor.execute(f"""
            UPDATE jobs
            SET notified = 1
            WHERE id IN ({placeholders})
        """, job_ids)
        
        conn.commit()
        conn.close()
    
    def save_cover_letter(self, job_db_id: int, cover_letter: str):
        """Save generated cover letter for a job."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE jobs
            SET cover_letter = ?
            WHERE id = ?
        """, (cover_letter, job_db_id))
        
        conn.commit()
        conn.close()
    
    def get_stats(self) -> Dict:
        """Get database statistics."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("SELECT COUNT(*) FROM jobs")
            total = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM jobs WHERE notified = 1")
            notified = cursor.fetchone()[0]
            
            cursor.execute("SELECT AVG(match_score) FROM jobs")
            avg_result = cursor.fetchone()[0]
            avg_score = avg_result if avg_result is not None else 0
            
            return {
                'total_jobs': total,
                'notified': notified,
                'pending': total - notified,
                'avg_match_score': round(avg_score, 2)
            }
        except Exception as e:
            return {'error': str(e)}
        finally:
            conn.close()

if __name__ == "__main__":
    # Test database operations
    db = JobDatabase("data/jobs.db")
    print("Database initialized successfully!")
    print("Stats:", db.get_stats())