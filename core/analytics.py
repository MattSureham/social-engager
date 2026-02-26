"""
Analytics Module
Track and analyze engagement results
"""

import sqlite3
import json
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict

from adapters.base import Platform, EngagementResult


@dataclass
class EngagementRecord:
    """Record of an engagement action"""
    id: int = 0
    platform: str = ""
    action: str = ""  # comment, like, follow
    post_id: str = ""
    post_author: str = ""
    comment: str = ""
    success: bool = False
    error: str = ""
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


class Analytics:
    """Track and analyze engagement results"""
    
    def __init__(self, db_path: str = "engagement.db"):
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        """Initialize database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS engagements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                platform TEXT NOT NULL,
                action TEXT NOT NULL,
                post_id TEXT NOT NULL,
                post_author TEXT,
                comment TEXT,
                success INTEGER NOT NULL,
                error TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS daily_stats (
                date TEXT PRIMARY KEY,
                comments_posted INTEGER DEFAULT 0,
                likes_posted INTEGER DEFAULT 0,
                follows_posted INTEGER DEFAULT 0,
                success_count INTEGER DEFAULT 0,
                failure_count INTEGER DEFAULT 0
            )
        """)
        
        conn.commit()
        conn.close()
    
    def record(self, result: EngagementResult, post_author: str = "", comment: str = ""):
        """Record an engagement result"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Insert engagement record
        cursor.execute("""
            INSERT INTO engagements (platform, action, post_id, post_author, comment, success, error)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            result.platform.value,
            result.action,
            result.post_id,
            post_author,
            comment,
            1 if result.success else 0,
            result.error or ""
        ))
        
        # Update daily stats
        date = datetime.now().strftime("%Y-%m-%d")
        
        action_col = f"{result.action}s_posted"
        if action_col in ["comments_posted", "likes_posted", "follows_posted"]:
            cursor.execute(f"""
                INSERT INTO daily_stats (date, {action_col}, success_count, failure_count)
                VALUES (?, 1, ?, ?)
                ON CONFLICT(date) DO UPDATE SET
                    {action_col} = {action_col} + 1,
                    success_count = success_count + ?,
                    failure_count = failure_count + ?
            """, (date, 
                  1 if result.success else 0, 
                  0 if result.success else 1,
                  1 if result.success else 0,
                  0 if result.success else 1))
        
        conn.commit()
        conn.close()
    
    def get_daily_stats(self, days: int = 7) -> List[Dict]:
        """Get stats for last N days"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM daily_stats
            ORDER BY date DESC
            LIMIT ?
        """, (days,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [
            {
                "date": row[0],
                "comments": row[1],
                "likes": row[2],
                "follows": row[3],
                "success": row[4],
                "failure": row[5]
            }
            for row in rows
        ]
    
    def get_total_stats(self) -> Dict:
        """Get overall stats"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Total engagements
        cursor.execute("""
            SELECT action, COUNT(*) as count, SUM(success) as success
            FROM engagements
            GROUP BY action
        """)
        action_stats = cursor.fetchall()
        
        # Today's engagements
        cursor.execute("""
            SELECT COUNT(*) FROM engagements
            WHERE date(timestamp) = date('now')
        """)
        today_count = cursor.fetchone()[0]
        
        # This week
        cursor.execute("""
            SELECT COUNT(*) FROM engagements
            WHERE timestamp > datetime('now', '-7 days')
        """)
        week_count = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            "today": today_count,
            "this_week": week_count,
            "by_action": {
                row[0]: {"total": row[1], "success": row[2]}
                for row in action_stats
            }
        }
    
    def get_recent_engagements(self, limit: int = 20) -> List[EngagementRecord]:
        """Get recent engagement records"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM engagements
            ORDER BY timestamp DESC
            LIMIT ?
        """, (limit,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [
            EngagementRecord(
                id=row[0],
                platform=row[1],
                action=row[2],
                post_id=row[3],
                post_author=row[4],
                comment=row[5],
                success=bool(row[6]),
                error=row[7],
                timestamp=datetime.fromisoformat(row[8])
            )
            for row in rows
        ]
    
    def is_engaged(self, post_id: str) -> bool:
        """Check if already engaged with a post"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT COUNT(*) FROM engagements
            WHERE post_id = ? AND action = 'comment'
        """, (post_id,))
        
        count = cursor.fetchone()[0]
        conn.close()
        
        return count > 0
    
    def get_engagement_rate(self, days: int = 30) -> float:
        """Calculate engagement success rate"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT SUM(success), COUNT(*) FROM engagements
            WHERE timestamp > datetime('now', '-{} days')
        """.format(days))
        
        result = cursor.fetchone()
        conn.close()
        
        if result[1] == 0:
            return 0.0
        
        return (result[0] / result[1]) * 100
