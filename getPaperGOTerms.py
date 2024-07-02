from utils.handlers import ConfigHandler, StatusHandler
from llms import LLMHandler
import sys
import json
import jsonschema

def getPaperGOTerms(pmid: str):
    status = StatusHandler(pmid)
    
    if not status.areSpeciesFetched():
        raise ValueError("Genes have not yet been fetched for this paper")
    
    if status.areGOTermsFetched():
        raise ValueError("GO terms have already been fetched for this paper")

    plaintextFilePath = status.getPlaintextFilePath()
    with open(plaintextFilePath) as plaintextFile:
        paperPlaintext = plaintextFile.read()
        
    geneSpeciesPairs = status.getGeneSpeciesPairs()
    
    goTerms = []
    failedPairs = []
    
    config = ConfigHandler()
    systemPromptStart = config.getSystemPromptStartForGetPaperGOTerms()
    responseSchema = config.getResponseSchemaForGetPaperGOTerms()
    
    for pair in geneSpeciesPairs:
        model = LLMHandler(systemPrompt=systemPromptStart + paperPlaintext)
        res = model.askWithRetry(
            message=json.dumps(pair),
            textToComplete="["
        )
        print(res)
        
        try:
            pairGOTermsData = json.loads(res)
            jsonschema.validate(pairGOTermsData, responseSchema)
        except Exception:
            failedPairs.append(pair)
            
        pair["goTermIDs"] = [term["id"] for term in pairGOTermsData]
        goTerms += pairGOTermsData
    
    seen = set()
    uniqueGoTerms = []

    for term in goTerms:
        if term["id"] not in seen:
            seen.add(term["id"])
            uniqueGoTerms.append(term)
            
    goTerms = uniqueGoTerms
    
    status.updateField("getPaperGOTerms", {
        "success": True,
        "failCount": len(failedPairs),
        "goTerms": goTerms,
        "geneSpeciesPairsWithGOTerms": geneSpeciesPairs,
        "failedPairs": failedPairs
    })
    
    return {
        "goTerms": goTerms,
        "failCount": len(failedPairs)
    }

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python getPaperGOTerms.py <pmid>")
        sys.exit(1)
        
    pmid = sys.argv[1]
    
    try:
        data = getPaperGOTerms(pmid)
        print(f"GO terms for paper with PMID {pmid} fetched and saved to status file with {data['failCount']} failures")
    except Exception as err:
        print(f"Error getting paper GO Terms: {err}")