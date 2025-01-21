import json
import sys
from GOntoSim import GOntoSim
from goatools.base import get_godag

validEvidence = ["IBA","ISO","IDA","IMP","ISS","TAS","IPI","HDA","IGI","NAS","EXP","IEP","ISA","ISM","RCA","HMP","IGC","HEP","HGI","NR","IRD","IMR","IKR"]

preloadData = {}
def setupScoreGOTerms():
    go = get_godag("../llm_data/go-basic.obo", optional_attrs={'relationship'})
    preloadData['go'] = go

def scoreGOTerms(g1, g2):
            method = "wang"
            go = preloadData['go']
            all_go_terms = [g1,g2]
            S_values = [(x, GOntoSim.Semantic_Value(x, go, method)) for x in all_go_terms]
            S_values = dict(S_values)
            score = GOntoSim.Similarity_of_Set_of_GOTerms([g1], [g2], method, S_values)
            print(score)

setupScoreGOTerms()

if __name__ == "__main__":
    g1 = "GO:0016428"
    g2 = "GO:0062152"
    if len(sys.argv) > 2:
       g1 = sys.argv[1]
       g2 = sys.argv[2]
    score = scoreGOTerms(g1,g2)
