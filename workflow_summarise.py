import json
import os
import pandas as pd
import time
import traceback
import sys
from utils.handlers import StatusHandler, ConfigHandler
from getPaperPDF import getPaperPDF
from getPaperJSON import getPaperJSON
from getTextFromJSON import mergeSections
from getPaperSummary import getPaperSummary
from getPaperSpecies import getPaperSpecies
from getPaperGenes import getPaperGenes
from getPaperGOTerms import getPaperGOTerms
from validateGOTermDescriptions import validateGOTermDescriptions
from scoreGOTerms import scoreGOTerms

MAX_PAPERS = 30000
FORCE_UPDATE = False

def workflow(vdbDataFile, resultXLSX, pmids, modelName, textSource):
    summaryTable = {'Model': [modelName], 'Average Score': [0]}
    
    if FORCE_UPDATE:
        for i, pmid in enumerate(pmids, start=1):
            status = StatusHandler(pmid)
        
            status.updateField("getSummary", {
            "success": False     })
            
 
        
        
    for i, pmid in enumerate(pmids, start=1):
        try:
            status = StatusHandler(pmid)
            
            
            print(f"---------\nStart PMID: {pmid}'s Workflow")
            print(status.isSummaryFetched())
            if not status.isSummaryFetched():
                time.sleep(.30)
                print("get summary")
                getPaperSummary(pmid)
     
                
        #still do others even if something goes wrong
        except Exception as err:
            print(f"error: {err}")
            print(traceback.format_exc())

     
    print("Done summarising")



if __name__ == "__main__":

    if len(sys.argv) > 1:
        config = ConfigHandler(sys.argv[1])
    else:
        config = ConfigHandler()

    # VDB data file name
    vdbDataFile = str(os.getenv("VDB_DATA_FILE_PATH"))
    # processed data from VDB
    resultFolder = config.getResultFolderPath()
    
    processedVDBFile = resultFolder+'/filtered_PMID_data.json'
    # result score file
    resultXLSX = resultFolder+"/table_data.xlsx"
    # test model name

    #read description from config

    modelName = config.getLLMDescription()

    # specify text source
    textSource = "summary"

    with open(vdbDataFile, 'r') as file:
        vdbData = json.load(file)
    validEntries = []
    pmids = []
 
    for entry in vdbData:
        species_names = [species['name'] for species in entry['species']]
        
#        if config.getSpecifiedSpecies() not in species_names:
#            continue
        pmid = entry.get("PMID")
        
        status = StatusHandler(pmid)
        if status.isJSONFetched():
            print("FETCHED ALREADY")
            pmids.append(pmid)
            validEntries.append(entry)
        else:
        #only use json files - can't get pdfs anyway
            continue
            time.sleep(3.30)
            try:
                print("NOT FETCHED ALREADY")
                getPaperJSON(pmid)
                pmids.append(pmid)
                validEntries.append(entry)
            except Exception as err:
                print(f"error: {err}")
                print(traceback.format_exc())
                try:   
                    print("FETCH PDF",pmid)
                    getPaperPDF(pmid)
                    pmids.append(pmid)
                    validEntries.append(entry)
                except Exception as err:
                    print(f"error: {err}")
                    print(traceback.format_exc())
                
        if len(pmids) >= MAX_PAPERS:
            break

    with open(processedVDBFile, 'w') as newFile:
        json.dump(validEntries, newFile, indent=4)

    import random
    random.seed(1)
    random.shuffle(pmids)

    #pmids = pmids[:300]
    
    print(pmids)
    for pmid in pmids:
        status = StatusHandler(pmid)
        if not status.isPaperConverted():
            try:
                mergeSections(pmid)
            except Exception as err:
                print(f"error: {err}")
                print(traceback.format_exc())
                
       
    try:
        workflow(vdbDataFile, resultXLSX, pmids, modelName, textSource)
    except Exception as err:
        print(f"error: {err}")
        print(traceback.format_exc())
