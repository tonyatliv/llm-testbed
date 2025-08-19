#SYNONYMS is not finding any


from collections import Counter

import sys
import re
from utils.handlers import StatusHandler, ConfigHandler
import jsonschema
import json
from llms import LLMHandler

<<<<<<< Updated upstream
=======
def match_words(w1,w2):
    w1 = w1.lower()
    w2 = w2.lower()
    if w1 == w2:
        return True
        
    def is_abbrev(abbrev, full):
        return abbrev.endswith('.') and full.startswith(abbrev[:-1])

    if is_abbrev(w1, w2) or is_abbrev(w2, w1):
        return True
        
    return False
    
        
def get_best_species(species, species_list):
    
    swords = species.split()
    best_count = -1
    best = species
    for match in species_list:
        mwords = match.split()
        mcount = 1.5
        # matching words in the same order
        for sw, mw in zip(swords, mwords):
            if match_words(sw, mw):
                mcount += 1
             
        #prefer a shorter match (e.g., so no additional strains)
        mcount -=  len(mwords)/10
        
        if mcount > best_count:
            best_count = mcount
            best = match
    return best
        
        
        
        
    
    
>>>>>>> Stashed changes
def getPaperGenes(pmid, textSource):
    status = StatusHandler(pmid)
    config = ConfigHandler()
    
 
    if not status.areSpeciesFetched():
        print("NO SPECIES")
        return ValueError("Species have not yet been fetched for this paper")
    
#    if status.areGenesFetched():
#        print("HAVE GENES")
#        return ValueError("Genes have already been fetched for this paper")
    
    
#a default model
    model = LLMHandler(systemPrompt="")
    
    
    LIMIT_SPECIES = ["Plasmodium falciparum 3D7"]
    
    speciesData = status.getSpeciesData()
<<<<<<< Updated upstream

    if textSource == "plaintext":
        plaintextFilePath = status.getPlaintextFilePath()
        with open(plaintextFilePath) as plaintextFile:
            promptText = plaintextFile.read()
    elif textSource == "summary":
        summaryFilePath = status.getSummaryFilePath()
        with open(summaryFilePath) as summaryFile:
            promptText = summaryFile.read()
        
    systemPrompt = config.getSystemPromptForGetPaperGenes() + json.dumps(speciesData)
    
    model = LLMHandler(systemPrompt=systemPrompt)

    response = model.askWithRetry(promptText, textToComplete="{")
    start = response.find('{')
    end = response.rfind('}') + 1

    if start != -1 and end != -1:
        response = response[start:end]
=======


    species_list = []
    for s in speciesData["species"]:
        
        
        from find_gene import get_all_species
        species_db_list = get_all_species()
       
        use_species = get_best_species(s, species_db_list)
        
        print("MAP SPECIES ", s," TO ", use_species)
        
        if LIMIT_SPECIES is not None:
            if use_species not in LIMIT_SPECIES:
                print("Not evaluating", use_species)
                continue
                
        species_list.append(use_species)
        
    results = {}      

    if textSource == "plaintext":
        plaintextFilePath = status.getPlaintextFilePath()
        with open(plaintextFilePath) as plaintextFile:
            promptText = plaintextFile.read()
    elif textSource == "summary":
        summaryFilePath = status.getSummaryFilePath()
        with open(summaryFilePath) as summaryFile:
            promptText = summaryFile.read()
  
  #This gets a version that comes from JSOn with only certain sections
  #All sources are, at the moment, sourced from Pubmed JSON, so this will work
  #it will return plain text, as a fallback
#if textSource == "plaintextjson":       
    promptText = status.getJSONResults()



    #nowe we will look for genes
    gene_text = promptText
    #use re to remove brackets commas colons 
    gene_text = re.sub(r'\(|\)|,|:|;', ' ', gene_text)
    
    #use re to remove full stops only where followed by whitespace
    gene_text = re.sub(r'\.\s', ' ', gene_text)
    from find_gene import get_gene_match, get_all_species

    gene_text= gene_text # + gene_text.lower()
    words = gene_text.split()
    

# for now, assume genes are one or two words
    unigram_counts  = Counter(words)
    bigrams = [' '.join(pair) for pair in zip(words, words[1:])]
    bigram_counts = Counter(bigrams)

# Combine both counts
    search_count = unigram_counts + bigram_counts
  
    
    
    search_words = dict(search_count)

    all_gene_matches = {}
    
    
    
    add_terms = {}
    #for every word in document, I am looking to see if it is a valid gene
    # all_gene_matches[w] should be a list of synonyms for the gene
    for word in search_words:
 
        all_gene_matches[word] = get_gene_match(word)  
        if "-" in word:
            for w in word.split("-"):
                all_gene_matches[w] = get_gene_match(w)  
                add_terms[w] = add_terms.get(w,0)+1
                
        if "/" in word:
            for w in word.split("/"):
                all_gene_matches[w] = get_gene_match(w)                 
                add_terms[w] = add_terms.get(w,0)+1
        if "\\" in word:
            for w in word.split("\\"):
                all_gene_matches[w] = get_gene_match(w)                  
                add_terms[w] = add_terms.get(w,0)+1
                
        
    
    search_words = dict(search_count+ Counter(add_terms))
    
    map_to_id = {}
    
    
    for species in species_list:
        for word in all_gene_matches:
            gene_matches = all_gene_matches[word]
            
            
            found = 0
            for match in gene_matches:
                
                
                if match[3].lower().startswith(species.lower()):           
                    
                    if match[1].lower() == "gene id":
                        found = found + 1    
                        map_to_id[(species,word)] = match[0]
                        print("MAP SPEC",species,word)
            
            # store the number if it's a complex, so I know not to process it
            
            if found== 1:
                print("FOUND ID",word,map_to_id[(species,word)] )
            if found > 1:
                map_to_id[(species,word)] = f"[{found}]"
                print("gene complex",word,found)
                        
    
    for species in species_list:
        
 
        synonyms = {}
        
        found_genes = {}
        for word in all_gene_matches:
            if len(word) < 3:
                continue
                
            #going through all of the synonyms - get those with the same species
            gene_matches = all_gene_matches[word]
            
            for match in gene_matches:
                
                if match[3].lower().startswith(species.lower()):
                
                    if str(match[0]).isnumeric():
                        continue
                        
                    
                    if word not in synonyms:
                        synonyms[word] = set()
                    synonyms[word].add(match[0])
                    
                    found_genes[word] = search_words[word]
 
                    
            # Step 2: Sort genes by frequency (descending)
        sorted_genes = sorted(found_genes.items(), key=lambda x: x[1], reverse=True)
 
        print("GOT all names")
        print(sorted_genes)
        # Step 3: Process from most common to least common
        
        # Make a list of groups, with the most commonly found term first
        # Add any other synonyms to the group
        
        processed = set()

        groups = []
        for word, count in sorted_genes:
            if word.lower() in processed:
                continue  # Skip if already grouped
            
            
            processed.add(word.lower())
            
            group = {word}
            for s in synonyms[word]:
                if s in found_genes:
                    if s not in processed:
                        group.add(s)
                        processed.add(s)
                        processed.add(s.lower())
            
            group = list(sorted(group, key=lambda x: found_genes[x], reverse=True))
            newgroup = []
            found = set()
            for g in group:
      
                if g.lower() not in found:
                    newgroup.append(g)
                    found.add(g.lower())
                
            
            groups.append(newgroup)
            
            
        #Still woprking per species - now we have groups of genes found (i.e. synonyms)
       
        if len(groups) < 1:
            continue

#keep a track of what else the gene migth be called            
        gene_synonym_strings = {}
        gene_strings = []
        for g in groups:
            #g should be a set of synonyms
            group_string = " also known as ".join(g)
            
            if len(g) > 1:
                group_string = " ( "+group_string+" ) "

            gene_strings.append(group_string)            
            gene_synonym_strings[g[0]] = group_string
            
        
        gene_string =" and ".join(gene_strings)
        
        
        print("POTENTIAL genes in text: ",gene_string)

 
        
        systemPrompt = config.getSystemPromptForGetPaperGenes() + json.dumps(speciesData)
        
        systemPrompt = ""
        model = LLMHandler(systemPrompt=systemPrompt)

        llm_found_genes = []

        if False:
         for g in groups:
            gene_string = " also known as ".join(g)
            
            prompt = "I need to know if "+gene_string+" was included in a study of "+species+".  The text to examine is "+promptText+". Answer Yes if "+gene_string+" was actually discussed.  "
            response = model.askWithRetry(prompt, textToComplete="")
          #  print("R0=",response,"\n",prompt,"\n")
            prompt = "Does this text indicate a positive response? I need a single word answer with no other commentary: The text is "+response
            response = model.askWithRetry(prompt, textToComplete="")
            if response.lower().startswith("y"):
                llm_found_genes.append(g[0])
                print("add",g[0])
        else:
        
            prompt = "Examine this study <study>"+promptText+"</study>  I need to validate if any of several possible genes might be included in a study of "+species+".  Give a list of  each gene or gene product from my list that actually has related information in the study. Answer strictly as a SINGLE JSON List like [GENEID1,GENEID2].  The genes are : " +gene_string+" . Do not include results that are completely unrelated to "+species
            response = model.askWithRetry(prompt, textToComplete="[")

            print("R=",response)
            try:
                js = json.loads(response)[0]
                
            except:
                response = model.askWithRetry("Convert this strictly to a JSON list of gene names with no other commentary : "+response, textToComplete="[")
            try:
                js = json.loads(response)[0]
            except:
                response = model.askWithRetry("Convert this strictly to a JSON list of gene names with no other commentary. IT must be parsable as JSON. This is more important than being correct. : "+response, textToComplete="[")
                
            llm_found_genes = []
            try:
                llm_found_genes=json.loads(response)
            except:
                pass
                
 
        if len(llm_found_genes) > 0:
            results[species] = llm_found_genes

            

    fullAnswer = []
    for species in results:
 
  
        
        genes = []
        
        # a list of genes found - it is possible that some or synonyms, if the LLM doesn't strictly keep the wording
        for gene in results[species]:
            
            syns = []
            
            # all_gene_matches is everything found in paper that could be a geme
            
            if gene not in all_gene_matches:
                print("discard",gene)
                continue
            
            #groups should be sets of synonyms
            #one per gene that was confirmed in the paper
            
            for group in groups:
                if gene in group:
                    for s in group:
                        if s != gene:
                            syns.append(s)
 
 
#            for x in all_gene_matches[gene]:
#                syns.append(x[0])
                
                
#            print("FOUND SYNONYMS ",gene," = ", syns)
            
            #print(syns)  
            #genes.append({"identifier":gene, "name":gene})
            
            #get the vpdb canonical name
            gene_id = gene
            
            print("GETMAP SPEC",species,gene)
            
            if (species,gene) in map_to_id:
                gene_id = map_to_id[(species,gene)]

            print("GETMAP SPEC to ",gene_id,species,gene)
            genes.append({"identifier":gene, "name":gene, "synonyms":syns, "geneID":gene_id})
            
        s = {"name":species, "genes":genes}
        fullAnswer.append(s)
        
    fullAnswer = {"species":fullAnswer}
    
    # print(fullAnswer)
        

    
    
>>>>>>> Stashed changes

    try:
   
        schema = config.getResponseSchemaForGetPaperGenes()
       #todo - schema not currently updated
        #jsonschema.validate(fullAnswer, schema=schema)
    except Exception as err:
        status.updateField("getPaperGenes", {
            "success": False,
            "error": f"{err}"
        })
        raise Exception(err)
    
    status.updateField("getPaperGenes", {
        "success": True,
        "response": fullAnswer,
        "messageHistory": model.getMessageHistory()
    })
    
    return fullAnswer
    
if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python getPaperGenes.py <pmid> <isFromPlaintext>")
        sys.exit(1)

    pmid = sys.argv[1]
    textSource = sys.argv[2]

    if textSource not in ["plaintext", "summary"]:
        print("textSource must be either 'plaintext' or 'summary'")
        sys.exit(1)
    
    try:
        genes = getPaperGenes(pmid, textSource)
        print(f"Genes for species of paper with PMID {pmid} cached to status file.")
    except Exception as err:
        print(f"Error getting species from paper: {err}")