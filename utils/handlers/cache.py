import sys
import sqlite3
import tarfile
import zlib
import json
import hashlib
from utils.handlers import ConfigHandler

cache_records = {}
config = ConfigHandler()

cache_db = config.getCacheFolderAPI()+"/cache.db"
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

#Returns value in cache, or none if not in cache
def get_cache(keytext):


    
    conn = sqlite3.connect(cache_db)
    key = hashlib.sha256(keytext.encode()).hexdigest()
        #convert the key to a string
    key = str(key)

    
    cur = conn.cursor()   
    cur.execute('SELECT content, prompt FROM records WHERE hash=?', (key,))

    row = cur.fetchone()
    content = None
    if row is not None:
        content = row[0]
 #       print("GET CACHE",key,":\n:",row[1],":\n:",content,":\n")
    else:
        pass
   #     print(key," not cached :\n", keytext)
    conn.close()
    return content
        
#puts content in cache
def put_cache(keytext,content,prompt="", section="default"):
    conn = sqlite3.connect(cache_db)
    key = hashlib.sha256(keytext.encode()).hexdigest()
        #convert the key to a string
    key = str(key)
        
            
 #   print("PUT CACHE",key,":\n:",keytext[:200], ":\n:",content,":\n")
 
    cur = conn.cursor()
    prompt = keytext
    
    cur.execute('''
            INSERT OR REPLACE INTO records (hash, content, prompt, section)
            VALUES (?, ?, ?, ?)
        ''', [key,content,prompt, section])
    conn.commit()  # Commit the transaction
    
 
    conn.close()
    return
    