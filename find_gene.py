import sqlite3
import sys
import json
import binascii
import shlex
import os

def get_base_path():
    if getattr(sys, 'frozen', False):  # Check if the app is "frozen" (bundled)
        return os.path.dirname(sys.executable)
    else:
        return os.path.dirname(os.path.abspath(__file__))

DB_FILE = get_base_path()+'/../find_gene/'+'gene_lookup.db'

def connect_db():
    conn = sqlite3.connect(DB_FILE)
    return conn

conn = sqlite3.connect(DB_FILE)

species_cache = None
def get_all_species():
    global species_cache
    if species_cache is not None:
        return species_cache
        
    cursor = conn.cursor()

    cursor.execute("SELECT DISTINCT species FROM records")
    rows = cursor.fetchall()

    # Extract species from the rows
    species_cache = [row[0] for row in rows]
    return species_cache


            
def get_gene_match(term,column = None, case_sensitive = False):
#This should match what the db was built with
    use_columns = ["Gene ID", "source_id", "Product Description", "Gene Name or Symbol",
               "Transcript Product Description", "gene_source_id", "Entrez Gene ID", "","","GAF Synonym"]

# Create SQLite database connection (or connect to an existing one)
#    conn = connect_db()
    cursor = conn.cursor()


    search_content = term

    column_part = ""
    if column is not None:
        if isinstance(column, str):
            column = use_columns.index(column)+1
        column_part = "AND column = ?" if column is not None else ""

    case_part = "COLLATE NOCASE" if not case_sensitive else ""
    query = f"""
        SELECT content,column,species FROM records WHERE id IN (
            SELECT id FROM records WHERE  content {case_part} = ? {column_part}
        )
        """

    if column is not None:
        cursor.execute(query, ( search_content, column))
    else:
        cursor.execute(query, (search_content,))

    # Fetch all matching rows
    rows = cursor.fetchall()


    output = []
    # Print results
    for row in rows:
        #        print(row[1])
        output.append((row[0], use_columns[row[1] - 1], row[1],row[2]))
    #    conn.close()
    output = set(output)
    
 
    outputlist = []
    for o in output:
        l = list(o)
        outputlist.append(l)
    outputlist.sort(key=lambda x: x[2])
    
    
  #returns a list of lists
  #in the format - name, column name, colum num, species
  
    
    return outputlist

  
def b64decode(data):
    missing_padding = len(data) % 4
    if missing_padding:
        data += '=' * (4 - missing_padding)  # Fix padding if needed
    return binascii.a2b_base64(data)
  
def decode_arguments():
    if '-b' in sys.argv:
        idx = sys.argv.index('-b')
        if idx + 1 < len(sys.argv):
            encoded_string = sys.argv[idx + 1]
            
            decoded_string =b64decode(encoded_string).decode('utf-8')
            decoded_args = shlex.split(decoded_string)
            sys.argv = [sys.argv[0]] + decoded_args  # Keep the script name as the first element

def main():
    decode_arguments()
    gene = sys.argv[1]

    print(json.dumps(get_gene_match(gene)))

if __name__ == "__main__":
    main()
