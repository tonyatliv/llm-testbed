import json
import os
block = 0

out_data = {}
while True:

    filename = str(block)+"go_terms_embeddings.json"
    block = block + 1
    try:
        with open(filename, 'r') as file:
            print(filename)
            data = json.load(file)
            for x in data:
                out_data[x] = data[x]
        
    except:
        break
        
with open("go_embeddings.json", "w") as f:
    json.dump(out_data, f, indent=4)        
    
block = 0

while True:
    filename = str(block)+"go_terms_embeddings.json"
    block = block + 1
    if os.path.exists(filename):
        os.remove(filename)
    else:
        break
 
    