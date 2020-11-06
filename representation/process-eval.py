import json 
import hashlib 
import csv       
import re
from SemanticParser import commands_to_webtalk


# Opening JSON file 
f = open('/Users/nancy/Documents/PhD/Multi-Modal/SiteBot/SiteBot/data/eval-rewritten.json') 
f_webtalk = open('/Users/nancy/Documents/PhD/Multi-Modal/SiteBot/SiteBot/data/eval_webtalk.tsv', 'w', newline='\n')
writer_webtalk = csv.writer(f_webtalk, delimiter='\t')
f_instrs = open('/Users/nancy/Documents/PhD/Multi-Modal/SiteBot/SiteBot/data/eval_instructions.tsv', 'w', newline='\n')
writer_instrs = csv.writer(f_instrs, delimiter='\t')

# returns JSON object as  
# a dictionary 
data = json.load(f) 

print(data)

eval_dict = {} 
for website in data['website'].keys(): 
    for instruction_dict in data['website'][website]: 
        search_query = instruction_dict['search_query']
        url = instruction_dict['url']
        instructions = [instr.replace('\t', ' ') for instr in instruction_dict['instructions']]
        new_instructions = [] 
        webtalks = commands_to_webtalk(instructions)
        for i in range(len(instructions)): 
            weblang_hash = hashlib.sha256(instructions[i].replace('\t', ' ').encode('utf-8')).hexdigest()
            element = 0
            dom_path = 'dom_file'
            new_instr = [instructions[i], weblang_hash, element, dom_path] 
            webtalk_row = [str(weblang_hash), instructions[i], webtalks[i]]

            writer_instrs.writerow(new_instr)
            writer_webtalk.writerow(webtalk_row)
# Iterating through the json 
# list 
"""
for i in data['emp_details']: 
    print(i) 
  

"""
# Closing file 
f_webtalk.close()
f.close() 
