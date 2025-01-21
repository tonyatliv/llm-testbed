import sys
from utils.handlers import StatusHandler, ConfigHandler
import jsonschema
import json
from llms import LLMHandler

def getPaperGenes(pmid, textSource):
    status = StatusHandler(pmid)
    config = ConfigHandler()
    
    if not status.areSpeciesFetched():
        return ValueError("Species have not yet been fetched for this paper")
    
    if status.areGenesFetched():
        return ValueError("Genes have already been fetched for this paper")
    
    speciesData = status.getSpeciesData()

    if textSource == "plaintext":
        plaintextFilePath = status.getPlaintextFilePath()
        with open(plaintextFilePath) as plaintextFile:
            promptText = plaintextFile.read()
    elif textSource == "summary":
        summaryFilePath = status.getSummaryFilePath()
        with open(summaryFilePath) as summaryFile:
            promptText = summaryFile.read()
        
    systemPrompt = config.getSystemPromptForGetPaperGenes() + json.dumps(speciesData)
    
    model = LLMHandler(systemPrompt=systemPrompt)

    response = model.askWithRetry(promptText, textToComplete="{")
    start = response.find('{')
    end = response.rfind('}') + 1

    if start != -1 and end != -1:
        response = response[start:end]

    try:
        fullAnswer = json.loads(response)
        schema = config.getResponseSchemaForGetPaperGenes()
        jsonschema.validate(fullAnswer, schema=schema)
    except Exception as err:
        status.updateField("getPaperGenes", {
            "success": False,
            "error": f"{err}"
        })
        raise Exception(err)
    
    status.updateField("getPaperGenes", {
        "success": True,
        "response": fullAnswer,
        "messageHistory": model.getMessageHistory()
    })
    
    return fullAnswer
    
if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python getPaperGenes.py <pmid> <isFromPlaintext>")
        sys.exit(1)

    pmid = sys.argv[1]
    textSource = sys.argv[2]

    if textSource not in ["plaintext", "summary"]:
        print("textSource must be either 'plaintext' or 'summary'")
        sys.exit(1)
    
    try:
        genes = getPaperGenes(pmid, textSource)
        print(f"Genes for species of paper with PMID {pmid} cached to status file.")
    except Exception as err:
        print(f"Error getting species from paper: {err}")