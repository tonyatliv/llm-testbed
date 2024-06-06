from ..interfaces import LLMInterface
from anthropic import Anthropic, APIConnectionError, RateLimitError, APITimeoutError
from typing import List
from utils.models import Message

class ClaudeAdapter(LLMInterface):
    
    def __init__(self, model: str, systemPrompt: str, messageHistory: List[Message]):
        if not self.__validateMessageHistory(messageHistory):
            raise ValueError("Message history not in correct format for this model")
            
        super().__init__(
            model,
            systemPrompt,
            messageHistory,
            exceptionsForRetry = [APIConnectionError, RateLimitError, APITimeoutError]
        )
    
    def ask(self, message: str, textToComplete: str) -> str:
        client = Anthropic()
        
        messageHistory = self.getMessageHistory()
        
        res = client.messages.create(
            model=self.model,
            max_tokens=4096,
            system=self.systemPrompt,
            messages=messageHistory + [
                {
                    "role": "user",
                    "content": message
                },
                {
                    "role": "assistant",
                    "content": textToComplete
                }
            ]
        )
        
        answer = textToComplete + res.content[0].text
        
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