import sqlite3
import json
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "customers.db")

def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS customers (
            user_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            language_preference TEXT DEFAULT 'hinglish',
            facts TEXT DEFAULT '{}',
            last_interaction TEXT
        )
    ''')
    conn.commit()
    conn.close()

def lookup_customer(user_id: str):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT name, language_preference, facts, last_interaction FROM customers WHERE user_id = ?', (user_id,))
    row = cursor.fetchone()
    conn.close()

    if row:
        return {
            "user_id": user_id,
            "name": row[0],
            "language_preference": row[1],
            "facts": json.loads(row[2]) if row[2] else {},
            "last_interaction": row[3]
        }
    return None

def save_customer(user_id: str, name: str, language_preference: str, facts: dict):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Check if the user already exists to merge facts
    cursor.execute('SELECT facts FROM customers WHERE user_id = ?', (user_id,))
    row = cursor.fetchone()
    
    existing_facts = {}
    if row and row[0]:
        existing_facts = json.loads(row[0])
        
    # Merge new facts into existing facts
    existing_facts.update(facts)
    facts_json = json.dumps(existing_facts)
    last_interaction = datetime.now().isoformat()

    cursor.execute('''
        INSERT INTO customers (user_id, name, language_preference, facts, last_interaction)
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(user_id) DO UPDATE SET
            name=excluded.name,
            language_preference=excluded.language_preference,
            facts=excluded.facts,
            last_interaction=excluded.last_interaction
    ''', (user_id, name, language_preference, facts_json, last_interaction))
    
    conn.commit()
    conn.close()
    return {"status": "success", "user_id": user_id}

def delete_customer(user_id: str) -> bool:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM customers WHERE user_id = ?', (user_id,))
    deleted = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return deleted
