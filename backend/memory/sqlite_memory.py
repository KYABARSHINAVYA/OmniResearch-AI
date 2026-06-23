import sqlite3

conn = sqlite3.connect(
    "chat_history.db",
    check_same_thread=False
)

cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS conversations(
id INTEGER PRIMARY KEY AUTOINCREMENT,
question TEXT,
answer TEXT
)
""")

conn.commit()


def save_chat(question, answer):

    cursor.execute(
        """
        INSERT INTO conversations(question,answer)
        VALUES(?,?)
        """,
        (question, answer)
    )

    conn.commit()


def load_history():

    cursor.execute(
        "SELECT id,question,answer FROM conversations ORDER BY id DESC"
    )

    return cursor.fetchall()
