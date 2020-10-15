import random 
import json
import hashlib 
from nltk.corpus import stopwords

ACTIONS1 = ['I want to ', 'i want to ', 'help me ', 'help ', 'i need to ']
ACTIONS2 = ['bring me to ', 'take me to ', 'click ', 'click on ', 'view ', 'select ', 'select the ', 'get ', 'show ', 'show me ', 'take me to ', 'go to ', 'press ', 'open ', 'open the ']
SCOPE = ['in' , 'of ', 'from ', 'on ']
SITE = ['the page', 'page', 'display', 'website'] 
STOPWORDS = set(stopwords.words('english'))
NUM_SUBSTRINGS = 5 
NUM_COMMANDS_PER_TEMPLATE = 3 


class Templates: 
    # Write a list of string commands for an element to JSONL file  
    @staticmethod
    def write_commands(commands, el, file_out ): 
        with open(file_out, mode='a') as f:
            datapoints = [] 
            for command in commands: 
                datapoint = {"equiv": [el.xid.item()], "exampleId": hashlib.sha256(command.encode('utf-8')).hexdigest(), "phrase": command, "version": "nancy-v1", "webpage": el.website, "xid": el.xid.item()} 
                datapoints.append(datapoint)
                f.write(json.dumps(datapoint) + '\n')

    # Generate commands for elements based on substrings / exact text in element
    @staticmethod
    def generate_text_match(el, file_out): 
        if (el.hidden == True) or (not el.innertext) or (el.innertext == 'None') or (el.innertext == ''): 
            return 
        
        # Generate commands 
        commands = [] 
        sites = SITE + [el.website]
        text = el.innertext.lower()
        substrings = Templates.get_substrings(el)

        for i in range(NUM_COMMANDS_PER_TEMPLATE): 
            commands.append(random.choice(ACTIONS1) + random.choice(ACTIONS2) + text) 
        for i in range(NUM_COMMANDS_PER_TEMPLATE): 
            commands.append(random.choice(ACTIONS2) + text + " " + random.choice(SCOPE) + random.choice(SITE))
        for i in range(NUM_COMMANDS_PER_TEMPLATE): 
            commands.append(random.choice(ACTIONS1) + random.choice(ACTIONS2) + random.choice(substrings)) 
        for i in range(NUM_COMMANDS_PER_TEMPLATE): 
            commands.append(random.choice(ACTIONS2) + random.choice(substrings) + " " + random.choice(SCOPE) + random.choice(SITE))

        Templates.write_commands(commands, el, file_out)

    # Generate substrings from text
    @staticmethod
    def get_substrings(el): 
        if (el.hidden == True) or (not el.innertext) or (el.innertext == 'None') or (el.innertext == ''): 
            return 
        
        # Generate commands 
        substrings = [] 
        while (len(substrings) < NUM_SUBSTRINGS): 
            a = random.randint(0, len(el.innertext.split()) - 1)
            b = random.randint(0, len(el.innertext.split()) - 1)
            start = min(a,b)
            end = max(a,b) + 1 
            substring_list = el.innertext.split()[start:end]
            if substring_list[-1] not in STOPWORDS: 
                substrings.append(' '.join(substring_list).lower())

        return substrings