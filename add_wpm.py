import sqlite3

conn = sqlite3.connect("users.db")
cursor = conn.cursor()

cursor.execute(
    "ALTER TABLE users ADD COLUMN best_wpm REAL DEFAULT 0"
)

conn.commit()
conn.close()

print("best_wpm added")