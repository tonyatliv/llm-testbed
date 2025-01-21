from sentence_transformers import SentenceTransformer
from sentence_transformers import util
import json
import sys
import os

print("py started")
#model = SentenceTransformer('BAAI/bge-m3')
model = SentenceTransformer('BAAI/bge-large-en-v1.5')
#model = SentenceTransformer('sentence-transformers/all-mpnet-base-v2')


filename = 'go_terms.json'

block = int(sys.argv[1])
blocks = int(sys.argv[2])


print("script start",block)

def get_embedding(string,namespace):
    prompt = string
    if (namespace == "molecular_function"):
        prompt = "In the context of Molecular-level activities performed by gene products. Molecular function terms describe activities that occur at the molecular level, such as 'catalysis' or 'transport'. GO molecular function terms represent activities rather than the entities (molecules or complexes) that perform the actions, and do not specify where, when, or in what context the action takes place. Molecular functions generally correspond to activities that can be performed by individual gene products (i.e. a protein or RNA), but some activities are performed by molecular complexes composed of multiple gene products. Examples of broad functional terms are catalytic activity and transporter activity; examples of narrower functional terms are adenylate cyclase activity or Toll-like receptor binding. To avoid confusion between gene product names and their molecular functions, GO molecular functions are often appended with the word 'activity' (a protein kinase would have the GO molecular function protein kinase activity).  This is the definition of a specific molecular function of an identified gene product: "+string
        
        prompt = "This is the name or definition of a specific Biological Process, Molecular Function, or Cellular Component of an identified gene product:  "+string
    if (namespace == "cellular_component"):
        prompt = "A location, relative to cellular compartments and structures, occupied by a macromolecular machine. There are two ways in which the gene ontology describes locations of gene products: (1) the cellular anatomical entities, in which a gene product carries out a molecular function. Cellular anatomical entities includes cellular structures such as the plasma membrane and the cytoskeleton, as well as membrane-enclosed cellular compartments such as the mitochondrion, and (2) the stable macromolecular complexes of which they are parts, e.g., the clathrin complex.: This is the definition of a specific Cellular Component of an identified gene product: "+string
        
        prompt = "This is the name or definition of a specific Biological Process, Molecular Function, or Cellular Component of an identified gene product:  "+string
        
    
    if (namespace == "biological_process"):
        prompt = "In the context of The larger processes, or ‘biological programs’ accomplished by multiple molecular activities. Examples of broad biological process terms are DNA repair or signal transduction. Examples of more specific terms are pyrimidine nucleobase biosynthetic process or glucose transmembrane transport.  This is the definition of a specific Biological Process of an identified gene product: "+string
        
        prompt = "This is the name or definition of a specific Biological Process, Molecular Function, or Cellular Component of an identified gene product:  "+string      
    #ignore the above
 
    embedding = model.encode(prompt).tolist()
    return embedding

with open(filename, 'r') as file:
    data = json.load(file)
count = 0
new_data = {}
for x in data:
    
    count = count + 1
    if not(count % blocks == block):
        continue
    go = data[x]
    print(x)
    
    new_go = go.copy()
    try:
    
                
        new_go["name_embed"] =  [get_embedding(go["name"],go["namespace"]),]
        
        new_go["definition_embed"] = [get_embedding(go["definition"],go["namespace"]),]
        
        sentences = go["definition"].split(".")
        if False:
            if len(sentences) > 1:
                for s in sentences:
                    if len(s) > 15:
                        sentence_embed = get_embedding(s,go["namespace"]),
                        new_go["definition_embed"].append(sentence_embed)
     
        syn_embed = []
        synonyms = go["synonyms"]
        if synonyms:
            for s in synonyms:
                embedding = get_embedding(s,go["namespace"])
               
                syn_embed.append(embedding)

        new_go["synonyms_embed"] = syn_embed
        new_data[x] = new_go
        
    except Exception as e:
        print(f"Exception message: {e}")
        print(x,"failed")
     #model.encode   
with open(str(block)+"go_terms_embeddings.json", "w") as f:
    json.dump(new_data, f, indent=4)
    
#delete the cached pickle file    
filename = 'go_embeddings.json'
pf = filename + ".pickle"
if os.path.exists(pf):
    os.remove(pf)