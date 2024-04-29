import sys
import os
import json

from urllib.request import urlretrieve


def parseJson(pmid,jsonfile):

    # Put the results in a dictionary
    # to save as json
    # allows access to individual sections

    data = []
    with open(jsonfile, 'r') as jsontext:
        data = json.load(jsontext)

    out_data = {}
    out_data['pmid'] = pmid

    sections = {}
    section_list = ["abstract","title","intro","results","discussion","methods"]

    for section in section_list:
        sections[section] = ""

    #


    for p in data:
        docs = p['documents']
        for doc in docs:
            #print("Doc",doc)
            passages = doc['passages']
            for passage in passages:

                x = passage['text']
                info = passage['infons']
                type = info['type']
                section_type = info['section_type']

                section_type = section_type.lower()
                if section_type in section_list:
                        sections[section_type] = sections[section_type] + x



    out_data['sections'] = sections

    return out_data



def getPaperJson(pmid):
    outfile = "pdfs/" + str(pmid) + ".json"
    print("Check file exists? ", outfile)
    if os.path.exists(outfile):
        return outfile

    try:

        url = "https://www.ncbi.nlm.nih.gov/research/bionlp/RESTful/pmcoa.cgi/BioC_json/"+str(pmid)+"/unicode"

        if url is None:
            print("No paper URL found.")
            return None

        print("URL", url)
        urlretrieve(url, outfile)

        if os.path.exists(outfile) == False:
            print("Was not downloaded")
            return None

        return outfile
    except Exception as e:
        print("URL Error", e)
        return None


if __name__ == "__main__":
    pmid = sys.argv[1]
    paper = getPaperJson(pmid)
    if paper is not None:
        print("Paper downloaded to: ", paper)
        data = parseJson(pmid,paper)
        data_json = json.dumps(data, ensure_ascii=True, indent = 4)
        print(data_json)

        