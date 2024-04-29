import sys
import requests
import metapub
from handlers import StatusHandler

def downloadPaper(pmid):
    status = StatusHandler(pmid)
    
    if status.isPaperDownloaded():
        raise ValueError("Paper already downloaded")
    
    # TODO - Make it fetch by id
    
    pdfURL = metapub.FindIt(pmid).url
    if pdfURL is None:
        raise ValueError("No PDF found for this paper.")
    
    res = requests.get(pdfURL)
    if res.status_code != 200:
        print(res.reason)
        raise requests.exceptions.RequestException("Failed to fetch PDF")
        
    statusData = status.get()
    statusData["downloadPaper"] = {
        "status": "downloaded",
        "filename": f"{pmid}.pdf"
    }
    
    status.update(statusData)
    
    pdfPath = status.getPDFPath()
    
    with open(pdfPath, "wb") as pdfFile:
        pdfFile.write(res.content)
        
    return pdfPath
    
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python download_paper.py <pmid>")
        sys.exit(1)
        
    pmid = sys.argv[1]
    
    try:
        path = downloadPaper(pmid)
        print(f"Paper with PMID {pmid} downloaded to {path}")
    except Exception as err:
        print(f"Error downloading paper: {err}")