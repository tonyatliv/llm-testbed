from ..interfaces import LLMInterface
from anthropic import Anthropic, APIConnectionError, RateLimitError, APITimeoutError
from openai import OpenAI
from typing import List
from utils.models import Message

class OpenAIAdapter(LLMInterface):
    
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
        client = OpenAI()
        
        messageHistory = self.getMessageHistory()
        
        res = client.chat.completions.create(
            model=self.model,
            max_tokens=4096,
            messages=[
                {
                    "role": "system",
                    "content": self.systemPrompt
                }
            ] + messageHistory + [
                {
                    "role": "user",
                    "content": f"{message}\n\n**Your response MUST start with AND complete the following text: {textToComplete}"
                },
                # {
                #     "role": "assistant",
                #     "content": textToComplete
                # }
            ]
        )
        
        answer = res.choices[0].message.content
        
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