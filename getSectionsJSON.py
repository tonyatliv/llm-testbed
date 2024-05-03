import sys
from handlers import StatusHandler
import json
import os
import requests

def getSectionsJSON(pmid: str):
    status = StatusHandler(pmid)
    
    if status.areSectionsFetched():
        raise ValueError("Sections already fetched")
    
    url = f"https://www.ncbi.nlm.nih.gov/research/bionlp/RESTful/pmcoa.cgi/BioC_json/{pmid}/unicode"
    
    res = requests.get(url)
    if res.status_code != 200:
        raise Exception("No JSON data found for this paper")
    
    articleJSON = json.loads(res.content)
    
    statusData = status.get()
    statusData["getSectionsJSON"] = {
        "status": "fetched",
        "filename": f"{pmid}.sections.json"
    }
    status.update(statusData)
    
    sectionsFilePath = status.getSectionsFilePath()
    
    with open(sectionsFilePath, "w") as sectionsFile:
        json.dump(articleJSON, sectionsFile, indent=4)
        
    return sectionsFilePath
    
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python download_paper.py <pmid>")
        sys.exit(1)
        
    pmid = sys.argv[1]
    
    try:
        path = getSectionsJSON(pmid)
        print(f"Sections of paper with PMID {pmid} saved to {path}")
    except Exception as err:
        print(f"Error getting sections as JSON: {err}")