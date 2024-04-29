from types import SimpleNamespace
import anthropic
import json
import pickle
import hashlib
import os


#chat_model_engine = "claude-3-opus-20240229"
chat_model_engine = "claude-3-haiku-20240307"

keyfile="api_key.txt"
with open(keyfile, 'r', encoding='utf-8') as file:
    api_key = file.readline().strip()  # Read the first line to get the key

#parameters for the API call
max_tokens = 4000
temperature = 0

api_calls = 0
#setup the API client
client = anthropic.Anthropic(
    api_key=api_key,
)

#loads the previous API response from a file
def load_gpt_text(filename):

    with open(filename, 'rb') as file:
        completions = pickle.load(file)
    return completions

#this is the function that gets the completion text from the API response
def get_completion_text(compObject):
    content =compObject.completions.content
    summary = content[0].text
    return summary

# We are expecting a list, in JSON format
# We try to return it as a string, separated by newlines

def get_completion_list(compObject):
    content = compObject.completions.content
    summary = content[0].text


    try:

        summary = json.loads(summary)
        if type(summary) is dict:
            key0 = list(summary.keys())[0]
            summary = summary[key0]
        if type(summary) is dict:
            key0 = list(summary.keys())[0]
            summary = summary[key0]

        summary = "\n".join(summary)

    except ValueError:
        summary = summary
    return summary


#saves the API response to a file
def save_gpt_text(completions, filename):
    with open(filename, 'wb') as file:
        pickle.dump(completions, file)

    return filename

def getFileName(prompt):
    key = prompt+"_"+chat_model_engine+"_"+str(temperature)+"_"+str(max_tokens)
    encoded = key.encode('utf-8')
    m = hashlib.md5()
    m.update(encoded)
    filename = m.hexdigest()
    return filename

def call_gpt_chat_api(prompt):
    global api_calls

    filename = getFileName(prompt)
#storing the prompt so I can check it later
    prompt_filename = "./prompts/" + filename+".txt"
    with open(prompt_filename, "a", encoding='utf-8') as prompt_file:
        prompt_file.write(prompt)

#if this prompt has been called before, load the response from a file
    filename = "./cache/" + filename
    if os.path.exists(filename):
        completions = load_gpt_text(filename)

    else:

        if api_calls ==0:
            print("API CALLED")
        else:
            print(".",end="")
        api_calls = api_calls+1

    #calls the API
        completions = client.messages.create(
            model=chat_model_engine,
            messages= [{"role":"user","content":prompt},],
            max_tokens=max_tokens,
            temperature=temperature,

        )
        save_gpt_text(completions,filename)

# this gives a consistent way to retrieve the text from the completions object


    result = SimpleNamespace()
    result.completions = completions

    result.get_completion_text = get_completion_text
    result.get_completion_list = get_completion_list

    return result


#if main call the function
if __name__ == "__main__":

    prompt = "What is the meaning of life?"
    result = call_gpt_chat_api(prompt)

    result_text = result.get_completion_text(result)
    print(result_text)