import sqlite3
import json
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

DB_PATH = 'newsletter.db'

# Ensure the research table exists
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS research (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            topic TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            key_points TEXT,
            summaries TEXT,
            sources TEXT,
            raw_data TEXT
        )
    ''')
    conn.commit()
    conn.close()

# Save research data for a topic
def save_research(topic: str, key_points: Any, summaries: Any, sources: Any, raw_data: Any):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        INSERT INTO research (topic, timestamp, key_points, summaries, sources, raw_data)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (
        topic,
        datetime.utcnow().isoformat(),
        json.dumps(key_points),
        json.dumps(summaries),
        json.dumps(sources),
        json.dumps(raw_data)
    ))
    conn.commit()
    conn.close()

# Fetch the latest research for a topic
def fetch_research(topic: str, max_age_days: int = 7) -> Optional[Dict[str, Any]]:
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        SELECT timestamp, key_points, summaries, sources, raw_data FROM research
        WHERE topic = ?
        ORDER BY timestamp DESC
        LIMIT 1
    ''', (topic,))
    row = c.fetchone()
    conn.close()
    if row:
        ts, key_points, summaries, sources, raw_data = row
        # Check age
        dt = datetime.fromisoformat(ts)
        if datetime.utcnow() - dt > timedelta(days=max_age_days):
            return None
        return {
            'timestamp': ts,
            'key_points': json.loads(key_points),
            'summaries': json.loads(summaries),
            'sources': json.loads(sources),
            'raw_data': json.loads(raw_data)
        }
    return None

# List all researched topics
def list_topics():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT DISTINCT topic FROM research ORDER BY timestamp DESC')
    topics = [row[0] for row in c.fetchall()]
    conn.close()
    return topics

# Initialize DB on import
init_db() 