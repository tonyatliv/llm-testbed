import json
import sys
from utils.handlers import StatusHandler
from GOntoSim import GOntoSim
from goatools.base import get_godag

validEvidence = ["IBA","ISO","IDA","IMP","ISS","TAS","IPI","HDA","IGI","NAS","EXP","IEP","ISA","ISM","RCA","HMP","IGC","HEP","HGI","NR","IRD","IMR","IKR"]

preloadData = {}



def setupscoreGOTerms(pmid: str, method: str, data_file: str):
    with open(data_file, 'r') as file:
        vdbData = json.load(file)


    preloadData['vdbData'] = vdbData
    go = get_godag("../llm_data/go-basic.obo", optional_attrs={'relationship'})
    preloadData['go'] = go

def scoreGOTerms(pmid: str, method: str, data_file: str):
    status = StatusHandler(pmid)

    if not status.areGOTermDescriptionsValidated():
        return ValueError("GO term descriptions have not been validated for this paper")

    validatedGOTerms = status.getAcceptedGOTerms()
    acceptedGOTerms = []
    for validatedGOTerm in validatedGOTerms:
        acceptedGOTerms.append(validatedGOTerm['id'])

    if "go" not in preloadData:
        setupscoreGOTerms(pmid, method, data_file)
    vdbData = preloadData['vdbData']
    go = preloadData['go']



    for subData in vdbData:
        if subData['PMID'] == pmid:
            vdbData = subData

    vdbGOTerms = []

    for species in vdbData['species']:
        for gene in species['genes']:
            for go_term in gene['GO_terms']:
                if go_term["evidence_code"] in validEvidence:
                    vdbGOTerms.append(go_term['GO_ID'])
       
    vdbGOTerms = list(set(vdbGOTerms))
    diff = (len(vdbGOTerms)-len(acceptedGOTerms))


    scoreTable = []
    scoreTableV = []
    scores = []
    scoresV = []
    if True:
      for vdbGOTerm in vdbGOTerms:
        maxScore = 0
        mostSimilarVDBGOTerm = ''
        for acceptedGOTerm in acceptedGOTerms:
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
            scoresV.append(maxScore)
            scoreTableV.append({"GO term": acceptedGOTerm, "vdb": mostSimilarVDBGOTerm, "score": maxScore})
    
    vdbGOTerms.append("GO:0008150")
    vdbGOTerms.append("GO:0003674")
    vdbGOTerms.append("GO:0005575")
    
    
    print("SCORING ",acceptedGOTerms)
    if True:
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
 
    scores.sort(reverse=True)
    scoresV.sort(reverse=True)
    
    print("LENGTH DIFF ",diff, len(vdbGOTerms))
    
    print("VPDB:",vdbGOTerms)
    
    
    #if diff < 0:
    #    diff = -diff /10
    
  
    paperScores = {"sum":0, "count": 0, "penalty":0, "average":0,"vdbSum":0,"vbdCount":0}
  
    if len(scoreTable) == 0:
        return paperScores
        
    top_scores = len(scoreTable)
    #if top_scores > len(vdbGOTerms):
    #    top_scores = len(vdbGOTerms)

    count = top_scores
#    count += diff/2
    paperScores["sum"] = sum(scores[:top_scores])
    paperScores["count"] = count
    paperScores["average"] = paperScores["sum"] / count
    paperScores["penalty"] = diff
    
    paperScores["vdbSum"] = sum(scoresV)
    paperScores["vbdCount"] = len(scoresV)
    
    
    if count > 0:
        score = sum(scores[:top_scores]) 
    status.updateField("scoreGOTerms", {
        "success": True,
        "score": paperScores,
    })
    return   paperScores


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
