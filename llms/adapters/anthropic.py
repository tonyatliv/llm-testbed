from ..interfaces import LLMInterface
from anthropic import Anthropic, APIConnectionError, RateLimitError, APITimeoutError
from typing import List
from utils.models import Message
import hashlib
import json


class AnthropicAdapter(LLMInterface):
    
    def __init__(self, model: str, systemPrompt: str, messageHistory: List[Message], cache: bool):
        if not self.__validateMessageHistory(messageHistory):
            raise ValueError("Message history not in correct format for this model")

        self.cache = cache    
        super().__init__(
            model,
            systemPrompt,
            messageHistory,
            exceptionsForRetry = [APIConnectionError, RateLimitError, APITimeoutError]
        )
    
    def ask(self, message: str, textToComplete: str) -> str:
        client = Anthropic()
        

        messageHistory = self.getMessageHistory()
        
        systemPrompt =[]

        if len(self.systemPrompt) > 2:
            systemPrompt =[
                {
                    "type": "text",
                    "text": self.systemPrompt,
                   }
            ]
            if self.cache:
                systemPrompt[0]["cache_control"] =  {"type": "ephemeral"}
               

        key = "prompt-caching-2024-07-31" + str(messageHistory) + str(textToComplete) + str(message) + str(self.systemPrompt)    + str(self.model)
        #check if the response is in the cache
        cachedResponse = self.checkCache(key)
        if cachedResponse:
            return cachedResponse


<<<<<<< Updated upstream
=======
        print("*",end="")
>>>>>>> Stashed changes
        res = client.messages.create(
            model=self.model,
            max_tokens=4096,
            system=systemPrompt,
            messages=messageHistory + [
                {
                    "role": "user",
                    "content": message
                },
                {
                    "role": "assistant",
                    "content": textToComplete
                }
            ],
               extra_headers={"anthropic-beta": "prompt-caching-2024-07-31"}

        )
        
        answer = textToComplete + res.content[0].text

        #save the response in the cache
        self.saveCache(key,answer)

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