import sqlite3

DB_PATH = 'db/bot.db'
db = sqlite3.connect(DB_PATH)
cursor = db.cursor()