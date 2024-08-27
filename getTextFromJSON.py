import sys
import json
import os
from utils.handlers import StatusHandler, ConfigHandler
from xml.etree import ElementTree as ET


def extractTableFromXML(xml):
    root = ET.fromstring(xml)
    tableData = []
    headers = []
    for thead in root.findall('.//thead'):
        for tr in thead.findall('.//tr'):
            row = []
            for td in tr.findall('.//td'):
                text = (td.text or "").strip()
                colspan = int(td.get('colspan', 1))
                for _ in range(colspan):
                    row.append(text)
            headers.append(row)

    for tbody in root.findall('.//tbody'):
        for tr in tbody.findall('.//tr'):
            row = []
            for td in tr.findall('.//td'):
                text = (td.text or "").strip()
                row.append(text)
            tableData.append(row)
    completeData = headers + tableData
    return completeData


def mergeSections(pmid):
    status = StatusHandler(pmid)
    config = ConfigHandler()
    
    if not status.isJSONFetched():
        raise ValueError("Paper JSON not yet fetched")
    
    if status.isPaperConverted():
        raise ValueError("Text file already generated")
    
    jsonFilePath = status.getJSONFilePath()
    
    with open(jsonFilePath, "r") as jsonFile:
        article = json.load(jsonFile)
        
    sectionsToGet = config.getMergeSectionsSections()
    sections = {section: "" for section in sectionsToGet}
    
    passages = []
    for a in article:
        for document in a["documents"]:
            passages += document["passages"]
                
    for passage in passages:
        sectionType = passage["infons"]["section_type"].lower()
        if sectionType in sectionsToGet:
            if sectionType == "table" and "xml" in passage["infons"]:
                tableData = extractTableFromXML(passage["infons"]["xml"])
                sections[sectionType] = sections[sectionType] + str(tableData) + "\n"
            else:
                sections[sectionType] = sections[sectionType] + f"{passage['text']}\n"
            
    plaintextFileName = f"{pmid}.txt"
    plaintextFilePath = os.path.join(config.getPlaintextFolderPath(), plaintextFileName)
            
    with open(plaintextFilePath, "w") as plaintextFile:
        for section in sections.values():
            plaintextFile.write(f"{section}\n")
    
    status.updateField("getPlaintext", {
        "success": True,
        "sourceFileType": "json",
        "filename": plaintextFileName
    })
    
    return plaintextFilePath


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python getTextFromJSON.py <pmid>")
        sys.exit(1)
        
    pmid = sys.argv[1]
    
    try:
        path = mergeSections(pmid)
        print(f"JSON Paper with PMID {pmid} converted to txt and saved as {path}")
    except Exception as err:
        print(f"Error getting paper from JSON: {err}")