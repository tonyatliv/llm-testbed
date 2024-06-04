from llms import LLMHandler

s = LLMHandler(messageHistory=[{"role": "user", "content": "My name jamal"}, {
    "role": "assistant", "content": "hi jamal"
}])

print("I most definitely know that" + s.askWithRetry("what is my name", textToComplete="I most definitely know that"))

print(s.ask("summarise every message of this conversation so far please"))