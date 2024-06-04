import sys
from utils.handlers import StatusHandler, ConfigHandler
import jsonschema
import json
from llms import ClaudeInstance

# TODO: Make get paper genes (currently is just copy paste of getPaperSpecies)

def getPaperSpecies(pmid):
    status = StatusHandler(pmid)
    config = ConfigHandler()
    
    if not status.isPaperConverted():
        return ValueError("Paper has not yet been converted to plaintext")
    
    plaintextFilePath = status.getPlaintextFilePath()
    with open(plaintextFilePath) as plaintextFile:
        promptText = plaintextFile.read()
        
    systemPrompt = config.getSystemPromptForGetPaperSpecies()
    
    claude = ClaudeInstance(systemPrompt=systemPrompt)

    response = claude.askWithRetry(promptText, answerStart="{}")
    
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
    
    status.updateField("getPaperSpeices", {
        "success": True,
        "response": fullAnswer
    })
    
    return fullAnswer
    
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python getPaperSpecies.py <pmid>")
        sys.exit(1)
        
    pmid = sys.argv[1]
    
    # try:
    species = getPaperSpecies(pmid)
    print(f"Species for paper with PMID {pmid} is: {species}")
    # except Exception as err:
    #     print(f"Error getting species from paper: {err}")