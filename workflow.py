import json
import pandas as pd
import time
from utils.handlers import StatusHandler
from getPaperPDF import getPaperPDF
from getPaperJSON import getPaperJSON
from getTextFromJSON import mergeSections
from getPaperSpecies import getPaperSpecies
from getPaperGenes import getPaperGenes
from getPaperGOTerms import getPaperGOTerms
from validateGOTermDescriptions import validateGOTermDescriptions
from scoreGOTerms import scoreGOTerms


def getPaperPlainText(pmid: str):
    status = StatusHandler(pmid)

    if status.isJSONFetched() or status.isPDFFetched():
        if status.isPaperConverted():
            return True
        else:
            try:
                path = mergeSections(pmid)
                print(f"PMID {pmid}'s plaintext is stored in {path}")
                return True
            except Exception as err:
                print(f"error: {err}")
                return False

    if not status.isJSONFetched():
        try:
            getPaperJSON(pmid)
            return True
        except Exception as err:
            print(f"error: {err}")

    if not status.isPDFFetched():
        try:
            getPaperPDF(pmid)
            return True
        except Exception as err:
            print(f"error: {err}")
            return False


def workflow(dataFile, resultJSON, resultXLSX, pmidNum, modelName):
    with open(dataFile, 'r') as file:
        data = json.load(file)
    validEntries = []
    pmids = []
    badpmids = ['16507167', '18551176|24043620', '30102371', '37130129', '37192974', '27602946', '24090929', '28806784']
    for entry in data:
        pmid = entry.get("PMID")
        if pmid in badpmids:
            continue
        if pmid:
            if getPaperPlainText(pmid):
                pmids.append(pmid)
                validEntries.append(entry)
                if len(pmids) == pmidNum:
                    break

    with open(resultJSON, 'w') as new_file:
        json.dump(validEntries, new_file, indent=4)

    summaryTable = {'Model': [modelName], 'Average Score': [0]}
    for i, pmid in enumerate(pmids, start=1):
        status = StatusHandler(pmid)
        print(f"---------\nStart PMID: {pmid}'s Workflow")
        if not status.areSpeciesFetched():
            time.sleep(30)
            getPaperSpecies(pmid)
            time.sleep(30)
        if not status.areGenesFetched():
            getPaperGenes(pmid)
            time.sleep(30)
        if not status.areGOTermsFetched():
            getPaperGOTerms(pmid)
            time.sleep(30)
        if not status.areGOTermDescriptionsValidated():
            validateGOTermDescriptions(pmid)
        print(f"End PMID: {pmid}'s Workflow\n---------")

        averageScore = 0
        try:
            print(f"---------Start PMID: {pmid}'s score calculating---------")
            averageScore = scoreGOTerms(pmid, 'wang', dataFile)
            print(f"PMID {pmid}'s average score is {averageScore}")
            print(f"---------End PMID: {pmid}'s score calculating---------")
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
    fileName = 'PFalciparum_3d7_gaf.json'
    # processed data from VDB
    resultJSON = './result/filtered_PMID_data.json'
    # result score file
    resultXLSX = "./result/table_data.xlsx"
    # test model name
    modelName = 'Claude3-haiku'

    try:
        workflow(fileName, resultJSON, resultXLSX, 100, modelName)
    except Exception as err:
        print(f"error: {err}")
