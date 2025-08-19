from utils.handlers import ConfigHandler, StatusHandler
from llms import LLMHandler
import re
import sys
import json
import jsonschema
import time
from search import search
import random
<<<<<<< Updated upstream

SCORE_THRESHOLD = 0.75
=======
from GOntoSim import GOntoSim



SCORE_THRESHOLD = 0.5
>>>>>>> Stashed changes
QUOTE_STYLE = True
TOP_TERMS = 4

EXAMPLE_QUOTES = True
EXAMPLE_QUOTES_NUM = 10

if EXAMPLE_QUOTES:
    quoteFile = 'quote_store.json'
    with open(quoteFile, 'r') as file:
        quote_data = json.load(file)
        random.seed(0)
        random.shuffle(quote_data)
    

#prompts are currently inline in the code
#some need terms replacing, and we don't have a handler for that yet
<<<<<<< Updated upstream
extractSystemPrompt_v1 = 'You are an assistant tasked with extracting the gene function and location from biological literature. only about [species] . You should ignore anything which describes a different species.  You should describe any Biological Process, Molecular Function or Cellular Component related to the Gene product that has been identified. These descriptions should be one or two full sentences, in the same detail as given in the Gene Ontology.  Some examples of entries in the Gene Ontology are  1. "Entry of a symbiont into the body, tissues, or cells of a host organism as part of the symbiont life cycle. The host is defined as the larger of the organisms involved in a symbiotic interaction."  \n 2. "The secretion of neuropeptides contained within a dense core vesicle by fusion of the granule with the presynaptic membrane, stimulated by a rise in cytosolic calcium ion concentration \n 3. A heterotetrameric protein complex that associates with replication origins, where it is required for the initiation of DNA replication, and with replication forks \n 4. Combining with the neurotransmitter dopamine and activating adenylate cyclase via coupling to Gi/Go to initiate a change in cell activity. \n 5. Any process that modulates the frequency, rate or extent of the growth of all or part of an organism so that it occurs at its proper speed, either globally or in a specific part of the organisms development.   '
extractSystemPrompt = 'You are an assistant tasked with extracting the gene function and location from biological literature.   '
extractPrompt =  "In the following article, look for any evidence of any Biological Processes, molecular functions, or cellular components that involve [species] and the gene product identified by [geneID]. Give a reasonable description of each one that has strong supporting evidence as one or two complete sentences.  Give a numbered list, one for each description found.   If there is no evidence of any specific biological process, molecular function, or cellular component, reply with an empty list [].  Add NO other commentary. The article follows: "
extractPromptQuote_v1 =  "In the following article, look for evidence of any Biological Processes, molecular functions, or cellular components that involve [species] and the gene product identified by [geneID]. Give a quote from the article of the supporting evidence as complete sentences.  Supply these as a numbered list.   If there is no evidence of any specific biological process, molecular function, or cellular component, reply with an empty list [].   Add NO other commentary.  The article follows: "

extractPromptQuote =  "In the following article, look for evidence of a gene or protein's involvement with any Biological Process, molecular function, or cellular component. For every one that you find, give a quote from the article of the supporting evidence  - as complete sentences and only quoted from the article.  Supply these as a numbered list.   If there is no evidence of any specific biological process, molecular function, or cellular component, reply with an empty list [].   Add NO other commentary.  The article follows: "

replaceGenePrompt = "In the following text, remove references to the specific gene product names or identifiers, like [geneID] .  Replace it with the generic term, 'protein', which is not specific to this gene product. ADD NO OTHER COMMENTARY. The text is: "

replaceSpeciesPrompt = "In the following text, remove references to a specific species names or identifiers, like [species] .  Replace it with the generic term, 'organism', which is not specific to this species.  ADD NO OTHER COMMENTARY. The text is: "

convertJSONPrompt = "Take the list of items that are Biological process, functions, or cellular components  from the following text and convert it to a json format single list only. It is vital that the output contains full descriptions with complete sentences and contains every piece of biological information that is contained in the input. This is the text: "        

=======
extractSystemPrompt = 'You are an assistant tasked with extracting the gene function and location from biological literature only about [species] . You should ignore anything which describes a different species.  You should describe any Biological Process, Molecular Function or Cellular Component related to the Gene product that has been identified. These descriptions should be one or two full sentences, in the same detail as given in the Gene Ontology.  Some examples of entries in the Gene Ontology are  1. "Entry of a symbiont into the body, tissues, or cells of a host organism as part of the symbiont life cycle. The host is defined as the larger of the organisms involved in a symbiotic interaction."  \n 2. "The secretion of neuropeptides contained within a dense core vesicle by fusion of the granule with the presynaptic membrane, stimulated by a rise in cytosolic calcium ion concentration \n 3. A heterotetrameric protein complex that associates with replication origins, where it is required for the initiation of DNA replication, and with replication forks \n 4. Combining with the neurotransmitter dopamine and activating adenylate cyclase via coupling to Gi/Go to initiate a change in cell activity. \n 5. Any process that modulates the frequency, rate or extent of the growth of all or part of an organism so that it occurs at its proper speed, either globally or in a specific part of the organisms development.   '

extractPrompt =  "In the following article, look for any evidence of any Biological Processes, molecular functions, or cellular components that involve [species] and the gene product identified by [geneID]. Give a reasonable description of each one that has strong supporting evidence as one or two complete sentences.  Give a numbered list, one for each description found.   If there is no evidence of any specific biological process, molecular function, or cellular component, reply with an empty list [].  Add NO other commentary. The article follows: "


extractPromptQuote2 =  ".\n  From that article, look for evidence of any Biological Processes, molecular functions, or cellular components that involve [species] and the gene product identified by [geneID]. Give a quote from the article of the supporting evidence as complete sentences.  Supply these as a numbered list.   If there is no evidence of any specific biological process, molecular function, or cellular component, reply with an empty list [].   Do not add any other commentary.  1. Only consider direct experimental evidence from THIS paper (not citations/references to other work). "


extractPromptQuote1 = '''For the following article, focusing specifically on [species] and gene product [geneID]:

1. Only consider direct experimental evidence from THIS paper (not citations/references to other work).
2. Only include evidence from the Results section (not Introduction or Discussion).
3. For each piece of evidence:
   - Provide the complete quote as full sentences
   - Include figure/table references if present
   - Specify which section of the paper the quote comes from
   - Indicate if multiple genes/proteins are being discussed in the same quote
   - Note any markers or co-localization studies used
4. For localization evidence:
   - Include all relevant control experiments
   - Note any temporal/developmental stage specificity
5. Exclude:
   - General statements about protein families
   - Domain predictions or sequence analysis
   - Evidence cited from other papers
   - Hypothetical or predicted functions

Format the response as:
Evidence #:
- Quote: [exact text]
- Section: [paper section]
- Figure/Table: [reference if any]
- Additional context: [multiple genes, controls, etc.]

If no direct experimental evidence exists in this paper, respond with "No direct experimental evidence found."'''


replaceGenePromptRewrite = "In the following text, describe any cellular component, molecular function or biological process without  references to the specific gene product names or identifiers, like [geneID]. This should be in the style of a Gene Ontology description. Do not add other commentary or conversation. The text is: "

replaceGenePrompt = "In the following text, remove references to the specific gene product names or identifiers, like [geneID] .  Replace it with a generic term, 'protein', which is not specific to this gene product. Do not add other commentary or conversation. The text is: "

replaceSpeciesPromptA = "In the following text, remove references to a specific species names or identifiers, like [species] .  Replace it with the generic term, 'organism', which is not specific to this species.  ADD NO OTHER COMMENTARY. The text is: "

replaceSpeciesPrompt = "In the following text, remove references to a specific species names or identifiers, like [species].  Replace it with the generic term, 'organism', which is not specific to this species.  Do not add any other commentary. The text is: "



removeQuotePrompt = "The following text may contain a quote from a paper.  If so, remove the quote, and repeat the rest of the text without the quote. If not, repeat the text. Add NO OTHER COMMENTARY.   The text is: "

keepQuotePrompt = "The following text may contain a quote from a paper.  If so, remove the rest of the text and repeat only the quote. If not, just repeat the entire text. Add NO OTHER COMMENTARY.   The text is: "


convertJSONPrompt = "Take the list of items that are Biological process, functions, or cellular components  from the following text and convert it to a json format single list only. It is vital that the output contains full descriptions with complete sentences and contains every piece of biological information that is contained in the input. This is the text: "        

simpleSystemPrompt = "You are an assistant helpinh to convert text to a machine readable format.  Reply only in the required format with no other commentary or formatting. Do not convert to a short format unless specifically requested."


>>>>>>> Stashed changes
convertJSONSystemPrompt = "You are an assistant converting text to a machine readable format.  Reply only in the required format with no other commentary or formatting. Write text only in complete sentences, not as bullet points or key terms."

listJSONprompt = 'Convert the following into the format of a single list, in valid JSON format (such as ["sentence one","sentence two"] ). Remove any dictionary keys and convert to flat lists. If there is no content give an empty list.  Give a JSON list with no other commentary: '                

rewriteSystemPrompt = 'You are an assistant that is curating written biological data so that it is in a consistent format.  Your output should be in the style of a Gene Ontology description, but do not add content.  He is a small selection of examples of Gene Ontology descriptions:  1. "Entry of a symbiont into the body, tissues, or cells of a host organism as part of the symbiont life cycle. The host is defined as the larger of the organisms involved in a symbiotic interaction."  \n 2. "The secretion of neuropeptides contained within a dense core vesicle by fusion of the granule with the presynaptic membrane, stimulated by a rise in cytosolic calcium ion concentration \n 3. A heterotetrameric protein complex that associates with replication origins, where it is required for the initiation of DNA replication, and with replication forks \n 4. Combining with the neurotransmitter dopamine and activating adenylate cyclase via coupling to Gi/Go to initiate a change in cell activity. \n 5. Any process that modulates the frequency, rate or extent of the growth of all or part of an organism so that it occurs at its proper speed, either globally or in a specific part of the organisms development. \n 6,. Any process that modulates the frequency, rate or extent of a molecular function, an elemental biological activity occurring at the molecular level, such as catalysis or binding. \n 7.         Any process that activates or increases the frequency, rate or extent of activity of a transcription factor, any factor involved in the initiation or regulation of transcription. \n 8. Any process that modulates the rate, frequency or extent of the chemical reactions and pathways resulting in the formation of a macromolecule, any molecule of high relative molecular mass, the structure of which essentially comprises the multiple repetition of units derived, actually or conceptually, from molecules of low relative molecular mass.'


checkSystemPrompt =  "You are an assistant checking if two descriptions may actually refer to the same entry in a Gene Ontology database.  Reply with YES or NO only with no other commentary."

checkPrompt = "Do the following two descriptions roughly match. Description 1: '[desc1]'\n  \nDescription 2: '[desc2]'.\n Reply as YES or NO with no other commentary. "

rewritePrompt = "Rewrite the following text, if necessary, to match the format at style of a Gene Ontology description.  Do not add content, if the text is not a reasonable description of a specific concept , reply with 'None'.  Reply with the rewritten text only, and never add any other commentary: "

removeCommentaryPrompt = "Remove additional commentary and reply with just decription from the following text: " 

<<<<<<< Updated upstream
=======

simplifyPrompt = "From the following text exrtract EVERYTHING that is specific to [geneID].  Use quotes in preference to a synopsis.  Very long quotes are acceptable, if relevant.  If there is nothing specific you may say nothing.  Do not miss anything out, it is important we get the quotes that give us ALL information about the study of [geneID].  The text to quote from is : "
    
>>>>>>> Stashed changes
    
def getSystemForQuote(prompt):
  
    qprompt = "  Here are a number of examples we have previously found of quotes that support a particular GO term annotation. We are looking for similar levels of description and detail although the specific content will usually be different:  <examples>"
    for i in range(EXAMPLE_QUOTES_NUM):
        x= quote_data[i]
        go = x[0]
        quote = x[1]
        desc = x[2]
        if len(desc) < 1200:
            qprompt = qprompt +" <example><go_term>"+go+"</go_term><go_description>"+desc+"</go_description><evidence_quote>"+quote+"</evidence_quote></example>"
        
    qprompt = qprompt + "</examples>"
<<<<<<< Updated upstream
    
    print(prompt+qprompt)
    return prompt + qprompt
        
    
    
=======
    return prompt + qprompt
        
    
def getChildGoTerms(go):
    
    children = GOntoSim.get_go_children(go)
    
    #is a dictionary, keys are id, values are description
    print("GET CHILDREN",go,len(children))
 
    
    return children
    
    
def getChildAlternative(go, pair,sectionText):
    
    config = ConfigHandler()
    systemPrompt = config.getSystemPromptStartForGetPaperGOTerms()
    systemPrompt = "You are an automated curator, used as part of a system to find assumed Gene Ontology term descriptions from a scientific paper.  Give succint answers in the format requested. Do not add other commentary, replies, or symboles."
    
    children = getChildGoTerms(go)
    if len(children) < 2:
        return go    

    model = LLMHandler(systemPrompt=systemPrompt, cache = True)
    go_id = go
      
    if len(children) < 10:   
  
        list_prompt ="<instruction>From this numbered list of GO terms in relation to the gene [geneID] which is the single most accurately described by the previous passage. Give the answer as the number from the list. </instruction>\n"
        
        list_prompt =  replaceTerms(list_prompt,pair)
        list_prompt = "<passage>"+sectionText+ "</passage>\n" +    list_prompt
              
        
        ids = {}
          
        for pos, child in enumerate(children, start=1):
            ids[pos] = child
            list_prompt = list_prompt+ str(pos)+". "+children[child] +"\n"
            
        
        
        #try to simplify before asking specific questions
        number = model.askWithRetry(
            message=list_prompt,
        )   
        
        
        print("SELECTED " + number +"  FROM "+list_prompt)
        
            
        convert_prompt = "<number>"+number+"</number> Extract just a single digit from this text. Add no other commentary as automated processing is vital"
        
        number = model.askWithRetry(
            message=convert_prompt,
        )   
        
        #checking if it is correct
        index = int(number)
        
        if index in ids:
            go_id = ids[index]
            
    # checking it now - either original or best child
    go_description = children[go_id]

    print("PAIR=",pair)
     
    check_prompt = "<passage>"+sectionText+ "</passage>\n <instruction>Does this passage provide good evidence for the GO term "+go_id+" : " + go_description+" related to gene "+pair["geneID"]+" </instruction>"
    
    
    check_answer = model.askWithRetry(
        message=check_prompt,
    )   
    
    print("check_answer=",check_answer, go_id,go_description)
    check_prompt2 = "<passage>"+check_answer+ "</passage>\n <instruction>Does this passage provide an affirmative answer.  Answer only as Yes or No with no other commentary </instruction>"
    
    
    check_2 = model.askWithRetry(
        message=check_prompt2,
    )   
    if check_2.lower().startswith("n"):
        return None
            
        
    return go_id
>>>>>>> Stashed changes
    
def replaceTerms(prompt: str, pair):
    for key in pair:
        prompt = prompt.replace("["+key+"]",pair[key])
    
    return prompt
    
def getPaperGOTerms(pmid: str, textSource: str):
    status = StatusHandler(pmid)
    
    if not status.areSpeciesFetched():
        raise ValueError("Genes have not yet been fetched for this paper")
    
#    if status.areGOTermsFetched():
#        raise ValueError("GO terms have already been fetched for this paper")


    if textSource == "plaintext":

        plaintextFilePath = status.getPlaintextFilePath()
        with open(plaintextFilePath) as plaintextFile:
            promptText = plaintextFile.read()
    elif textSource == "summary":

        summaryFilePath = status.getSummaryFilePath()
        with open(summaryFilePath, encoding='utf-8') as summaryFile:
            promptText = summaryFile.read()

<<<<<<< Updated upstream
    if textSource == "plaintext":
        plaintextFilePath = status.getPlaintextFilePath()
        with open(plaintextFilePath) as plaintextFile:
            promptText = plaintextFile.read()
    elif textSource == "summary":
        summaryFilePath = status.getSummaryFilePath()
        with open(summaryFilePath, encoding='utf-8') as summaryFile:
            promptText = summaryFile.read()
        
=======
>>>>>>> Stashed changes
    geneSpeciesPairs = status.getGeneSpeciesPairs()
    
    goTerms = []
    failedPairs = []
    
<<<<<<< Updated upstream
   
=======

>>>>>>> Stashed changes
  
    config = ConfigHandler()
    systemPromptStart = config.getSystemPromptStartForGetPaperGOTerms()

    responseSchema = config.getResponseSchemaForGetPaperGOTerms()

    sectionText = status.getJSONResults()

    print("PAIRS",geneSpeciesPairs,len(geneSpeciesPairs))
    
    
    go_terms_structure = {}
    for pair in geneSpeciesPairs:
<<<<<<< Updated upstream
        start = time.time()
=======
        
        gene_id = pair["geneID"]
        
        
        start = time.time()
        gene_data = status.getGenesData()
        
 
        gene_db_id = gene_id   
        #looking for the vpdb id
        gene_data = gene_data.get("response",[])
        for species in gene_data["species"]:
 
            for genes in species["genes"]:
                if genes["identifier"] == gene_id:
                    gene_db_id  = genes["geneID"]
                    print("MATCH", gene_id, gene_db_id)
        
        
        
        
        
        synonyms_text= ""

        if gene_id in gene_data:
            print("Check for synonyms",gene_data[gene_id])
            
            synonyms_text = " or ".join(gene_data[gene_id]["synonyms"])
            
        
        
        

        
>>>>>>> Stashed changes
        systemPrompt = replaceTerms(extractSystemPrompt,pair)
        
         
       #  quote_data
        if EXAMPLE_QUOTES:
            systemPrompt = getSystemForQuote(systemPrompt)

        fullModel = LLMHandler(systemPrompt=systemPrompt, cache = True)
        
<<<<<<< Updated upstream
        prompt =  replaceTerms(extractPrompt,pair)
        if QUOTE_STYLE:
            prompt =  replaceTerms(extractPromptQuote,pair)

        prompt += promptText
        
        
        res = fullModel.askWithRetry(
            message=prompt,
        )
 
        model = LLMHandler(systemPrompt="")
        
#make it generic to match the Gene ontology terms   
        
        prompt =  replaceTerms(replaceGenePrompt,pair)
        
        
        prompt = prompt + res
        res = model.askWithRetry(
            message=prompt,
        )
        
=======
        
        simplify = replaceTerms(simplifyPrompt,pair) + sectionText

        #try to simplify before asking specific questions
        gene_summary= fullModel.askWithRetry(
            message=simplify,
        )
        
        promptText = gene_summary
        
        prompt =  replaceTerms(extractPrompt,pair)
        prompt += promptText
        if QUOTE_STYLE:
            prompt =  replaceTerms(extractPromptQuote2,pair)
            prompt = promptText + prompt

        
        
        
        res = fullModel.askWithRetry(
            message=prompt,
        )
 
 
 
        model = LLMHandler(systemPrompt="")
        
#make it generic to match the Gene ontology terms   
        print("QUOTE=len",len(prompt))
        
        print("QUOTERES=",res)
        
        quote = res
        prompt =  replaceTerms(replaceGenePromptRewrite,pair)
        
        
        prompt = prompt + res
        res = model.askWithRetry(
            message=prompt,
        )
        
        
        
>>>>>>> Stashed changes
#make it generic to match the Gene ontology terms
        prompt =  replaceTerms(replaceSpeciesPrompt,pair)
        prompt = prompt + res
        res = model.askWithRetry(
            message=prompt,
        )
        
#make it json                

        prompt =  replaceTerms(convertJSONPrompt,pair)
                
        prompt = prompt + res

        
        model = LLMHandler(systemPrompt=convertJSONSystemPrompt)
        res = model.askWithRetry(
            message=prompt,
        )
        
<<<<<<< Updated upstream
=======
        
>>>>>>> Stashed changes
         # textToComplete= "["
#make it readable as a json list

        prompt = listJSONprompt + res
        
        res = model.askWithRetry(
            message=prompt,
        )
        
        
        go_sentences = [res]
<<<<<<< Updated upstream
=======
        print("GO_SENTENCES=",go_sentences)
>>>>>>> Stashed changes
        try:
            go_sentences = json.loads(res)
        except:
            print("not json",res)
        pairGOTermsData = []

        


            
        for s in go_sentences:
<<<<<<< Updated upstream
            if len(s) < 10:
=======
            if len(s) < 6:
>>>>>>> Stashed changes
                continue
                
            if not QUOTE_STYLE:
                model = LLMHandler(systemPrompt=rewriteSystemPrompt,cache=True)
                
    # try to match 'style'            
                prompt = rewritePrompt + s
                s = model.askWithRetry(message=prompt,)    
<<<<<<< Updated upstream
                
            if len(s) < 10:
=======
            else:
                model = LLMHandler(systemPrompt=simpleSystemPrompt,cache=True)
                prompt = removeQuotePrompt + s
                s = model.askWithRetry(message=prompt,)    
                
                
                
            if len(s) < 6:
>>>>>>> Stashed changes
                continue

#in case we can't trust it to not add commentary
            if False:
                model = LLMHandler(systemPrompt='')
                
                prompt = removeCommentaryPrompt + s
                s = model.askWithRetry(message=prompt,)    


            #get top 3
            find_terms = search(s, TOP_TERMS)
            
            #check the similarity scoring
            
            print("search score",find_terms[0][1])
 
            idx = 1
            
<<<<<<< Updated upstream
            #This doesn't appear to be helpful
=======
            #getChildGoTerms(go):
            
>>>>>>> Stashed changes
            if True:
                prompt = "From this numbered list, which term most closely matches the term "+s+" \n"
                num = 1
                for term in find_terms:
                    if float(term[1]) < SCORE_THRESHOLD:
                        break
                    prompt += str(num)+" : "+term[3]+" \n"
                    num += 1
                
                res = "1"
                if num > 2:
                    model = LLMHandler(systemPrompt="You are an assistant selecting the best match from a list. Reply only with numbers, as the  position in the list.")
                    res = model.askWithRetry(message=prompt,)
                    
                
                try:
                    idx = int(res)
                    if idx  < 1:
                        idx =   1
                except:
                    idx = 1
                
            if len(find_terms) == 0:
                continue

            term = find_terms[0]
            try:
                term = find_terms[idx-1]
            except:
                 pass
            go_id = term[0]
            
<<<<<<< Updated upstream
=======
            
            #children = getChildGoTerms(go_id)
            
                
                
>>>>>>> Stashed changes

            
            model = LLMHandler(systemPrompt=checkSystemPrompt)
                        
            replaceVals = {"desc1":s,"desc2":term[3]}
<<<<<<< Updated upstream
=======
            print("Checking",s,"EQUALS",term[3])
            
>>>>>>> Stashed changes
            prompt = replaceTerms(checkPrompt,replaceVals)
            

            
            res = model.askWithRetry(message=prompt,)
            
<<<<<<< Updated upstream
            
            if len(res) > 4 or res.lower().strip() == "yes":
                
            
            #validate will work easiest if it matches the name=descrptions
                pairGOTermsData.append({"id":go_id,"full_description":term[3],"description":term[2]})
         

      
            pair["goTermIDs"] = [term["id"] for term in pairGOTermsData]
            goTerms += pairGOTermsData
=======
            IGNORE_MEANING_CHECK = True
            
            if IGNORE_MEANING_CHECK or len(res) > 4 or res.lower().strip() == "yes":
                
                go_id = getChildAlternative(go_id, pair, gene_summary)
                if go_id is None:
                    print("Failed validation (after child check)")
                else:
            #validate will work easiest if it matches the name=descrptions
                    #pairGOTermsData.append({"id":go_id,"full_description":term[3],"description":term[2]})
                    pairGOTermsData.append({"id":go_id,"full_description":term[3],"description":term[2], "species":pair["species"], "geneID":gene_db_id, "geneName":gene_id})
                  
                    
                    print(pmid,go_id,term[2],term[4])
            else:
                print("Reject match")
         

      
            # pair["goTermIDs"] = [term["id"] for term in pairGOTermsData]
        goTerms += pairGOTermsData
            
 

    #need to get the go terms with species, gene pairs
        
>>>>>>> Stashed changes
        
    seen = set()
    uniqueGoTerms = []

    for term in goTerms:
        if term["id"] not in seen:
            term["validated"] = True
            seen.add(term["id"])
            uniqueGoTerms.append(term)
            
  
    print("SAVE STRUCTRE",goTerms)
    
    
    
    status.updateField("getPaperGOTerms", {
        "success": True,
        "failCount": len(failedPairs),
        "goTerms": uniqueGoTerms,
        "structuredGoTerms": goTerms,
        "geneSpeciesPairsWithGOTerms": geneSpeciesPairs,
        "failedPairs": failedPairs
    })
    
    return {
        "goTerms": uniqueGoTerms,
        "failCount": len(failedPairs)
    }

if __name__ == "__main__":
<<<<<<< Updated upstream
    if len(sys.argv) != 3:
        print("Usage: python getPaperGOTerms.py <pmid>")
        sys.exit(1)
        
    pmid = sys.argv[1]
    textSource = sys.argv[2]
=======
    if len(sys.argv) < 2:
        print("Usage: python getPaperGOTerms.py <pmid> [plaintext / summary]")
        sys.exit(1)
        
    pmid = sys.argv[1]
    textSource = "plaintext"
    if len(sys.argv) > 2:
        textSource = sys.argv[2]
>>>>>>> Stashed changes

    if textSource not in ["plaintext", "summary"]:
        print("textSource must be either 'plaintext' or 'summary'")
        sys.exit(1)
    
    try:
        data = getPaperGOTerms(pmid, textSource)
        print(f"GO terms for paper with PMID {pmid} fetched and saved to status file with {data['failCount']} failures")
    except Exception as err:
        print(f"Error getting paper GO Terms: {err}")
