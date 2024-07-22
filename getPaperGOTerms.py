from utils.handlers import ConfigHandler, StatusHandler
from llms import LLMHandler
import re
import sys
import json
import jsonschema

def getPaperGOTerms(pmid: str, textSource: str):
    status = StatusHandler(pmid)
    
    if not status.areSpeciesFetched():
        raise ValueError("Genes have not yet been fetched for this paper")
    
    if status.areGOTermsFetched():
        raise ValueError("GO terms have already been fetched for this paper")

    if textSource == "plaintext":
        plaintextFilePath = status.getPlaintextFilePath()
        with open(plaintextFilePath) as plaintextFile:
            promptText = plaintextFile.read()
    elif textSource == "summary":
        summaryFilePath = status.getSummaryFilePath()
        with open(summaryFilePath) as summaryFile:
            promptText = summaryFile.read()
        
    geneSpeciesPairs = status.getGeneSpeciesPairs()
    
    goTerms = []
    failedPairs = []
    
    config = ConfigHandler()
    systemPromptStart = config.getSystemPromptStartForGetPaperGOTerms()
    responseSchema = config.getResponseSchemaForGetPaperGOTerms()
    
    for pair in geneSpeciesPairs:
        model = LLMHandler(systemPrompt=systemPromptStart + promptText)
        res = model.askWithRetry(
            message=json.dumps(pair),
            textToComplete="["
        )
        regex = r'\[\s*(?:\{\s*"id":\s*".+?"\s*,\s*"description":\s*".+?"\s*\}\s*,?\s*)+\s*\]'
        match = re.search(regex, res, re.DOTALL)
        if match:
            res = match.group(0)

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
    if len(sys.argv) != 3:
        print("Usage: python getPaperGOTerms.py <pmid>")
        sys.exit(1)
        
    pmid = sys.argv[1]
    textSource = sys.argv[2]

    if textSource not in ["plaintext", "summary"]:
        print("textSource must be either 'plaintext' or 'summary'")
        sys.exit(1)
    
    try:
        data = getPaperGOTerms(pmid, textSource)
        print(f"GO terms for paper with PMID {pmid} fetched and saved to status file with {data['failCount']} failures")
    except Exception as err:
        print(f"Error getting paper GO Terms: {err}")