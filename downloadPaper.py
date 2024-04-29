import sys
import os
import config
import json
import requests
import utils

def downloadPaper(id):
    statusFilePath = os.path.join(config.getStatusFolderPath(), f"{id}.json")
    
    statusData = {}
    
    if os.path.isfile(statusFilePath):
        with open(statusFilePath, "r") as statusFile:
            statusData = json.load(statusFile)
            
            if utils.hasattrdeep(statusData, ["downloadPaper", "status"]) and statusData["downloadPaper"]["status"] == "downloaded":
                raise ValueError("Paper already downloaded")
                
    # TODO: Find way of fetching by PMID here (current solution is static and temporary since metapub doesn't support it)
    
    pdfURL = "https://www.dovepress.com/getfile.php?fileID=15943"
    
    res = requests.get(pdfURL)
    if res.status_code != 200:
        print(res.reason)
        raise requests.exceptions.RequestException("Failed to fetch PDF")
        sys.exit(1)
    
    # END TODO
    
    pdfFilePath = os.path.join(config.getPDFsFolderPath(), f"{id}.pdf")
    with open(pdfFilePath, "wb") as pdfFile:
        pdfFile.write(res.content)

    statusData["downloadPaper"] = {
        "status": "downloaded",
        "filename": f"{id}.pdf"
    }
    
    with open(statusFilePath, "w") as statusFile:
        json.dump(statusData, statusFile, indent=4)
    
if __name__ == "__main__":
    
    if len(sys.argv) != 2:
        print("Usage: python download_paper.py <paper_id>")
        sys.exit(1)
        
    id = sys.argv[1]
    
    try:
        downloadPaper(id)
    except Exception as err:
        print(f"Error downloading paper: {err}")