from utils.handlers import ConfigHandler, StatusHandler
from utils import helpers
from llms import LLMHandler
import sys
import json
import requests
from typing import List
import jsonschema

def validateGOTermDescriptions(pmid: str):
    status = StatusHandler(pmid)
    
    if not status.areGOTermsFetched():
        raise ValueError("GO terms have not yet been fetched for this paper")
    
    if status.areGOTermDescriptionsValidated():
        raise ValueError("GO terms have already been validated")
    
    goTerms = status.getFetchedGOTerms()
    
    acceptedGOTerms = []
    rejectedGOTerms = []
    apiFailedGOTerms = []
    
    for term in goTerms:
        reqURL = f"https://www.ebi.ac.uk/QuickGO/services/ontology/go/terms/{term['id']}"
        res = requests.get(reqURL, headers={ "Accept" : "application/json"})
        if not res.ok:
            print(f"api request for {term['id']} failed")
            apiFailedGOTerms.append(term)
            continue
        
        goTermAPIInfo = json.loads(res.text)

        desc: str = ""
        if goTermAPIInfo["results"]:
            desc = goTermAPIInfo["results"][0]["name"]
        else:
            rejectedGOTerms.append({
                "id": term["id"],
                "description": term["description"],
            })
            continue

        if desc.lower() == term["description"].lower():
            acceptedGOTerms.append(term)
            continue
        
        synonyms: List[str] = []
        if "synonyms" in goTermAPIInfo["results"][0]:
            synonyms = [synonym["name"] for synonym in goTermAPIInfo["results"][0]["synonyms"]]
            
            if term["description"].lower() in [synonym.lower() for synonym in synonyms]:
                acceptedGOTerms.append(term)
                continue
        
        config = ConfigHandler()
        
        systemPrompt = config.getSystemPromptStartForValidateGOTermDescriptions()
        model = LLMHandler(systemPrompt=systemPrompt)
        
        question = f"Does '{term['description']}' mean the same thing as any of the terms: " + ", ".join("'" + i + "'" for i in ([desc] + synonyms))
        
        res = model.askWithRetry(question)
        
        responseSchema = config.getResponseSchemaForValidateGOTermDescriptions()
        try:
            isAccepted = json.loads(res)["result"]
            jsonschema.validate(isAccepted, responseSchema)
        except:
            pass
        
        if not isAccepted:
            rejectedGOTerms.append({
                "id": term["id"],
                "description": term["description"],
                "actualDescription": desc
            })
            continue
        
        acceptedGOTerms.append(term)
        
    status.updateField("validateGOTermDescriptions", {
        "success": True,
        "acceptedGOTerms": acceptedGOTerms,
        "rejectedGOTerms": rejectedGOTerms,
        "apiFailedGOTerms": apiFailedGOTerms
    })
    
    return {
        "acceptedCount": len(acceptedGOTerms),
        "rejectedCount": len(rejectedGOTerms),
        "apiFailedCount": len(apiFailedGOTerms)
    }
    

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python validateGOTermDescriptions.py <pmid>")
        sys.exit(1)
        
    pmid = sys.argv[1]
    
    try:
        data = validateGOTermDescriptions(pmid)
        print(f"GO term descriptions for paper with PMID {pmid} validated and results saved to status file with [{data['acceptedCount']}] accepted, [{data['rejectedCount']}] rejected, and [{data['apiFailedCount']}] QuickGO API failures")
        if not data["apiFailedCount"] == 0:
            print("Run the script again to try the api failed terms again.")
    except Exception as err:
        print(f"Error validating GO Terms: {err}")
