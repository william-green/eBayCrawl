import sqlite3

conn = sqlite3.connect("app_data.db")
cur = conn.cursor()

with open("init_db.sql", "r") as sql_file:
    sql_script = sql_file.read()
    cur.executescript(sql_script)

conn.commit()
conn.close()