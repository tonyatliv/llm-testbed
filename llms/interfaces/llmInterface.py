from abc import ABC, abstractmethod
from typing import List
from utils.models import Message
from utils.handlers import ConfigHandler
import time
import hashlib
import json
from utils.handlers.cache import get_cache, put_cache

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
    
    def checkCache(self,key):
    
     #   print("\ncheckCache_keytext=",key)
        cache_result = get_cache(key)
        return cache_result
        
        #hash the key
        key = hashlib.sha256(key.encode()).hexdigest()
        #convert the key to a string
        key = str(key)
        #check if the file exists and get the content
        
        config = ConfigHandler()

    
        cacheFolder = config.getCacheFolderAPI()  
        
        try:
            with open(cacheFolder+"/"+key+".json", "r") as f:

                print(".",end="")
                res = json.load(f)
                return res["content"]
        except FileNotFoundError:
            print("o",end="")
            pass
        return None
    
    def saveCache(self,key,content):
        put_cache(key,content)
        return
        
        #hash the key
        key = hashlib.sha256(key.encode()).hexdigest()
        #convert the key to a string
        key = str(key)
        #save the content
        config = ConfigHandler()

    
        cacheFolder = config.getCacheFolderAPI()  

        with open(cacheFolder+"/"+key+".json", "w") as f:
            json.dump({"content":content},f)


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
        
