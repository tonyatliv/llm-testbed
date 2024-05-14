from typing import List
import time

class LLMInstance:
    __messageHistory: List = []
    
    def __init__(self, messageHistory: List=[]):
        self.__messageHistory = messageHistory
        
    def getMessageHistory(self):
        return self.__messageHistory
        
    def setMessageHistory(self, newMessageHistory: List):
        self.__messageHistory = newMessageHistory
        
    def ask():
        raise Exception("Cannot use class LLMInstance on its own. Model-specific classes like ClaudeInstance should be used instead.")
    
    def askWithRetry(self, messageContent: str, retryExceptions: List[Exception]):
        retryIntervals = [2**i for i in range(0,5)]
        
        for interval in retryIntervals:
            try:
                return self.ask(messageContent)
            except tuple(retryExceptions) as err:
                print(f"API call failed: {err}\nRetrying in {interval} seconds")
                time.sleep(interval)
                print("Retrying...")
                
        raise Exception("All attempts failed")