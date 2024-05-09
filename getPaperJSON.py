import sys
from handlers import StatusHandler, ConfigHandler
import json
import requests
import os

def getPaperJSON(pmid: str):
    status = StatusHandler(pmid)
    config = ConfigHandler()
    
    if status.isJSONFetched():
        raise ValueError("Paper JSON already fetched")
    
    url = f"https://www.ncbi.nlm.nih.gov/research/bionlp/RESTful/pmcoa.cgi/BioC_json/{pmid}/unicode"
    
    res = requests.get(url)
    if res.status_code != 200:
        raise Exception("No JSON data found for this paper")
    
    articleJSON = json.loads(res.content)
    
    jsonFileName = f"{pmid}.json"
    jsonFilePath = os.path.join(config.getJSONFolderPath(), jsonFileName)
    
    with open(jsonFilePath, "w") as sectionsFile:
        json.dump(articleJSON, sectionsFile, indent=4)
    
    statusData = status.get()
    statusData["getPaperJSON"] = {
        "status": "fetched",
        "sourceURL": url,
        "filename": jsonFileName
    }
    status.update(statusData)
    
    return jsonFilePath
    
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python download_paper.py <pmid>")
        sys.exit(1)
        
    pmid = sys.argv[1]
    
    try:
        path = getPaperJSON(pmid)
        print(f"JSON file of paper with PMID {pmid} downloaded to {path}")
    except Exception as err:
        print(f"Error getting paper as JSON: {err}")