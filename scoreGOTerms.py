import json
import sys
from utils.handlers import StatusHandler
from GOntoSim import GOntoSim
from goatools.base import get_godag
<<<<<<< Updated upstream
=======
import traceback
>>>>>>> Stashed changes

validEvidence = ["IBA","ISO","IDA","IMP","ISS","TAS","IPI","HDA","IGI","NAS","EXP","IEP","ISA","ISM","RCA","HMP","IGC","HEP","HGI","NR","IRD","IMR","IKR"]

preloadData = {}



<<<<<<< Updated upstream
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

=======
def setupscoreGOTerms(data_file):
    with open(data_file, 'r') as file:
        vdbData = json.load(file)

    annotated = {}
    for paper in vdbData:
        for species in paper["species"]:
            for gene in species["genes"]:
                geneid = gene["VEuPAthDB_ID"]
                if geneid not in annotated:
                    annotated[geneid] = []
                for go in gene["GO_terms"]:
                    if go["evidence_code"] in validEvidence:
                        annotated[geneid].append(go["GO_ID"])
                        
    for gene in annotated:
        annotated[gene] = list(set(annotated[gene]))
    

    
    preloadData['vdbData'] = vdbData
    preloadData['annotations'] = annotated
    go = get_godag("../llm_data/go-basic.obo", optional_attrs={'relationship'})
    preloadData['go'] = go


def scoreTermsNew(pmid: str, method: str):
    
    status = StatusHandler(pmid)

    structuredGOTerms = status.getStructuredGOTerms()
    vdbData = preloadData['vdbData']
    
    
    vdbGOTerms = {}
    
    for paper in vdbData:
        
        
        if paper["PMID"] == pmid:
            print("GOT PMID")
        
            for species in paper['species']:
                print("SPEC?",species)
                for gene in species['genes']:
                    geneId = gene["VEuPAthDB_ID"]
                    vdbGOTerms[geneId] = []
                    
                    print("GO GENE?",gene)
                    for go_term in gene['GO_terms']:
                        if go_term["evidence_code"] in validEvidence:
                            vdbGOTerms[geneId].append(go_term['GO_ID'])
                            
    for gene in vdbGOTerms:
        vdbGOTerms[gene] = list(set(vdbGOTerms[gene]))
     
    vdbAll = preloadData['annotations']
    
    #scoring is a) num correct, over threshold
    # false and no annotations
    # false and annotation
    
   
    found = {}
    
    for go in structuredGOTerms:
        geneID  = go["geneID"]
        go_term = go["id"]
        if geneID not in found:
            found[geneID] = []
        found[geneID].append(go_term)
    numCorrect = 0
    numGoMissed = 0
    numGenesFound = 0
    numGenesMissed = 0
    numGenesFP = 0
    
    THRESHOLD = 0.6
    
    positives = found.copy()
    
    print("POS",positives)
    
    for gene in found:
        if gene not in vdbGOTerms:
             numGenesFP += 1
    
    for gene in vdbGOTerms:

        if gene in found:
            numGenesFound += 1
            for go_term in vdbGOTerms[gene]:
                print(go_term)
                best = 0
                best_term = go_term
                for fgt in found[gene]:
                    
                    score = getGoScore(go_term,fgt,method)
    
                    if score > best:
                        best = score
                        best_term = fgt
                    
                if best > THRESHOLD:
                    numCorrect += 1
                    
    
                    if best_term in positives[gene]:
                        positives[gene].remove(best_term)
                else:
                    numGoMissed += 1
    
  
        else:
            numGenesMissed += 1
            
            
    
    #now count false positivs
    false_positives = 0
    maybe_positives = 0
    for gene in positives:
        if gene in vdbGOTerms:  # ignores go terms for genes that were not annotated
            for go in positives[gene]:
                best = 0
                for go_term in vdbAll[gene]:
                    
                    score = getGoScore(go_term,go,method)
                    if score > best:
                        best = score
    
    
                
                if go in vdbAll[gene] or best >  THRESHOLD:
                    maybe_positives += 1
                else:
                    false_positives += 1
                    
    print(numGenesFound,numGenesMissed, " :  numGenesFound    numMissed")
    print(numCorrect,numGoMissed, maybe_positives,false_positives ," :  numCorrect  numGoMissed  maybe_positives false_positives")
 
    goPercent = 0
    if numCorrect + numGoMissed > 0:
        goPercent = numCorrect / (numGoMissed + numCorrect)
    
    results = {"pmid":pmid, "numGenesFound":numGenesFound, "numGenesMissed":numGenesMissed, "numGenesFalse": numGenesFP, "numGOCorrect":numCorrect, "numGOMissed":numGoMissed, "ratioGOFound":goPercent, "numFoundExtra": maybe_positives + false_positives, "numFoundNotAnnotated":maybe_positives}
    
    return results
    
    
    
    #structuredGOTerms are those that have been found - should include a vpdb id
    #vdbGOTerms are all those annotated from this paper 
    #vdbAll are all annotations - so we can check for f.paper
    
def getGoScore(acceptedGOTerm,vdbGOTerm, method):
    go = preloadData['go']
    all_go_terms = [acceptedGOTerm, vdbGOTerm]
    try:
        S_values = [(x, GOntoSim.Semantic_Value(x, go, method)) for x in all_go_terms]
    except Exception as e:
        print("Except",e)
        return 0
    S_values = dict(S_values)
    score = GOntoSim.Similarity_of_Set_of_GOTerms([acceptedGOTerm], [vdbGOTerm], method, S_values)    
    return score

    
    
def scoreGOTerms(pmid: str, method: str, data_file: str):
    status = StatusHandler(pmid)

    if "go" not in preloadData:
        setupscoreGOTerms(data_file)
        

#    if not status.areGOTermDescriptionsValidated():
#        return ValueError("GO term descriptions have not been validated for this paper")

# TO DO - scoring based on species / gene
#  this structure includes species and genes with the go terms

    structuredGOTerms = status.getStructuredGOTerms()
    
   # print("STRUCT=",structuredGOTerms)
    
    
    
    
    
    newStats = {}
    
    
    try:
    
        newStats = scoreTermsNew(pmid, method)
    except Exception as e:
        print(traceback.format_exc())
    
    
    
    
    
>>>>>>> Stashed changes
    validatedGOTerms = status.getAcceptedGOTerms()
    acceptedGOTerms = []
    for validatedGOTerm in validatedGOTerms:
        acceptedGOTerms.append(validatedGOTerm['id'])

<<<<<<< Updated upstream
    if "go" not in preloadData:
        setupscoreGOTerms(pmid, method, data_file)
=======
    
>>>>>>> Stashed changes
    vdbData = preloadData['vdbData']
    go = preloadData['go']



    for subData in vdbData:
        if subData['PMID'] == pmid:
            vdbData = subData

    vdbGOTerms = []
<<<<<<< Updated upstream

    for species in vdbData['species']:
        for gene in species['genes']:
            for go_term in gene['GO_terms']:
                if go_term["evidence_code"] in validEvidence:
                    vdbGOTerms.append(go_term['GO_ID'])
       
=======
    if 'species' in vdbData:
        for species in vdbData['species']:
            for gene in species['genes']:
                for go_term in gene['GO_terms']:
                    if go_term["evidence_code"] in validEvidence:
                        vdbGOTerms.append(go_term['GO_ID'])
           
>>>>>>> Stashed changes
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
    
<<<<<<< Updated upstream
    
    if count > 0:
        score = sum(scores[:top_scores]) 
    status.updateField("scoreGOTerms", {
        "success": True,
        "score": paperScores,
=======
    print("SAVE score",count)
    if count > 0:
        score = sum(scores[:top_scores]) 
        status.updateField("scoreGOTerms", {
        "success": True,
        "score": paperScores,
        "stats": newStats
>>>>>>> Stashed changes
    })
    return   paperScores


if __name__ == "__main__":
<<<<<<< Updated upstream
    if len(sys.argv) != 4:
        print("Usage: python scoreGOTerms <pmid> <method> <data_file>")
        sys.exit(1)

    pmid = sys.argv[1]
    method = sys.argv[2]
    data_file = sys.argv[3]

=======
    if len(sys.argv) < 2:
        print("Usage: python scoreGOTerms <pmid> [method data_file]")
        sys.exit(1)

    
    pmid = sys.argv[1]
    method="wang"
    import os
    data_file = str(os.getenv("VDB_DATA_FILE_PATH"))
    
    if len(sys.argv) > 2:
        method = sys.argv[2]
    if len(sys.argv) > 3:        
        data_file = sys.argv[3]
    
    
    
>>>>>>> Stashed changes
    try:
        score = scoreGOTerms(pmid, method, data_file)
        print(f"Score of PMID {pmid} is: {score}")
    except Exception as err:
        print(f"Error getting summary from paper: {err}")
