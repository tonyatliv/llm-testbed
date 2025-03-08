import json
import sys
from utils.handlers import StatusHandler
from GOntoSim import GOntoSim
from goatools.base import get_godag

def scoreGOTerms(pmid: str, method: str, data_file: str):
    status = StatusHandler(pmid)

    if not status.areGOTermDescriptionsValidated():
        return ValueError("GO term descriptions have not been validated for this paper")

    validatedGOTerms = status.getAcceptedGOTerms()
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
            except Exception:
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

    score = sum(scores) / len(scoreTable)
    status.updateField("scoreGOTerms", {
        "success": True,
        "score": score,
    })
    return score


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python scoreGOTerms <pmid> <method> <data_file>")
        sys.exit(1)

    pmid = sys.argv[1]
    method = sys.argv[2]
    data_file = sys.argv[3]

    try:
        score = scoreGOTerms(pmid, method, data_file)
        print(f"Score of PMID {pmid} is: {score}")
    except Exception as err:
        print(f"Error getting summary from paper: {err}")
