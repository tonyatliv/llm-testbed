import anthropic
from anthropic import Anthropic
from .__llmInstance import LLMInstance
from typing import List, Literal, TypedDict

class ClaudeMessage(TypedDict):
    role: Literal["user", "assistant"]
    content: str

class ClaudeInstance(LLMInstance):
    # The askWithRetry function will retry with the following exceptions
    __RETRYEXCEPTIONS = [anthropic.APIConnectionError, anthropic.RateLimitError, anthropic.APITimeoutError]
    
    __systemPrompt: str
    __model: str
    __maxTokens: int = 4096

    def __init__(self, systemPrompt="", messageHistory: List[ClaudeMessage]=[], model="claude-3-haiku-20240307", maxTokens=4096):
        super().__init__(messageHistory=messageHistory)
        self.__systemPrompt = systemPrompt
        self.__model = model
        self.__maxTokens = maxTokens
        
    def getMessageHistory(self) -> List[ClaudeMessage]:
        return super().getMessageHistory()
    
    def setMessageHistory(self, newMessageHistory: List[ClaudeMessage]):
        return super().setMessageHistory(newMessageHistory)
        
    def ask(self, messageContent: str, answerStart="", messageHistory: List[ClaudeMessage]=None, maxTokens=None):
        if messageHistory is None:
            messageHistory = self.getMessageHistory()
            
        if maxTokens is None:
            maxTokens = self.__maxTokens
        
        client = Anthropic()
        
        response = client.messages.create(
            max_tokens = maxTokens,
            system = self.__systemPrompt,
            messages = messageHistory + [
                {
                    "role": "user",
                    "content": messageContent
                },
                {
                    "role": "assistant",
                    "content": answerStart
                }
            ],
            model=self.__model,
        )
        
        answerText = answerStart + response.content[0].text
        
        self.setMessageHistory(messageHistory + [
            {
                "role": "user",
                "content": messageContent
            },
            {
                "role": "assistant",
                "content": answerText
            }
        ])
        
        return answerText
    
    def askWithRetry(self, messageContent: str):
        return super().askWithRetry(messageContent, self.__RETRYEXCEPTIONS)