import json
import os
import pandas as pd
import time
from utils.handlers import StatusHandler
from getPaperJSON import getPaperJSON
from getTextFromJSON import mergeSections
from getPaperSummary import getPaperSummary
from getPaperSpecies import getPaperSpecies
from getPaperGenes import getPaperGenes
from getPaperGOTerms import getPaperGOTerms
from validateGOTermDescriptions import validateGOTermDescriptions
from scoreGOTerms import scoreGOTerms


def workflow(vdbDataFile, resultXLSX, pmids, modelName, textSource):
    summaryTable = {'Model': [modelName], 'Average Score': [0]}
    for i, pmid in enumerate(pmids, start=1):
        status = StatusHandler(pmid)
        print(f"---------\nStart PMID: {pmid}'s Workflow")
        if not status.isSummaryFetched():
            time.sleep(30)
            getPaperSummary(pmid)
        if not status.areSpeciesFetched():
            time.sleep(30)
            getPaperSpecies(pmid, textSource)
        if not status.areGenesFetched():
            time.sleep(30)
            getPaperGenes(pmid, textSource)
        if not status.areGOTermsFetched():
            time.sleep(30)
            getPaperGOTerms(pmid, textSource)
        if not status.areGOTermDescriptionsValidated():
            validateGOTermDescriptions(pmid)

        averageScore = 0
        try:
            averageScore = scoreGOTerms(pmid, 'wang', vdbDataFile)
            print(f"PMID {pmid}'s average score is {averageScore}")
            print(f"End PMID: {pmid}'s Workflow")

        except Exception as err:
            if "\'NoneType\' object is not iterable" not in str(err):
                print(f"error: {err}")
        try:
            summaryTable[pmid] = [averageScore]
        except Exception as err:
            print(f"error: {err}")

    summaryTable['Average Score'] = [sum(summaryTable[pmid][0] for pmid in pmids) / len(pmids)]

    try:
        df = pd.DataFrame(summaryTable)
        df.to_excel(resultXLSX, index=False)
    except Exception as err:
        print(f"error: {err}")


if __name__ == "__main__":
    # VDB data file name
    vdbDataFile = str(os.getenv("VDB_DATA_FILE_PATH"))
    # processed data from VDB
    processedVDBFile = './caches/result/filtered_PMID_data.json'
    # result score file
    resultXLSX = "./caches/result/table_data.xlsx"
    # test model name
    modelName = 'Claude3-haiku'
    # specify text source
    textSource = "summary"

    with open(vdbDataFile, 'r') as file:
        vdbData = json.load(file)
    validEntries = []
    pmids = []
    badpmids = ['16507167', '18551176|24043620', '30102371', '37130129', '37192974', '27602946', '24090929', '28806784']
    for entry in vdbData:
        pmid = entry.get("PMID")
        if pmid in badpmids:
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
        if len(pmids) == 100:
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
    try:
        workflow(vdbDataFile, resultXLSX, pmids, modelName, textSource)
    except Exception as err:
        print(f"error: {err}")
