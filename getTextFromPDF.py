import sys
import os
from handlers import ConfigHandler, StatusHandler
from pdfminer.high_level import extract_text

def getTextFromPDF(pmid):
    config = ConfigHandler()
    status = StatusHandler(pmid)
    
    if not status.isPDFFetched():
        raise ValueError("Paper with provided ID has not been fetched yet")
    
    if status.isPaperConverted():
        raise ValueError("Text file has already been generated")

    plaintextFileName = f"{pmid}.txt"
    plaintextFilePath = os.path.join(config.getPlaintextFolderPath(), plaintextFileName)
    
    if os.path.isfile(plaintextFilePath):
        raise FileExistsError("Plaintext file for this document already exists")
    
    pdfPath = status.getPDFPath()
    plaintext = extract_text(pdfPath)
        
    with open(plaintextFilePath, "w") as plaintextFile:
        plaintextFile.write(plaintext)
            
    statusData = status.get()
    statusData["getPlaintext"] = {
        "status": "converted",
        "sourceFileType": "pdf",
        "filename": plaintextFileName
    }
    
    status.update(statusData)
    
    return plaintextFilePath
    

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python convertPDF.py <paper_id>")
        sys.exit(1)
        
    pmid = sys.argv[1]
    
    try:
        path = getTextFromPDF(pmid)
        print(f"PDF with PMID {pmid} converted to plaintext and saved as {path}")
    except Exception as err:
        print(f"Error converting PDF to plaintext: {err}")