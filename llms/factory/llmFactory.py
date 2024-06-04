from utils.handlers import ConfigHandler
from ..adapters import ClaudeAdapter
from typing import List
from utils.models import Message

class LLMFactory:
    
    @staticmethod
    def createLLM(systemPrompt: str, messageHistory: List[Message]):
        config = ConfigHandler()
        modelType = config.getLLMType()
        model = config.getLLM()
        
        match modelType:
            case "claude":
                return ClaudeAdapter(model, systemPrompt, messageHistory)
            case _:
                raise ValueError("LLM type set in confing not foud")