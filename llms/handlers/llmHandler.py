from ..factory import LLMFactory
from typing import List
from utils.models import Message

class LLMHandler:
    
    def __init__(self, systemPrompt="", messageHistory: List[Message]=[]):
        self.llm = LLMFactory.createLLM(systemPrompt, messageHistory)
        
    def ask(self, message: str, textToComplete: str="") -> str:
        return self.llm.ask(message, textToComplete)
    
    def askWithRetry(self, message: str, textToComplete: str="") -> str:
        return self.llm.askWithRetry(message, textToComplete)