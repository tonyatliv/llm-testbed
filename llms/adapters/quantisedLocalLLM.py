import torch
from ..interfaces import LLMInterface
from typing import List
from llama_cpp import Llama
from utils.models import Message


class quantisedLocalLLMAdapter(LLMInterface):

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
        use_gpu = torch.cuda.is_available()
        if use_gpu:
            print("Using GPU")
            gpu_layers = -1
        else:
            print("Using CPU")
            gpu_layers = 0

        model_path = self.model
        if not self.model.lower().endswith(".gguf"):
            model_path = self.model + ".gguf"
        engine = Llama(
            model_path=model_path,
            n_gpu_layers=gpu_layers,
            n_ctx=17048,
        )

        messageHistory = self.getMessageHistory()
        messages = messageHistory + [
            {"role": "system", "content": self.systemPrompt},
            {"role": "user", "content": message},
            {"role": "assistant", "content": textToComplete}
        ]

        assistantResponse = engine.create_chat_completion(messages)
        print(assistantResponse)
        answer = assistantResponse["choices"][0]["message"]["content"]
        print(answer)

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