import sys
from utils.handlers import StatusHandler, ConfigHandler
import jsonschema
import json
from llms import LLMHandler

def getPaperSpecies(pmid):
    status = StatusHandler(pmid)
    config = ConfigHandler()
    
    if not status.isPaperConverted():
        return ValueError("Paper has not yet been converted to plaintext")
    
    if status.areSpeciesFeteched():
        return ValueError("Species have alreade been fetched for this paper")
    
    plaintextFilePath = status.getPlaintextFilePath()
    with open(plaintextFilePath) as plaintextFile:
        promptText = plaintextFile.read()
        
    systemPrompt = config.getSystemPromptForGetPaperSpecies()
    
    model = LLMHandler(systemPrompt=systemPrompt)

    response = model.askWithRetry(promptText, textToComplete="{")
    
    try:
        fullAnswer = json.loads(response)
        schema = config.getResponseSchemaForGetPaperSepcies()
        jsonschema.validate(fullAnswer, schema=schema)
    except Exception as err:
        status.updateField("getPaperSpecies", {
            "success": False,
            "error": f"{err}"
        })
        raise Exception(err)
    
    status.updateField("getPaperSpecies", {
        "success": True,
        "response": fullAnswer,
        "messageHistory": model.getMessageHistory()
    })
    
    return fullAnswer
    
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python getPaperSpecies.py <pmid>")
        sys.exit(1)
        
    pmid = sys.argv[1]
    
    try:
        species = getPaperSpecies(pmid)
        print(f"Species for paper with PMID {pmid} is: {species}")
    except Exception as err:
        print(f"Error getting species from paper: {err}")