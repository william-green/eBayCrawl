import sqlite3
from pathlib import Path
#from util.get_abs_path import get_abs_path

#path = get_abs_path()

script_dir = Path(__file__).resolve().parent
db_path = script_dir / "app_data.db"
db_sql_path = script_dir / "init_db.sql"

conn = sqlite3.connect(db_path)
cur = conn.cursor()

with open(db_sql_path, "r") as sql_file:
    sql_script = sql_file.read()
    cur.executescript(sql_script)

conn.commit()
conn.close()