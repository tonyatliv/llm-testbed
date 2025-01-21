import warnings
import json
import time
import pickle
import os
import numpy as np
try:
	import cupy as cp
except:
	import numpy as cp

prompt = "Take the list from the following summary and convert it to json format, with no other commentary.  Remove any descriptions that relate to the gene."

data_root ="../llm_data/"
mf = data_root+"model.pickle"
embed_model = data_root+"model.pre" #'BAAI/bge-large-en-v1.5'
filename = data_root+'go_embeddings.json'
pf = filename + ".pickle"
go_data = {}
model = None
#Number of best matches to show
SHOW_RESULTS = 5
storage = None
def getModel():
    global model
    
    #Pickling a model is not ideal, but it will make things quicker to run
    #Delete the pickle file if the model changes
    if os.path.exists(mf): 
        with open(mf, 'rb') as file:
            warnings.filterwarnings("ignore", category=FutureWarning)
            model = pickle.load(file)
    else:        
        from sentence_transformers import SentenceTransformer

        model = SentenceTransformer(embed_model, trust_remote_code=True)

    #    with open(mf, 'wb') as file:
    #        pickle.dump(model, file)
            
def load():
    with open(filename, 'r') as file:
        load_data = json.load(file)
 
    for x in load_data:
        go = load_data[x]
        new_term = {}
        
        new_term["name"] = go["name"]
        new_term["definition"] = go["definition"]
        new_term["synonyms"] = go["synonyms"]
        
        name_embed = []
        for s in go["name_embed"]:
            name_embed.append(np.array(s, dtype=np.float32))
        new_term["name_embed"] = name_embed
        
        definition_embed = []
        for s in go["definition_embed"]:
            definition_embed.append(np.array(s, dtype=np.float32))
        new_term["definition_embed"] = definition_embed
        
        
 
        syn_embed = []
        for s in go["synonyms_embed"]:
            syn_embed.append(np.array(s, dtype=np.float32))
        new_term["synonyms_embed"] = syn_embed
        
        
        go_data[x] = new_term
    with open(pf, 'wb') as file:
        pickle.dump(go_data , file)

def compute_similarity(d, embed):
    """Compute the cosine similarity between two vectors."""
    a = embed
    b = d
    score = np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
    return score

class VectorStorage:
    def __init__(self, vector_size):
        # Initialize an empty array with shape (0, vector_size)
        self.vectors = cp.empty((0, vector_size))
    
    def setids(self, vector):
        # Add a new vector by stacking it to the existing array
        self.idlist = vector
        
    def getids(self):
        # Add a new vector by stacking it to the existing array
        return self.idlist
        
    def add_vector(self, vector):
        # Add a new vector by stacking it to the existing array
        self.vectors = np.vstack([self.vectors, vector])
    def make_vector(self, vector):
        # Add a new vector by stacking it to the existing array
        self.vectors = cp.array( vector)
        
    def find_best_match(self, target_vector):
    
        target_vector = cp.array(target_vector)
        # Normalize the vectors to avoid computing magnitude multiple times
        vectors_normalized = self.vectors / cp.linalg.norm(self.vectors, axis=1, keepdims=True)
        target_vector_normalized = target_vector / cp.linalg.norm(target_vector)
        
        # Compute cosine similarity by matrix multiplication
        cosine_similarities = cp.dot(vectors_normalized, target_vector_normalized)

        # Find the index of the best match
        cosine_similarities = cosine_similarities.flatten()
     
     #in case the same id is repeated (should not really matter)
        top_n_indices = np.argsort(-cosine_similarities)[:SHOW_RESULTS*3]  
        
        top_n_indices = top_n_indices.tolist()
        top_n_scores = cosine_similarities[top_n_indices]
                
        top_n_scores = top_n_scores.tolist()

        combined_array = (list(zip(top_n_indices, top_n_scores)))
        
        
        return  combined_array
        
        
def find(string):
    

    best = {}
    best_score = -1
    embed = model.encode(string)
    
    results = storage.find_best_match(embed)
    
    new_results = []
    foundid = {}
    id_list = storage.getids()
    #put them into a data structure -remember that there may be id duplicates
    for r in results:
    
        goid = id_list[r[0]]
        if goid in foundid:
            continue
        foundid[goid] = 1
            
        n = (goid,float(r[1]),go_data[goid]['name'], go_data[goid]['definition'])
        new_results.append(n)
        if len(new_results)  >= SHOW_RESULTS:
            break
        
    return new_results
    

def setup():
    global go_data, storage
    getModel()

    if os.path.exists(pf):
        with open(pf, 'rb') as file:
            go_data = pickle.load(file)
    else:
        load()
        
    for go_id in go_data:
        go = go_data[go_id]
        embeddings = go["definition_embed"]
        vector_size=embeddings[0].size
        break
    storage = VectorStorage(vector_size)
    print("build vector store")
    embeddings_list = []
    id_list = []
    for go_id in go_data:
        go = go_data[go_id]
        embeddings = go["definition_embed"]
        embeddings = go["definition_embed"] + go["name_embed"] + go["synonyms_embed"]
            
        for e in embeddings:
            embeddings_list.append(e)
            id_list.append(go_id)
 
    storage.make_vector(embeddings_list)
    storage.setids(id_list)
        
setup_data = {}
def search(string, sz = SHOW_RESULTS):
    global SHOW_RESULTS
    SHOW_RESULTS = sz
    prompt = "This is the name or definition of a specific Biological Process, Molecular Function, or Cellular Component of an identified gene product: " + string

    if "ok" not in setup_data:
        setup_data["ok"] = 1
        setup()

    return find(prompt)
def main():

 
    #This is from GO:0044409
    test_text = "Entry of a symbiont into the body, tissues, or cells of a host organism as part of the symbiont life cycle."

            
    while True:
        start = time.time()
        x = search(test_text)
        print(x,time.time()-start)

        test_text = input("Enter term (or press Enter to stop): ")
        
        if test_text == "":
            break
 

if __name__ == "__main__":
    main()
