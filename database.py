import sqlite3

DB_NAME = "compliance_audits.db"

def init_db():
    """Create the audit table if it does not already exist."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS audits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            customer_sentiment TEXT,
            promised_payment_date TEXT,
            agent_compliant INTEGER,
            summary TEXT,
            transcript TEXT
        )
    ''')
    conn.commit()
    conn.close()

def save_audit(sentiment, payment_date, compliant, summary, transcript):
    """Insert a new audit record into the database."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO audits (customer_sentiment, promised_payment_date, agent_compliant, summary, transcript)
        VALUES (?, ?, ?, ?, ?)
    ''', (sentiment, payment_date, 1 if compliant else 0, summary, transcript))
    conn.commit()
    conn.close()

def fetch_all_audits():
    """Retrieve all saved audit logs, newest first."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, timestamp, customer_sentiment, promised_payment_date, agent_compliant, summary, transcript FROM audits ORDER BY timestamp DESC")
    rows = cursor.fetchall()
    conn.close()
    return rows