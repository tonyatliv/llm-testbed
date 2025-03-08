from ..interfaces import LLMInterface
from typing import List
from transformers import pipeline
from utils.models import Message
import torch

class localLLMAdapter(LLMInterface):

    def __init__(self, model: str, systemPrompt: str, messageHistory: List[Message]):
        if not self.__validateMessageHistory(messageHistory):
            raise ValueError("Message history not in correct format for this model")

        super().__init__(
            model,
            systemPrompt,
            messageHistory,
            exceptionsForRetry=[]
        )

    def ask(self, message: str, textToComplete: str) -> str:
        if torch.cuda.is_available():
            print("Using GPU")
        else:
            print("Using CPU")
        device = 0 if torch.cuda.is_available() else -1
        pipe = pipeline("text-generation", model=self.model, device=device)
        print("model is running on:", pipe.model.device)
        messageHistory = self.getMessageHistory()
        messages = messageHistory + [
            {"role": "system", "content": self.systemPrompt},
            {"role": "user", "content": message},
            {"role": "assistant", "content": textToComplete}
        ]

        assistantResponse = pipe(text_inputs=messages, max_new_tokens=8196)

        answer = assistantResponse[0]["generated_text"][3]["content"]

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