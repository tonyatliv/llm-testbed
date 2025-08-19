<<<<<<< Updated upstream
=======
print("start import")
>>>>>>> Stashed changes
import json
import os
import pandas as pd
import time
import traceback
import sys
<<<<<<< Updated upstream
from utils.handlers import StatusHandler, ConfigHandler
from getPaperJSON import getPaperJSON
from getTextFromJSON import mergeSections
=======

from utils.handlers import StatusHandler, ConfigHandler
from getPaperJSON import getPaperJSON
from getTextFromJSON import mergeSections, getTitleData

>>>>>>> Stashed changes
from getPaperSummary import getPaperSummary
from getPaperSpecies import getPaperSpecies
from getPaperGenes import getPaperGenes
from getPaperGOTerms import getPaperGOTerms
from getQuotes import getQuotes, loadQuotes, putQuotes
<<<<<<< Updated upstream

from validateGOTermDescriptions import validateGOTermDescriptions
from scoreGOTerms import scoreGOTerms

MAX_PAPERS = 50
FORCE_UPDATE = True
TEXTSOURCE = "plaintext"
MIN_TERMS_PER_PAPER = 1
=======
from validateGOTermDescriptions import validateGOTermDescriptions

print("finish local import")
CUTOFF_YEAR = 2015
MIN_ARTICLE_LENGTH = 5000
MAX_PAPERS = 70
SKIP_PAPERS = 0
FORCE_UPDATE = False
TEXTSOURCE = "plaintext"
MIN_TERMS_PER_PAPER = 1
FORCE_PMIDS = False
#FORCE_PMIDS = ["38713739","39690155"]
FORCE_MERGE = True  #creates a simplified json version with sections - not 
>>>>>>> Stashed changes

def workflow(vdbDataFile, resultXLSX, pmids, modelName, textSource):
    summaryTable = {'Model': [modelName,"sum","count","penalty","vdbsum","vdbcount"], 'Average Score': [0,0,0,0,0,0]}
    
<<<<<<< Updated upstream
    if FORCE_UPDATE:
        for i, pmid in enumerate(pmids, start=1):
            status = StatusHandler(pmid)
        
#            status.updateField("getSummary", {
#            "success": False     })
            
            status.updateField("getPaperGOTerms", {
            "success": False     })
        
            status.updateField("validateGOTermDescriptions", {
            "success": False     })
        
        
=======
    
    if FORCE_UPDATE:
        for i, pmid in enumerate(pmids, start=1):
            status = StatusHandler(pmid)

            status.updateField("getSummary", { "success": False     })
        
            status.updateField("getPaperSpecies", {   "success": False     })

            status.updateField("getPaperGenes", {   "success": False     })
                  
            status.updateField("getPaperGOTerms", {   "success": False     })
        
            status.updateField("validateGOTermDescriptions", {     "success": False     })
        
        
    all_stats = []
    
>>>>>>> Stashed changes
    for i, pmid in enumerate(pmids, start=1):
        try:
            status = StatusHandler(pmid)
 
            print(f"---------\nStart PMID: {pmid}'s Workflow")
<<<<<<< Updated upstream
            
            
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
=======

            
            if not status.isSummaryFetched():
                print("GS")
                time.sleep(.30)
                getPaperSummary(pmid)
            if not status.areSpeciesFetched():
                print("GPS")
                time.sleep(.30)
                getPaperSpecies(pmid, textSource)
            if not status.areGenesFetched():
                print("GPG")
                time.sleep(.30)
                getPaperGenes(pmid, textSource)
            if not status.areGOTermsFetched():
                print("GGO")
>>>>>>> Stashed changes
                time.sleep(.30)
                getPaperGOTerms(pmid, textSource)
            if not status.areGOTermDescriptionsValidated():
                validateGOTermDescriptions(pmid)
            

            defScores = {"average":0, "sum":0, "count": 0, "penalty":0 , "vdbSum":0, "vbdCount":0}
            paperScores = {"average":0, "sum":0, "count": 0, "penalty":0, "vdbSum":0, "vbdCount":0 }
            averageScore = 0
            try:
<<<<<<< Updated upstream
                paperScores = scoreGOTerms(pmid, 'wang', vdbDataFile)
                averageScore = paperScores["average"]
                
=======
                from scoreGOTerms import scoreGOTerms
                paperScores = scoreGOTerms(pmid, 'wang', vdbDataFile)
                averageScore = paperScores["average"]
                
                
                stats = status.getGOScoreStats()
                all_stats.append(stats)
                
                
>>>>>>> Stashed changes
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

<<<<<<< Updated upstream
    print("Summary Table:")
    print(df)


if __name__ == "__main__":

=======

    print(all_stats)
    result_stats = resultXLSX+"_stats.xlsx"
    
    try:
        df = pd.DataFrame(all_stats)
        
        
        mean_row = df.mean(numeric_only=True)
        mean_row_df = pd.DataFrame([mean_row])
        mean_row_df["pmid"] = "Average"
        df = pd.concat([df, mean_row_df], ignore_index=True)


        df.to_excel(result_stats, index=False)
    except Exception as err:
        print(f"error: {err}")
        print(traceback.format_exc())


    result_stats = resultXLSX+"_stats.csv"
    
    try:
        df = pd.DataFrame(all_stats)
        
        mean_row = df.mean(numeric_only=True)
        mean_row_df = pd.DataFrame([mean_row])
        mean_row_df["pmid"] = "Average"
        df = pd.concat([df, mean_row_df], ignore_index=True)

        
        df.to_csv(result_stats, index=False)
    except Exception as err:
        print(f"error: {err}")
        print(traceback.format_exc())
        
        
    print("Summary Table:")
    print(df)

def checkSuitable(status, pmid):
    titleData = getTitleData(pmid)
    year = "1900"
    if "year" in titleData:
        year =  titleData["year"]
    else:
        print("Year not found, skipping")
    year = int(year)
    if year < CUTOFF_YEAR:
        print("Reject on age", year, CUTOFF_YEAR)
        return False
       
       
    length = titleData["document_length"]
 
    
    if length < MIN_ARTICLE_LENGTH:
        print("Reject on length",  length, MIN_ARTICLE_LENGTH)
        return False
        
        
    return True
           #requires plain text, but we might only have json - now fixed abobve
           
    plaintextFilePath = status.getPlaintextFilePath()
    with open(plaintextFilePath) as plaintextFile:
        plaintext = plaintextFile.read()
    if len(plaintext) < MIN_ARTICLE_LENGTH:
        print("Reject on length",  len(plaintext), MIN_ARTICLE_LENGTH)

        return False
    return True
                

if __name__ == "__main__":

    print("start")
>>>>>>> Stashed changes
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
    textSource = TEXTSOURCE

    with open(vdbDataFile, 'r') as file:
        vdbData = json.load(file)
    validEntries = []
<<<<<<< Updated upstream
    pmids = []
=======
>>>>>>> Stashed changes
    
    
    validEvidence = ["IBA","ISO","IDA","IMP","ISS","TAS","IPI","HDA","IGI","NAS","EXP","IEP","ISA","ISM","RCA","HMP","IGC","HEP","HGI","NR","IRD","IMR","IKR"]
    
                
<<<<<<< Updated upstream
    for entry in vdbData:
=======
    pmids= []
    for entry in vdbData[SKIP_PAPERS:]:
>>>>>>> Stashed changes
        species_names = [species['name'] for species in entry['species']]
        go_count = 0
        for species in entry["species"]:
             for genes in species["genes"]:
                 for go in genes["GO_terms"]:
                    if go["evidence_code"] in validEvidence:
                        go_count = go_count + 1
 
<<<<<<< Updated upstream
        if go_count < MIN_TERMS_PER_PAPER:
=======

              
        pmid = entry.get("PMID")
                
        if go_count < MIN_TERMS_PER_PAPER:
            print("Reject",pmid," on num. go terms",MIN_TERMS_PER_PAPER)
>>>>>>> Stashed changes
            continue
#        if config.getSpecifiedSpecies() not in species_names:
#            continue

        
        for species in entry["species"]:
             for genes in species["genes"]:
                removeGO = []
                for go in genes["GO_terms"]:
                    if go["evidence_code"] in validEvidence:
<<<<<<< Updated upstream
                        print("ok")
                    else:
                        print("NOT OK",go)
=======
                        pass
                    else:
                        print("Evidence code NOT OK",go)
>>>>>>> Stashed changes
                        removeGO.append(go)
#                        print(entry["species"][species])
#                        exit(1)
                
                
                        
                        
        pmid = entry.get("PMID")
        print("check pmid",pmid)
<<<<<<< Updated upstream
        if len(pmid) > 12:
            continue
        status = StatusHandler(pmid)
        if status.isJSONFetched():
            pmids.append(pmid)
=======
        
        
        if len(pmid) > 12:
            print("Reject",pmid," on length")
            continue
        status = StatusHandler(pmid)
        
    
        if status.isJSONFetched():
            if checkSuitable(status,pmid):
                pmids.append(pmid)
>>>>>>> Stashed changes
            validEntries.append(entry)
        else:
            try:
                getPaperJSON(pmid)
<<<<<<< Updated upstream
                pmids.append(pmid)
=======
                if checkSuitable(status,pmid):
                    pmids.append(pmid)
>>>>>>> Stashed changes
                validEntries.append(entry)
            except Exception as err:
                print(f"error: {err}")
                print(traceback.format_exc())
        if len(pmids) >= MAX_PAPERS:
            break

    with open(processedVDBFile, 'w') as newFile:
        json.dump(validEntries, newFile, indent=4)
<<<<<<< Updated upstream

    print(pmids)
    for pmid in pmids:
        status = StatusHandler(pmid)
        if not status.isPaperConverted():
=======
    if FORCE_PMIDS:
         pmids = FORCE_PMIDS
    print(pmids)

    
    for pmid in pmids:
        
                
        
    
        if not status.isJSONFetched():
            getPaperJSON(pmid)
            
        if FORCE_MERGE or not status.isPaperConverted():
>>>>>>> Stashed changes
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
