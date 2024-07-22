import os
import json
import pandas as pd
import time
from utils.handlers import StatusHandler
from GOntoSim import GOntoSim
from getPaperPDF import getPaperPDF
from getPaperJSON import getPaperJSON
from getTextFromJSON import mergeSections
from getPaperSpecies import getPaperSpecies
from getPaperGenes import getPaperGenes
from getPaperGOTerms import getPaperGOTerms
from validateGOTermDescriptions import validateGOTermDescriptions
from goatools.base import get_godag


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


def getAverageScore(pmid: str, method: str = 'wang', data_file: str = 'test_3d7_gaf.json'):
    status_file = f'./caches/status/{pmid}.json'
    with open(status_file, 'r') as file:
        data = json.load(file)
    validatedGOTerms = data['validateGOTermDescriptions']['acceptedGOTerms']
    acceptedGOTerms = []
    for validatedGOTerm in validatedGOTerms:
        acceptedGOTerms.append(validatedGOTerm['id'])

    with open(data_file, 'r') as file:
        vdbData = json.load(file)
        for subData in vdbData:
            if subData['PMID'] == pmid:
                vdbData = subData

    vdbGOTerms = []

    for species in vdbData['species']:
        for gene in species['genes']:
            for go_term in gene['GO_terms']:
                vdbGOTerms.append(go_term['GO_ID'])

    go = get_godag("go-basic.obo", optional_attrs={'relationship'})
    scoreTable = []
    scores = []
    for acceptedGOTerm in acceptedGOTerms:
        maxScore = 0
        mostSimilarVDBGOTerm = ''
        for vdbGOTerm in vdbGOTerms:
            all_go_terms = [acceptedGOTerm, vdbGOTerm]
            try:
                S_values = [(x, GOntoSim.Semantic_Value(x, go, method)) for x in all_go_terms]
            except Exception as err:
                print(f"error: {err}")
                continue
            S_values = dict(S_values)
            score = GOntoSim.Similarity_of_Set_of_GOTerms([acceptedGOTerm], [vdbGOTerm], method, S_values)
            if score > maxScore:
                maxScore = score
                mostSimilarVDBGOTerm = vdbGOTerm
        if maxScore > 0:
            scores.append(maxScore)
            scoreTable.append({"GO term": acceptedGOTerm, "vdb": mostSimilarVDBGOTerm, "score": maxScore})
    if len(scoreTable) == 0:
        return 0
    for score in scoreTable:
        print(score)
    return sum(scores) / len(scoreTable)


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
            averageScore = getAverageScore(pmid, method='wang', data_file=dataFile)
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
    # original data file name
    fileName = 'PFalciparum_3d7_gaf.json'
    # processed data from original
    resultJSON = './result/filtered_PMID_data.json'
    # result file
    resultXLSX = "./result/table_data.xlsx"
    # test model name
    modelName = 'Claude3-haiku'

    try:
        workflow(fileName, resultJSON, resultXLSX, 100, modelName)
    except Exception as err:
        print(f"error: {err}")
