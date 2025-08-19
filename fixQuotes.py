import json
filename = 'go_terms.json'

with open(filename, 'r') as file:
    go_data = json.load(file)
    
filename = 'all_quotes.json'

with open(filename, 'r') as file:
    quote_data = json.load(file)
    
new_quotes = []
for q in quote_data:
    go = q[0]
    quote = q[1]
    goTermData = go_data[go]
    goDesc = goTermData["definition"]
    
    nq = [go,quote,goDesc]
    new_quotes.append(nq)
filename = 'all_quotes_new.json'
with open(filename, 'w') as f:
    json.dump(new_quotes, f, indent=4)
