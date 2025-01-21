import sqlite3

cache_folder = "../llm_data/caches/apicalls/"
cache_db = cache_folder+"cache.db"
# Create SQLite database connection (or connect to an existing one)
conn = sqlite3.connect(cache_db)
cur = conn.cursor()

# Ensure the table exists (you can skip this if you've already created the table)
cur.execute('''
CREATE TABLE IF NOT EXISTS records (
    hash TEXT PRIMARY KEY,
    section TEXT,
    prompt TEXT,
    content TEXT
);
''')

cur.execute('CREATE INDEX IF NOT EXISTS idx_section ON records (section)')
conn.commit()

#loop through all json files in cache_folder  and insert them into the database
import json
import os
for filename in os.listdir(cache_folder):
    if filename.endswith(".json"):
        with open(cache_folder+filename) as f:
            data = json.load(f)
            #get hash from filename
            hash = filename.split(".")[0]
            print(hash)

            cur.execute('''
            INSERT OR IGNORE INTO records (hash, section, prompt, content)
            VALUES (?, ?, ?, ?);
            ''', (hash, "default", "", data['content']))



