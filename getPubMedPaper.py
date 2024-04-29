import sys
import os
import metapub
from urllib.request import urlretrieve



def getPaper(pmid):
    outfile = "pdfs/" + str(pmid) + ".pdf"
    print("Check file exists? ", outfile)
    if os.path.exists(outfile):
        return outfile

    try:
        url = metapub.FindIt(pmid).url

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
    paper = getPaper(pmid)
    if paper is not None:
        print("Paper downloaded to: ", paper)
        
