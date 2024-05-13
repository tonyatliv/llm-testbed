import sys
from handlers import StatusHandler, ConfigHandler
from anthropic import Anthropic
import jsonschema
import json

def getPaperSpecies(pmid):
    status = StatusHandler(pmid)
    config = ConfigHandler()
    client = Anthropic()
    
    if not status.isPaperConverted():
        return ValueError("Paper has not yet been converted to plaintext")
    
    plaintextFilePath = status.getPlaintextFilePath()
    with open(plaintextFilePath) as plaintextFile:
        promptText = plaintextFile.read()
        
    systemPrompt = config.getSystemPromptForGetPaperSpecies()
    answerStart = "{"
    
    message = client.messages.create(
        max_tokens=1024,
        system=systemPrompt,
        messages=[
            {
                "role": "user",
                "content": promptText
            },
            {
                "role": "assistant",
                "content": answerStart
            }
        ],
        model="claude-3-haiku-20240307",
    )
    
    statusData = status.get()
    answerString = answerStart + message.content[0].text
    
    try:
        fullAnswer = json.loads(answerString)
        schema = config.getResponseSchemaForGetPaperSepcies()
        jsonschema.validate(fullAnswer, schema=schema)
    except Exception as err:
        statusData["getPaperSpecies"] = {
            "success": False,
            "error": f"{err}"
        }
        status.update(statusData)
        raise Exception(err)
    
    statusData["getPaperSpecies"] = {
        "success": True,
        "response": fullAnswer
    }
    status.update(statusData)
    
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