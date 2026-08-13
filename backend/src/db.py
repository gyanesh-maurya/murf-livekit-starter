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
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tickets (
            ticket_id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            customer_name TEXT NOT NULL,
            category TEXT NOT NULL,
            summary TEXT NOT NULL,
            urgency TEXT DEFAULT 'medium',
            status TEXT DEFAULT 'open',
            created_at TEXT NOT NULL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS calls (
            call_id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            customer_name TEXT DEFAULT 'Customer',
            channel TEXT DEFAULT 'browser',
            status TEXT DEFAULT 'failed',
            outcome_reason TEXT DEFAULT 'Call disconnected before inquiry completed',
            tools_used TEXT DEFAULT '[]',
            duration_seconds INTEGER DEFAULT 0,
            started_at TEXT NOT NULL,
            ended_at TEXT
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

def create_escalation_ticket(user_id: str, customer_name: str, category: str, summary: str, urgency: str = "medium"):
    import random
    ticket_num = random.randint(1000, 9999)
    ticket_id = f"TICK-{ticket_num}"
    created_at = datetime.now().isoformat()

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Check for existing open ticket for this user and category to prevent duplicates
    cursor.execute('''
        SELECT ticket_id FROM tickets 
        WHERE user_id = ? AND category = ? AND status = 'open'
    ''', (user_id, category))
    existing = cursor.fetchone()

    if existing:
        ticket_id = existing[0]
        cursor.execute('''
            UPDATE tickets 
            SET summary = ?, urgency = ?, created_at = ? 
            WHERE ticket_id = ?
        ''', (summary, urgency, created_at, ticket_id))
    else:
        cursor.execute('''
            INSERT INTO tickets (ticket_id, user_id, customer_name, category, summary, urgency, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?, 'open', ?)
        ''', (ticket_id, user_id, customer_name, category, summary, urgency, created_at))

    conn.commit()
    conn.close()

    return {
        "status": "created",
        "ticket_id": ticket_id,
        "customer_name": customer_name,
        "category": category,
        "summary": summary,
        "urgency": urgency,
        "estimated_resolution": "2 to 4 hours"
    }

def get_open_tickets():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT ticket_id, customer_name, category, summary, urgency, created_at FROM tickets WHERE status = "open"')
    rows = cursor.fetchall()
    conn.close()
    return [
        {
            "ticket_id": r[0],
            "customer_name": r[1],
            "category": r[2],
            "summary": r[3],
            "urgency": r[4],
            "created_at": r[5]
        }
        for r in rows
    ]

def record_call_start(call_id: str, user_id: str, customer_name: str = "Customer", channel: str = "browser"):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    started_at = datetime.now().isoformat()
    cursor.execute('''
        INSERT INTO calls (call_id, user_id, customer_name, channel, status, outcome_reason, tools_used, duration_seconds, started_at)
        VALUES (?, ?, ?, ?, 'failed', 'In progress / disconnected early', '[]', 0, ?)
        ON CONFLICT(call_id) DO UPDATE SET
            user_id=excluded.user_id,
            customer_name=excluded.customer_name,
            channel=excluded.channel
    ''', (call_id, user_id, customer_name, channel, started_at))
    conn.commit()
    conn.close()
    return call_id

def record_call_end(call_id: str, status: str, outcome_reason: str, tools_used: list, duration_seconds: int):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    ended_at = datetime.now().isoformat()
    tools_json = json.dumps(tools_used or [])
    cursor.execute('''
        UPDATE calls
        SET status = ?, outcome_reason = ?, tools_used = ?, duration_seconds = ?, ended_at = ?
        WHERE call_id = ?
    ''', (status, outcome_reason, tools_json, duration_seconds, ended_at, call_id))
    conn.commit()
    conn.close()

def get_analytics_summary():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('SELECT COUNT(*) FROM calls')
    total_calls = cursor.fetchone()[0]

    cursor.execute('SELECT COUNT(*) FROM calls WHERE status = "successful"')
    successful_calls = cursor.fetchone()[0]

    cursor.execute('SELECT COUNT(*) FROM calls WHERE status = "failed"')
    failed_calls = cursor.fetchone()[0]

    success_rate = round((successful_calls / total_calls * 100), 1) if total_calls > 0 else 0.0

    cursor.execute('''
        SELECT call_id, user_id, customer_name, channel, status, outcome_reason, tools_used, duration_seconds, started_at
        FROM calls
        ORDER BY started_at DESC
        LIMIT 20
    ''')
    rows = cursor.fetchall()
    conn.close()

    recent_calls = []
    for r in rows:
        recent_calls.append({
            "call_id": r[0],
            "user_id": r[1],
            "customer_name": r[2],
            "channel": r[3],
            "status": r[4],
            "outcome_reason": r[5],
            "tools_used": json.loads(r[6]) if r[6] else [],
            "duration_seconds": r[7],
            "started_at": r[8]
        })

    return {
        "total_calls": total_calls,
        "successful_calls": successful_calls,
        "failed_calls": failed_calls,
        "success_rate": success_rate,
        "recent_calls": recent_calls
    }


