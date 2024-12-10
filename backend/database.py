import sqlite3

def init_db():
    """
    Creează baza de date pentru istoricul conversației, dacă nu există deja.
    """
    conn = sqlite3.connect("chat_history.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_message TEXT,
            ai_response TEXT
        )
    """)
    conn.commit()
    conn.close()

def save_to_db(user_message, ai_response):
    """
    Salvează un mesaj și răspunsul asociat în baza de date.
    """
    conn = sqlite3.connect("chat_history.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO history (user_message, ai_response) VALUES (?, ?)", (user_message, ai_response))
    conn.commit()
    conn.close()

def get_history():
    """
    Obține istoricul complet al conversațiilor din baza de date.
    """
    conn = sqlite3.connect("chat_history.db")
    cursor = conn.cursor()
    cursor.execute("SELECT user_message, ai_response FROM history")
    rows = cursor.fetchall()
    conn.close()
    return [{"user": row[0], "ai": row[1]} for row in rows]


def clear_database():
    """
    Șterge toate înregistrările din tabelul 'history'.
    """
    conn = sqlite3.connect("chat_history.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM history")
    conn.commit()
    conn.close()

