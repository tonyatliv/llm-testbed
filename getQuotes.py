import sys
from utils.handlers import StatusHandler, ConfigHandler
import jsonschema
import json
from llms import LLMHandler

filename = 'go_terms.json'
with open(filename, 'r') as file:
    go_data = json.load(file)

vdbDataCache = None

quoteStore = []

def loadQuotes(pmid):
    
    status = StatusHandler(pmid)
    quotes = status.getQuotes()
    
    for goterm in quotes:
        quote = quotes[goterm]
        godesc = quote[1]
        quote = quote[0]
        
        if len(quote) < 2:
            print(pmid,quote)
            continue
        
        
        quoteStore.append([goterm,quote,godesc])
        
    
    
def putQuotes():
   filename = 'all_quotes.json'
   with open(filename, 'w') as f:
       json.dump(quoteStore, f, indent=4)
    
    
    
def getQuotes(pmid, textSource, vdbDataFile):
    global vdbDataCache
    status = StatusHandler(pmid)
    config = ConfigHandler()
    
    if vdbDataCache is None:
        with open(vdbDataFile, 'r') as file:
            vdbDataCache = json.load(file)


    if textSource == "plaintext":
        plaintextFilePath = status.getPlaintextFilePath()
        with open(plaintextFilePath) as plaintextFile:
            promptText = plaintextFile.read()
    elif textSource == "summary":
        summaryFilePath = status.getSummaryFilePath()
        with open(summaryFilePath) as summaryFile:
            promptText = summaryFile.read()
        
    systemPrompt = "You are a helpful assistant finding quotes from publications that provide evidential support.  You must only ever quote from the text you are given as this will be automatically checked and the program will fail if it is not a direct quote.  If there is no suitable quote reply with an empty line."
    
    vdbData = {}
    for subData in vdbDataCache:
        if subData['PMID'] == pmid:
            vdbData = subData
    
    model = LLMHandler(systemPrompt=systemPrompt)
    vdbGOTerms = []
    for species in vdbData['species']:
        for gene in species['genes']:
            for go_term in gene['GO_terms']:
                vdbGOTerms.append(go_term['GO_ID'])
       
    vdbGOTerms = list(set(vdbGOTerms))

    quotes = {}
    
    for goTerm in vdbGOTerms:
        if goTerm not in go_data:
            continue
                
        goTermData = go_data[goTerm]
        goDesc = goTermData["definition"]
        prompt = "From the following paper, give the single quote, of up to five sentences, that best supports the evidence of annotating the GO Term "+goTerm+" which means "+goDesc+". Only quote from the paper, with no other commentary.  The paper follows: "
        
        promptText = prompt + promptText
        response = model.askWithRetry(promptText)
        quotes[goTerm] = [response,goDesc]
        





    fullAnswer = quotes
    status.updateField("getQuotes", {
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