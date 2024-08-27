from utils.handlers import ConfigHandler
from ..adapters import *
from typing import List
from utils.models import Message

class LLMFactory:
    
    @staticmethod
    def createLLM(systemPrompt: str, messageHistory: List[Message]):
        config = ConfigHandler()
        modelType = config.getLLMType()
        model = config.getLLM()
        
        match modelType:
            case "anthropic":
                return AnthropicAdapter(model, systemPrompt, messageHistory)
            case "openai":
                return OpenAIAdapter(model, systemPrompt, messageHistory)
            case "local":
                return localLLMAdapter(model, systemPrompt, messageHistory)
            case "quantisedLocal":
                return quantisedLocalLLMAdapter(model, systemPrompt, messageHistory)
            case _:
                raise ValueError("Model type not supported")
