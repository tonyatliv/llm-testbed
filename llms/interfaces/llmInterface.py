from abc import ABC, abstractmethod
from typing import List
from utils.models import Message
import time

class LLMInterface(ABC):
    
    def __init__(self, model: str, systemPrompt: str, messageHistory: List[Message], exceptionsForRetry: List[Exception]=[]):
        self.model = model
        self.systemPrompt = systemPrompt
        self.__messageHistory = messageHistory
        self.__exceptionForRetry = exceptionsForRetry
        
    # Abstract methods
    
    @abstractmethod
    def ask(self, message: str, textToComplete: str) -> str:
        pass
    
    
    # Common methods
    
    def askWithRetry(self, messageContent: str, textToComplete=""):
        retryIntervals = [2**i for i in range(0,5)]
        
        for interval in retryIntervals:
            try:
                return self.ask(messageContent, textToComplete=textToComplete)
            except tuple(self.__exceptionForRetry) as err:
                print(f"API call failed: {err}\nRetrying in {interval} seconds")
                time.sleep(interval)
                print("Retrying...")

        raise Exception("All attempts failed")
    
    
    # Getters and setters
    
    def getMessageHistory(self):
        return self.__messageHistory
    
    def setMessageHistory(self, messageHistory: List[Message]):
        self.__messageHistory = messageHistory
        