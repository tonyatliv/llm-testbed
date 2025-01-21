import json
import os
import pandas as pd
import time
import traceback
import sys
from utils.handlers import StatusHandler, ConfigHandler
from getPaperJSON import getPaperJSON
from getTextFromJSON import mergeSections
from getPaperSummary import getPaperSummary
from getPaperSpecies import getPaperSpecies
from getPaperGenes import getPaperGenes
from getPaperGOTerms import getPaperGOTerms
from getQuotes import getQuotes, loadQuotes, putQuotes

from validateGOTermDescriptions import validateGOTermDescriptions
from scoreGOTerms import scoreGOTerms

MAX_PAPERS = 91250
FORCE_UPDATE = True



def workflow(vdbDataFile, resultXLSX, pmids, modelName, textSource):
    summaryTable = {'Model': [modelName,"sum","count","penalty","vdbsum","vdbcount"], 'Average Score': [0,0,0,0,0,0]}
    
    if FORCE_UPDATE:
        for i, pmid in enumerate(pmids, start=1):
            status = StatusHandler(pmid)
        
            status.updateField("getSummary", {
            "success": False     })
            
            status.updateField("getPaperGOTerms", {
            "success": False     })
        
            status.updateField("validateGOTermDescriptions", {
            "success": False     })
        
        
    for i, pmid in enumerate(pmids, start=1):
        try:
            status = StatusHandler(pmid)
 
            print(f"---------\nStart PMID: {pmid}'s Workflow")
            getQuotes(pmid,textSource,vdbDataFile)
            loadQuotes(pmid)
            
            continue
            
            if not status.isSummaryFetched():
                time.sleep(.30)
                getPaperSummary(pmid)
            if not status.areSpeciesFetched():
                time.sleep(.30)
                getPaperSpecies(pmid, textSource)
            if not status.areGenesFetched():
                time.sleep(.30)
                getPaperGenes(pmid, textSource)
            if not status.areGOTermsFetched():
                time.sleep(.30)
                getPaperGOTerms(pmid, textSource)
            if not status.areGOTermDescriptionsValidated():
                validateGOTermDescriptions(pmid)
            

            defScores = {"average":0, "sum":0, "count": 0, "penalty":0 , "vdbSum":0, "vbdCount":0}
            paperScores = {"average":0, "sum":0, "count": 0, "penalty":0, "vdbSum":0, "vbdCount":0 }
            averageScore = 0
            try:
                paperScores = scoreGOTerms(pmid, 'wang', vdbDataFile)
                averageScore = paperScores["average"]
                
                print(f"PMID {pmid}'s average score is {averageScore}")
                print(f"End PMID: {pmid}'s Workflow")

            except Exception as err:
                if "\'NoneType\' object is not iterable" not in str(err):
                    print(f"error: {err}")
                    print(traceback.format_exc())
            try:
                if averageScore > 0:
                    summaryTable[pmid] = []
                    for data in defScores:
                        summaryTable[pmid].append(paperScores[data])
            except Exception as err:
                print(f"error: {err}")
                print(traceback.format_exc())
                
        #still do others even if something goes wrong
        except Exception as err:
            print(f"error: {err}")
            print(traceback.format_exc())

    putQuotes()
    
    foundpmids = []
    for pmid in pmids:
        if pmid in summaryTable:
            foundpmids.append(pmid)
    pmids = foundpmids   

    
    summaryTable['Average Score'] = [sum(summaryTable[pmid][0] for pmid in pmids) / len(pmids),0,0,0,sum(summaryTable[pmid][4] for pmid in pmids) / len(pmids),0]
    

    
    print("Average Score:")
    print(summaryTable['Average Score'])
    print("Summary Table:")
    print(summaryTable)

    df = None
    try:
        df = pd.DataFrame(summaryTable)
        df.to_excel(resultXLSX, index=False)
    except Exception as err:
        print(f"error: {err}")
        print(traceback.format_exc())

    print("Summary Table:")
    print(df)


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
    textSource = "plaintext"

    with open(vdbDataFile, 'r') as file:
        vdbData = json.load(file)
    validEntries = []
    pmids = []
    
    
    validEvidence = ["IBA","ISO","IDA","IMP","ISS","TAS","IPI","HDA","IGI","NAS","EXP","IEP","ISA","ISM","RCA","HMP","IGC","HEP","HGI","NR","IRD","IMR","IKR"]
    
                
    for entry in vdbData:
        species_names = [species['name'] for species in entry['species']]
        go_count = 0
        for species in entry["species"]:
             for genes in species["genes"]:
                 for go in genes["GO_terms"]:
                    if go["evidence_code"] in validEvidence:
                        go_count = go_count + 1
 
        if go_count < 1:
            continue
#        if config.getSpecifiedSpecies() not in species_names:
#            continue

        
        for species in entry["species"]:
             for genes in species["genes"]:
                removeGO = []
                for go in genes["GO_terms"]:
                    if go["evidence_code"] in validEvidence:
                        print("ok")
                    else:
                        print("NOT OK",go)
                        removeGO.append(go)
#                        print(entry["species"][species])
#                        exit(1)
                
                
                        
                        
        pmid = entry.get("PMID")
        print("check pmid",pmid)
        if len(pmid) > 12:
            continue
        status = StatusHandler(pmid)
        if status.isJSONFetched():
            pmids.append(pmid)
            validEntries.append(entry)
        else:
            try:
                getPaperJSON(pmid)
                pmids.append(pmid)
                validEntries.append(entry)
            except Exception as err:
                print(f"error: {err}")
                print(traceback.format_exc())
        if len(pmids) >= MAX_PAPERS:
            break

    with open(processedVDBFile, 'w') as newFile:
        json.dump(validEntries, newFile, indent=4)

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
