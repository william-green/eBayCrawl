import sqlite3
from util.get_abs_path import get_abs_path

path = get_abs_path()

conn = sqlite3.connect(path+"db/app_data.db")
cur = conn.cursor()

with open("db/init_db.sql", "r") as sql_file:
    sql_script = sql_file.read()
    cur.executescript(sql_script)

conn.commit()
conn.close()