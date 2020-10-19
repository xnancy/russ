import random
import json
import hashlib
from nltk.corpus import stopwords
import psycopg2

ACTIONS1 = ['I want to', 'i want to', 'help me', 'help', 'i need to']
ACTIONS2 = ['bring me to', 'take me to', 'click', 'click on', 'view', 'select', 'select the', 'get', 'show', 'show me', 'take me to', 'go to', 'press', 'open', 'open the']
SCOPE = ['in' , 'of', 'from', 'on']
SITE = ['the page', 'page', 'display', 'website']

SEARCH_ACTIONS2= ['find', 'look for', 'look up', 'search', 'search for', 'search up', 'ask', 'ask about']
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
                datapoint = {"equiv": [el.xid], "exampleId": hashlib.sha256(command.encode('utf-8')).hexdigest(), "phrase": command, "version": "nancy-v1", "webpage": el.website, "xid": el.xid}
                datapoints.append(datapoint)
                f.write(json.dumps(datapoint) + '\n')

    # Generate commands for elements based on substrings / exact text in element
    @staticmethod
    def generate_text_match(el, file_out):
        if el.hidden == True:
            return
        commands = []
        if el.tag == "INPUT":
          sites = SITE + [el.website]
          if "placeholder" in el.attributes:
            text = el.attributes['placeholder'].lower()
            substrings = Templates.get_substrings(text)
            for i in range(NUM_COMMANDS_PER_TEMPLATE):
              commands.append(random.choice(ACTIONS1) + " " + random.choice(SEARCH_ACTIONS2) + " " + text)
              commands.append(random.choice(ACTIONS1) + " " + random.choice(SEARCH_ACTIONS2) + " " + random.choice(substrings))
              commands.append(random.choice(ACTIONS2) + " " + text + " " + random.choice(SCOPE) + " " + random.choice(sites))
          else:
            for i in range(NUM_COMMANDS_PER_TEMPLATE):
              commands.append(random.choice(ACTIONS2) + " " + random.choice(SCOPE) + " " + random.choice(sites))
              commands.append(random.choice(ACTIONS1) + " " + random.choice(ACTIONS2) + " " + random.choice(SCOPE) + " " + random.choice(sites))

        elif (not el.innertext) or (el.innertext == 'None') or (el.innertext == ''):
            return
        else:
          sites = SITE + [el.website]
          text = el.innertext.lower()
          substrings = Templates.get_substrings(text)

          for i in range(NUM_COMMANDS_PER_TEMPLATE):
              commands.append(random.choice(ACTIONS1) + " " + random.choice(ACTIONS2) + " " + text)
          for i in range(NUM_COMMANDS_PER_TEMPLATE):
              commands.append(random.choice(ACTIONS2) + " " + text + " " + random.choice(SCOPE) + " " + random.choice(sites))
          for i in range(NUM_COMMANDS_PER_TEMPLATE):
              commands.append(random.choice(ACTIONS1) + " " + random.choice(ACTIONS2) + " " + random.choice(substrings))
          for i in range(NUM_COMMANDS_PER_TEMPLATE):
              commands.append(random.choice(ACTIONS2) + " " + random.choice(substrings) + " " + random.choice(SCOPE) + " " + random.choice(sites))

        Templates.write_commands(commands, el, file_out)

    # Generate substrings from text
    @staticmethod
    def get_substrings(text):
        if len(text.split()) == 0:
            print(text)
            return [text] * NUM_SUBSTRINGS
        # Generate commands
        substrings = []
        while (len(substrings) < NUM_SUBSTRINGS):
            a = random.randint(0, len(text.split()) - 1)
            b = random.randint(0, len(text.split()) - 1)
            start = min(a,b)
            end = max(a,b) + 1
            substring_list = text.split()[start:end]
            if substring_list[-1] not in STOPWORDS:
                substrings.append(' '.join(substring_list).lower())
            else:
              substrings.append(text)
        return substrings
