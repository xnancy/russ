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
    def write_commands(commands, el ):
        con = psycopg2.connect(user="lxcgasgqutnxqf",
                                        password="4e136676c0b826659e6b00bd1e5fac2bce004d853d324b2083638cd71c321d43",
                                        host="ec2-54-156-53-71.compute-1.amazonaws.com",
                                        port="5432",
                                        database="d3nialk4215ojk")
        for command in commands:
            # datapoint = {"equiv": [el.xid.item()], "exampleId": hashlib.sha256(command.encode('utf-8')).hexdigest(), "phrase": command, "version": "nancy-v1", "webpage": el.website, "xid": el.xid.item()}
            # datapoints.append(datapoint)
            cur = con.cursor()
            row = ([el.xid.item()], hashlib.sha256(command.encode('utf-8')).hexdigest(), command, "nancy-v1", el.website, el.xid.item(), 6)
            a = "shell_dot_com_synthetic_elements"
            sql = "INSERT INTO " + a + "(equiv, exampleid, phrase, version, webpage, xid, id_website) VALUES(%s, %s, %s, %s, %s, %s, %s) RETURNING element_id;"
            cur.execute(sql, (row))
            element_id = cur.fetchone()[0]
            print(element_id)
            cur.close()
            con.commit()
        con.close()

    # Generate commands for elements based on substrings / exact text in element
    @staticmethod
    def generate_text_match(el, file_out):
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
              ommands.append(random.choice(ACTIONS1) + " " + random.choice(ACTIONS2) + " " + random.choice(SCOPE) + " " + random.choice(sites))
          print(commands)

        elif (el.hidden == True) or (not el.innertext) or (el.innertext == 'None') or (el.innertext == ''):
            return
        else:# Generate commands

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

        Templates.write_commands(commands, el)

    # Generate substrings from text
    @staticmethod
    def get_substrings(text):
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
