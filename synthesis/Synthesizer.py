from enum import Enum ,  auto 
import random 
import re
from tqdm import tqdm
import hashlib

class Relative(Enum): 
    above = 'above'
    below = 'below'
    right = 'right'
    left = 'left'

class Location(Enum):
    top_left = 'top_left'
    top_right = 'top_right'
    bottom_left = 'bottom_left'
    bottom_right = 'bottom_right'
    top = 'top'
    bottom = 'bottom'
    left = 'left'
    right = 'right'

class Type(Enum):
    button = 'button'
    link = 'link'
    input_el = 'input'
    checkbox = 'checkbox'
    dropdown = 'dropdown'
    image = 'image'
    icon = 'icon'
    text = 'text'

type_dict = {
    'button': ['button' ,  'selector'] , 
    'link': ['url' ,  'link'] ,  
    'input': ['textbox' ,  'searchbox' ,  'input'] , 
    'checkbox': ['checkbox'] ,  
    'dropdown': ['dropdown' ,  'down arrow'] ,  
    'image': ['image' ,  'picture'] ,  
    'icon': ['icon' ,  'widget'] ,  
    'text': ['text' ,  'content' ,  'section'] , 
    '': ['']
}
class Synthesizer: 
    def __init__(self ,  file_path): 
        self.file = open(file_path ,  'a')

    def close_file(self):
        self.file.close() 
        
    def remove_emoji(self, string): 
        emoji_pattern = re.compile("[" u"\U0001F600-\U0001F64F" u"\U0001F300-\U0001F5FF" u"\U0001F680-\U0001F6FF" u"\U0001F1E0-\U0001F1FF" u"\U00002702-\U000027B0" u"\U000024C2-\U0001F251" "]+", flags=re.UNICODE) 
        return emoji_pattern.sub(r'', string)

    # returns => RETRIEVE(description=descr ,  location = location ,  type=type ,  and relative val = id)
    def element_ref(self ,  descr ,  location = '' ,  type_html = ''):  
        base = "@webagent.retrieve " 
        if descr and descr != " ": 
            base += " param:description = \" " + descr + " \""
        if location:
            base += " param:location = enum:" + location.value 
        if type_html:
            base += " param:type = enum:" + type_html.value 
        return base 

    def get_element_descriptors(self ,  descr = '',  location = '' ,  type_html = ''): 
        options = [] 
        if location and type_html and (not descr or descr == " "): 
            # type location
            options.append(" the " + random.choice(type_dict[type_html.value]) + random.choice([' in ' ,  ' on ']) + random.choice([' the ' ,  ' ']) + location.value.replace("_" ,  " ") + random.choice([' of the page ' ,  ' of the screen ' ,  ' of the website ' ,  '']))
            options.append(" the " + random.choice(type_dict[type_html.value]) + " at the " + location.value.replace("_" ,  " "))
            # location type 
            options.append(" the " + location.value.replace("_" ,  " ") + " " + random.choice(type_dict[type_html.value]) + random.choice([' on the website ' ,  ' on the page ' ,  '']))
        elif location and type_html and descr: 
            # descr type location
            options.append(" the " + descr + " " + random.choice(type_dict[type_html.value]) + random.choice([' at' ,  ' near' ,  ' on']) + " the " + location.value.replace("_" ,  " ")+ random.choice([' of the page ' ,  ' of the screen ' ,  ' of the website ' ,  '']))
            # location descr type 
            options.append(" the " + location.value.replace("_" ,  " ") + " " + descr + " " + random.choice(type_dict[type_html.value]) + random.choice([' on the website ' ,  ' on the page ' ,  '']))
            # location type descr 
            options.append(" the " + location.value.replace("_" ,  " ") + " " + random.choice(type_dict[type_html.value]) + random.choice([' that says ' ,  ' with ' ,  ' containing ']) + descr)
            # type location descr 
            options.append(" the " + location.value.replace("_" ,  " ") + " " + random.choice(type_dict[type_html.value]) + random.choice([' on the website ' ,  ' on the page ' ,  '']) + random.choice([' that says ' ,  ' with ' ,  ' containing ']) + descr)
            # type descr location 
            options.append(" the " + random.choice(type_dict[type_html.value]) + random.choice([' that says ' ,  ' with ' ,  ' about ']) + descr + random.choice([' at ' ,  ' near ' ,  ' on  ']) + " the " + location.value.replace("_" ,  " ")+ random.choice([' of the page ' ,  ' of the screen ' ,  ' of the website ' ,  ' ']))
        elif location and descr: 
            options.append(descr + " " + random.choice([' at ' ,  ' near ' ,  ' on ']) + " the " + location.value.replace("_" ,  " ")+ random.choice([' of the page ' ,  ' of the screen ' ,  ' of the website ' ,  ' ']))
        elif type_html and descr: 
            options.append(" the " + descr + " " + random.choice(type_dict[type_html.value]))
            options.append(" the " + random.choice(type_dict[type_html.value]) + " that says " + descr)
        elif descr: 
            options.append(descr)
        
        return options

    def secondary_action(self ,  actions ,  action_command ,  relative ,  descr ,  location = '' ,  type_html = '' ,  descr_side = '' ,  location_side = '' ,  type_html_side = ''):
        command = "now => ( " + self.element_ref(descr_side ,  location_side ,  type_html_side) + " ) join ( " + self.element_ref(descr ,  location ,  type_html) + " ) on param:"+ relative.value + " = param:id => " + action_command + " on param:element = param:id"
        
        options = [] 
        el_options_side = self.get_element_descriptors(descr_side ,  location_side ,  type_html_side)
        el_options = self.get_element_descriptors(descr ,  location ,  type_html)

        rel_values = []
        if relative.value == ' left ' or relative.value == ' right ': 
            rel_values = [' to the ' + relative.value + ' of ' ,  relative.value + ' of ']
        else: 
            rel_values = [" " + relative.value + " " ]

        for el_option in el_options: 
            for el_option_side in el_options_side: 
                for rel_value in rel_values : 
                    for action in actions: 
                        options.append(rel_value + " " + el_option_side + " ,  " + action + " " + el_option+ "  .")
                        options.append(action + " " + el_option + " " + rel_value + el_option_side+ "  .")

        if location and location_side and location.value == location_side.value: 
            for el_option in self.get_element_descriptors(descr ,  type_html): 
                for el_option_side in self.get_element_descriptors(descr_side ,  type_html_side): 
                    for rel_value in rel_values : 
                        for action in actions: 
                                options.append(random.choice([' At ' ,  ' near ' ,  ' on ']) + " the " + location.value.replace("_" ,  " ")+ random.choice([' of the page ' ,  ' of the screen ' ,  ' of the website ' ,  ' ']) + " ,  " + action + " " + el_option + " " + rel_value + el_option_side+ "  . ")
                                options.append(random.choice([' At ' ,  ' near ' ,  ' on ']) + " the " + location.value.replace("_" ,  " ")+ random.choice([' of the page ' ,  ' of the screen '  ,  ' of the website ' ,  ' ']) + " ,  " + rel_value + " " + el_option_side + " ,  " + action + " " + el_option+ " . ")

                                options.append(" Go to the " + location.value + " of the page and " + action + " " + el_option + " " + rel_value + el_option_side+ " .")
                                options.append(" Go to the " + location.value + " of the page and " + rel_value + " " + el_option_side + " ,  " + action + " " + el_option+ "  . ")

        option = random.choice(options)
        hash_object = hashlib.sha224(option.lower().encode('utf-8'))
        hex_dig = hash_object.hexdigest()

        self.file.write(hex_dig + "\t")
        option = self.remove_emoji(re.sub(' +' ,  ' ' ,  option.lower()))
        command = self.remove_emoji(re.sub(' +' ,  ' ' ,  command.lower()))
        self.file.write(option + "\t")
        self.file.write(command + "\n")

    # FOR CLICK AND READ 
    def basic_action(self ,  actions ,  action_command ,  descr ,  location = '' ,  type_html = ''):
        command = "now => " + self.element_ref(descr ,  location ,  type_html) + " => " + action_command + " param:element = param:id"
        options = []

        for el_option in self.get_element_descriptors(descr ,  location ,  type_html):
                options.append(random.choice(actions) + " " + el_option+ " .")

        if location: 
            location_options = ["go to the " + location.value + " of the page and " ,  random.choice([' at ' ,  ' near ' ,  ' on ']) + " the " + location.value.replace("_" ,  " ")+ random.choice([' of the page ' ,  ' of the screen ' ,  ' of the website ' ,  ' ']) + " ,  "]
            for location_option in location_options:
                for el_option in self.get_element_descriptors(descr ,  type_html): 
                    options.append(location_option + " " + random.choice(actions) + " " + el_option+ " .")

        option = random.choice(options)
        hash_object = hashlib.sha224(option.lower().encode('utf-8'))
        hex_dig = hash_object.hexdigest()

        self.file.write(hex_dig + "\t")
        option = self.remove_emoji(re.sub(' +' ,  ' ' ,  option.lower()))
        command = self.remove_emoji(re.sub(' +' ,  ' ' ,  command.lower()))
        self.file.write(option + "\t")
        self.file.write(command + "\n")
    
    def goto(self ,  website): 
        command = "now => @webagent.goto param:website =  \"  " + website + "  \" "
        options = [] 
        options.append(" Go to " +website+ " . ")
        options.append(" Navigate to " + website+ " . ")
        options.append(" Redirect to " + website+ " . ")
        options.append(" Go to the website " + website+ " . ")
 
        option = random.choice(options)
        hash_object = hashlib.sha224(option.lower().encode('utf-8'))
        hex_dig = hash_object.hexdigest()

        self.file.write(hex_dig + "\t")
        option = self.remove_emoji(re.sub(' +' ,  ' ' ,  option.lower()))
        command = self.remove_emoji(re.sub(' +' ,  ' ' ,  command.lower()))
        self.file.write(option + "\t")
        self.file.write(command + "\n")
    
    def ask(self ,  text_var): 
        command = "let param:" + re.sub(' +', '_', text_var).lower().strip() + " = ( @webagent.ask param:text =  \"  " + text_var +  "  \" ) "
        options = []
        options.append("Ask the " + random.choice(["user for their " ,  "customer for their " ,  "caller for their "]) + text_var+ " .")
        options.append("Get the " + random.choice(["user's " ,  "customer's " ,  "caller's "]) + text_var+ " .")
        options.append("What is the " + random.choice(["user's " ,  "customer's " ,  "caller's "]) + text_var+ " ? ")

        option = random.choice(options)
        hash_object = hashlib.sha224(option.lower().encode('utf-8'))
        hex_dig = hash_object.hexdigest()

        self.file.write(hex_dig + "\t")
        option = self.remove_emoji(re.sub(' +' ,  ' ' ,  option.lower()))
        command = self.remove_emoji(re.sub(' +' ,  ' ' ,  command.lower()))
        self.file.write(option + "\t")
        self.file.write(command + "\n")

    def enter_basic(self ,  text_var ,  descr ,  location = '' ,  type_html = ''): 
        command = "now => " + self.element_ref(descr ,  location ,  type_html) + " => @webagent.enter" + " param:text =    \" " + text_var + " \"  on param:element = param:id "
        options = [] 
        el_options = self.get_element_descriptors(descr ,  location ,  type_html)
        for el_option in el_options: 
            options.append(random.choice([' Type in ' ,  ' Enter ' ,  ' Give ']) + random.choice(['the ' ,  "the user's " ,  "the customer's " ,  "the caller's "]) + text_var + random.choice([' in ' ,  ' for ']) + el_option+ " .")
            options.append(random.choice([' In ' ,  ' For ']) + el_option + random.choice([' type in ' ,  ' enter ' ,  ' give ']) + random.choice(['the ' ,  "the user's " ,  "the customer's " ,  "the caller's "]) +text_var+ " .")

        option = random.choice(options)
        hash_object = hashlib.sha224(option.lower().encode('utf-8'))
        hex_dig = hash_object.hexdigest()

        self.file.write(hex_dig + "\t")
        option = self.remove_emoji(re.sub(' +' ,  ' ' ,  option.lower()))
        command = self.remove_emoji(re.sub(' +' ,  ' ' ,  command.lower()))
        self.file.write(option + "\t")
        self.file.write(command + "\n")

    def enter_secondary(self ,  text_var ,  relative ,  descr ,  location = '' ,  type_html = '' ,  descr_side = '' ,  location_side = '' ,  type_html_side = ''):
        command = "now => ( " + self.element_ref(descr_side ,  location_side ,  type_html_side) + " ) join ( " + self.element_ref(descr ,  location ,  type_html) + " ) on param:" + relative.value + " = param:id  => @webagent.enter"  + " param:text =   \" " + text_var + "  \"  on param:element = param:id"
        options = [] 
        el_options_side = self.get_element_descriptors(descr_side ,  location_side ,  type_html_side)
        el_options = self.get_element_descriptors(descr ,  location ,  type_html)

        rel_values = []
        if relative.value == ' left ' or relative.value == ' right ': 
            rel_values = [' to the ' + relative.value + ' of' ,  relative.value + ' of ']
        else: 
            rel_values = [" "  + relative.value + " "]

        for el_option in el_options: 
            for el_option_side in el_options_side: 
                for rel_value in rel_values : 
                    options.append(rel_value + " " + el_option_side + " ,  " + random.choice(['type in ' ,  'enter ' ,  'give ']) + random.choice(['the ' ,  "the user's " ,  "the customer's " ,  "the caller's "]) + text_var + random.choice([' in ' ,  ' for ']) + el_option+ " .")
                    options.append(random.choice(['Type in ' ,  'Enter ' ,  'Give ']) + random.choice(['the ' ,  "the user's " ,  "the customer's " ,  "the caller's "]) + text_var + random.choice([' in ' ,  ' for ']) + " " + el_option + " " + rel_value + el_option_side+ " .")

        if location and location_side and location.value == location_side.value: 
            for el_option in self.get_element_descriptors(descr ,  type_html): 
                for el_option_side in self.get_element_descriptors(descr_side ,  type_html_side): 
                    for rel_value in rel_values : 
                        options.append(random.choice([' At' ,  ' Near' ,  ' On']) + " the " + location.value.replace("_" ,  " ")+ random.choice([' of the page' ,  ' of the screen' ,  ' of the website' ,  '']) + " ,  " + random.choice(['type in ' ,  'enter ' ,  'give ']) + random.choice(['the ' ,  "the user's " ,  "the customer's " ,  "the caller's "]) + text_var + random.choice([' in ' ,  ' for ']) + " " + el_option + " " + rel_value + el_option_side+ " .")
                        options.append(random.choice([' At' ,  ' Near' ,  ' On']) + " the " + location.value.replace("_" ,  " ")+ random.choice([' of the page' ,  ' of the screen' ,  ' of the website' ,  '']) + " ,  " + rel_value + " " + el_option_side + " ,  " + random.choice(['type in ' ,  'enter ' ,  'give ']) + random.choice(['the ' ,  "the user's " ,  "the customer's " ,  "the caller's "]) + text_var + random.choice([' in ' ,  ' for ']) + " " + el_option+ " .")

                        options.append("Go to the " + location.value + " of the page and " + random.choice(['type in ' ,  'enter ' ,  'give ']) + random.choice(['the ' ,  "the user's " ,  "the customer's " ,  "the caller's "]) + text_var + random.choice([' in ' ,  ' for ']) + " " + el_option + " " + rel_value + el_option_side+ " .")
                        options.append("Go to the " + location.value + " of the page and " + rel_value + " " + el_option_side + " ,  " + random.choice(['type in ' ,  'enter ' ,  'give ']) + random.choice(['the ' ,  "the user's " ,  "the customer's " ,  "the caller's "]) + text_var + random.choice([' in ' ,  ' for ']) + " " + el_option+ " .")

        option = random.choice(options)
        hash_object = hashlib.sha224(option.lower().encode('utf-8'))
        hex_dig = hash_object.hexdigest()

        self.file.write(hex_dig + "\t")
        option = self.remove_emoji(re.sub(' +' ,  ' ' ,  option.lower()))
        command = self.remove_emoji(re.sub(' +' ,  ' ' ,  command.lower()))
        self.file.write(option + "\t")
        self.file.write(command + "\n")

    def say(self ,  text): 
        command = "now => @webagent.say param:text =  \" " + text + "  \" "
        options = [] 
        options.append(random.choices(['Say ' ,  'Say to the user ' ,  'Say to the caller ' ,  'Say to the customer ' ,  'Tell the user ' ,  'Tell the caller ' ,  'Tell the customer '] ,  weights = (3 ,  1 ,  1 ,  1 ,  1 ,  1 ,  1))[0] + text + " .")

        option = random.choice(options)
        hash_object = hashlib.sha224(option.lower().encode('utf-8'))
        hex_dig = hash_object.hexdigest()

        self.file.write(hex_dig + "\t")
        option = self.remove_emoji(re.sub(' +' ,  ' ' ,  option.lower()))
        command = self.remove_emoji(re.sub(' +' ,  ' ' ,  command.lower()))
        self.file.write(option + "\t")
        self.file.write(command + "\n")
# GOTO('walmart.com')
# let order = ASK('relevant order')
# RETRIEVE('email' ,  tyipe = text box) => ENTER(email_box ,  email)
# RETRIEVE => RETRIEVE => ALL
# SAY('check email and reset password') 

action_click = ['click' ,  'click on' ,  'go to' ,  'select' ,  'choose']
action_command_click = "@webagent.click"

action_read = ['read' ,  'say' ,  'read the content of']
action_command_read = "@webagent.read"

descr_file = open("synth-strings/descriptions.txt" ,  "r")
descriptions = descr_file.readlines()
descriptions = [descr.strip() for descr in descriptions]

website_file = open("synth-strings/websites.txt" ,  "r")
websites = website_file.readlines()
websites = [web.strip() for web in websites]


ask_file = open("synth-strings/ask_var.txt" ,  "r")
asks = ask_file.readlines()
asks = [ask.strip() for ask in asks]

say_file = open("synth-strings/say.txt" ,  "r")
says = say_file.readlines()
says = [say.strip() for say in says]

synth = Synthesizer('synth1M-2.txt')

for i in tqdm(range(1000000)): 
    descr = random.choice(descriptions)
    descr = random.choices([descr ,  ''] ,  weights = (70 , 1))[0].replace(u"\u2122", '')
    website = random.choice(websites)
    location = random.choice(list(Location))
    location = random.choices([location ,  ''] ,  weights = (1 , 2))[0]
    type_html = random.choice(list(Type))
    type_html = random.choices([type_html ,  ''] ,  weights = (1 ,  2))[0]
    relative = random.choice(list(Relative))
    relative = random.choices([relative ,  ''] ,  weights = (1 ,  3))[0]

    if not descr and not (location and type_html): 
        continue 

    if random.uniform(0,1) < 0.3: 
        synth.basic_action(action_read ,  action_command_read ,  descr ,  location = location ,  type_html = type_html)
    if random.uniform(0,1) < 0.3: 
        synth.basic_action(action_click ,  action_command_click ,  descr ,  location = location ,  type_html = type_html)

    ask = random.choice(asks)
    if random.uniform(0,1) < 0.3 and ask: 
        synth.ask(ask)

    say = random.choice(says)
    if random.uniform(0, 1) < 0.3 and say: 
        synth.say(say)
    
    if random.uniform(0,1) < 0.3 and ask: 
        synth.enter_basic(ask ,  descr ,  location = location ,  type_html = type_html)

    if random.uniform(0 ,1)  < 0.3 and website: 
        synth.goto(website)

    if relative: 
        descr_side = random.choice(descriptions)
        descr_side = random.choices([descr_side, ''], weights = (70,1))[0].replace(u"\u2122", '')
        location_side = random.choice(list(Location))
        location_side = random.choices([location ,  ''] ,  weights = (1 , 1))[0]
        type_html_side = random.choice(list(Type))
        type_html_side = random.choices([type_html ,  ''] ,  weights = (1 ,  2))[0]

        if not ((descr or (location and type_html)) and (descr_side or (location_side and type_html_side))): 
            continue 

        if random.uniform(0,1) < 0.3:
            synth.secondary_action(action_read ,  action_command_read ,  relative ,  descr ,  location = location ,  type_html = type_html ,  descr_side = descr_side ,  location_side = location_side ,  type_html_side = type_html_side)
        if random.uniform(0,1) < 0.3 : 
            synth.secondary_action(action_click ,  action_command_click ,  relative ,  descr ,  location = location ,  type_html = type_html ,  descr_side = descr_side ,  location_side = location_side ,  type_html_side = type_html_side)
        if random.uniform(0,1)<0.3 and ask: 
            synth.enter_secondary(ask ,  relative ,  descr ,  location = location ,  type_html = type_html ,  descr_side = descr_side ,  location_side = location_side ,  type_html_side = type_html_side)

"""
synth = Synthesizer('testsynth.txt')
synth.basic_click('hello' ,  location = Location.top_left)
synth.basic_click('hello' ,  location = Location.top_right ,  type_html = Type.input_el)
synth.basic_click('hello' ,  type_html = Type.text)
synth.basic_click('hello')
"""
