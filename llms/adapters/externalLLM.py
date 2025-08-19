from ..interfaces import LLMInterface
from typing import List

from utils.models import Message
import subprocess
import atexit
import json
import base64

class externalLLMAdapter(LLMInterface):

    def __init__(self, model: str, systemPrompt: str, messageHistory: List[Message]):
        if not self.__validateMessageHistory(messageHistory):
            raise ValueError("Message history not in correct format for this model")

        #start external LLM - may also need to check if it is already running
        #for the current usage, this will not do anything - we need to
        #initiate from a different host
        subprocess.run(['./external/LLM_start.sh'])
        atexit.register(self.exit_handler)
        super().__init__(
            model,
            systemPrompt,
            messageHistory,
            exceptionsForRetry=[]
        )

##destructor to end external LLM
    def exit_handler(self):
        #end external LLM
        result = subprocess.run(['./external/LLM_end.sh'], stdout=subprocess.PIPE)
        answer = result.stdout.decode('utf-8')
        

    def ask(self, message: str, textToComplete: str) -> str:
 
        messageHistory = self.getMessageHistory()

        
        system = self.systemPrompt
        prompt = message
        
        
<<<<<<< Updated upstream
        key = "llama33.1i+prompt-caching-2024-07-31" + str(messageHistory) + str(textToComplete) + str(message) + str(self.systemPrompt)    + str(self.model)
=======
        key = "sonnet+prompt-caching-2025-05-06" + str(messageHistory) + str(textToComplete) + str(message) + str(self.systemPrompt)    + str(self.model)
>>>>>>> Stashed changes
        #key = "sonnet"+key
        
      #  print("ask_keytext=",key)
        #check if the response is in the cache
        cachedResponse = self.checkCache(key)
        if cachedResponse:
            print(".",end="")
            return cachedResponse

        print("o",end="")

#        print("GOT NEW PROMPT", message[:300])
        data = {"prompt": message, "system": self.systemPrompt}

        # Convert the dictionary to a JSON string
        json_string = json.dumps(data)

        # Encode the JSON string to Base64
        base64_encoded = base64.b64encode(json_string.encode('utf-8')).decode('utf-8')
        base64_encoded = str(base64_encoded)

        #call to external shell script
        result = subprocess.run(['./external/LLM_b64.sh',base64_encoded], stdout=subprocess.PIPE)
        
        answer = result.stdout.decode('utf-8')
           #save the response in the cache
        self.saveCache(key,answer)

        return answer
    #not using history - just confuses things
    #beware it's not set for cached answers also - don't reinstate without fixing that
        self.setMessageHistory(messageHistory + [
            {
                "role": "user",
                "content": message
            },
            {
                "role": "assistant",
                "content": answer
            }
        ])
        
        
        return answer

    def __validateMessageHistory(self, messageHistory: List[Message]):
        user = True
        for message in messageHistory:
            if user and message["role"] == "assistant" or not user and message["role"] == "user":
                return False
            user = not user
        return True
