from sklearn.metrics.pairwise import cosine_similarity as cs
from sentence_transformers import SentenceTransformer
import operator
import json
import numpy as np
import asyncio
import time
from enum import Enum
from WebDriver import WebDriver

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

class Element:
# get the data and compute the additional representations here
    def __init__(self, attrs, embedding_model, body_height, body_width):
        # Features needed for element factors 
        self.tag = ''
        if 'tag' in attrs.keys() and attrs['tag'] is not None:
            self.tag = attrs['tag']
        self.role = False 
        if 'role' in attrs.keys() and attrs['role'] is not None:
            self.role = attrs['role']
        
        self.description = ''
        self.descr_embedding = np.zeros(768)
        if 'text' in attrs.keys():
            self.description = attrs['text']
        if self.description :
            self.descr_embedding = embedding_model.encode([self.description])[0]
       
        # left/right/top/bottom coords used for comparing with other elements 
        # set left/ right /top/botton default to the most extreme so they dont count if no value given 
        self.left = False
        if 'left' in attrs.keys() and attrs['left'] is not None:
            self.left = attrs['left']
        self.right = False
        if 'left' in attrs.keys() and attrs['left'] is not None and 'width' in attrs.keys() and attrs['width'] is not None:
            self.right = float(attrs['left']) + float(attrs['width'])
        
        self.top = False
        if 'top' in attrs.keys() and attrs['top'] is not None:
            self.top = attrs['top']
        self.bottom = False
        if 'top' in attrs.keys() and attrs['top'] is not None and 'height' in attrs.keys() and attrs['height'] is not None:
            self.bottom = float(attrs['top']) + float(attrs['height'])

        self.location = False
        if self.top and self.left: 
            if self.top < body_height / 2 and self.left < body_width/ 2 : 
                self.location = Location.top_left
            elif self.top >= body_height / 2 and self.left < body_width/ 2 : 
                self.location = Location.bottom_left
            elif self.top < body_height / 2 and self.left >= body_width / 2: 
                self.location = Location.top_right
            elif self.top >= body_height / 2 and self.left >= body_width / 2: 
                self.location = Location.bottom_right
        elif self.top and not self.left: 
            if self.top < body_height / 2: 
                self.location = Location.top
            elif self.top >= body_height / 2: 
                self.location = Location.bottom
        elif not self.top and self.left: 
            if self.left < body_width / 2: 
                self.location = Location.left
            elif self.left >= body_width / 2: 
                self.location = Location.right
    
        # Type.dropdown is actually a marker for a list!!! 
        self.html_type = False
        if self.tag: 
            if (self.tag.strip().lower() == "a" or self.tag.strip().lower() == "base" or self.tag.strip().lower() == "link" or self.tag.strip().lower() == "nav"): 
                self.html_type = Type.link
            elif (self.tag.strip().lower() == "abbr" or self.tag.strip().lower() == "acronym" or self.tag.strip().lower() == "address" or self.tag.strip().lower() == "article" or self.tag.strip().lower() == "b" or self.tag.strip().lower() == "blockquote" or self.tag.strip().lower() == "caption" or self.tag.strip().lower() == "cite" or self.tag.strip().lower() == "dd" or self.tag.strip().lower() == "div" or self.tag.strip().lower() == "figcaption" or self.tag.strip().lower() == "label" or self.tag.strip().lower() == "legend" or self.tag.strip().lower() == "p" or self.tag.strip().lower() == "small" or self.tag.strip().lower() == "span" or self.tag.strip().lower() == "strong" or self.tag.strip().lower() == "sub" or self.tag.strip().lower() == "sup" or self.tag.strip().lower() == "title"):
                self.html_type = Type.text
            elif (self.tag.strip().lower() == "area" or self.tag.strip().lower() == "canvas" or self.tag.strip().lower() == "img" or self.tag.strip().lower() == "map" or self.tag.strip().lower() == "picture" or self.tag.strip().lower() == "svg"): 
                self.html_type = Type.image
            elif (self.tag.strip().lower() == "button"): 
                self.html_type = Type.button
            elif (self.tag.strip().lower() == "datalist" or self.tag.strip().lower() == "dl" or self.tag.strip().lower() == "ol" or self.tag.strip().lower() == "select" or self.tag.strip().lower() == "ul"): 
                self.html_type = Type.dropdown
            elif (self.tag.strip().lower() == "input" or self.tag.strip().lower() == "kbd"):
                self.html_type = Type.input_el
        
        if self.role: 
            if (self.role == "button"): 
                self.html_type = Type.button
            elif (self.role == "checkbox" or self.role == "switch" or self.role == "menuitemcheckbox" or self.role == "menuitemradio" or self.role == "option" or self.role== "option"): 
                self.html_type = Type.checkbox
            elif (self.role == "link"): 
                self.html_type = Type.link
            elif (self.role == "searchbox" or self.role =="textbox"):
                self.html_type = Type.input_el
            elif (self.role == "document" or self.role == "heading"): 
                self.html_type = Type.text
            elif (self.role == "figure" or self.role =="img"): 
                self.html_type = Type.image

        
        self.hidden = False
        if 'hidden' in attrs.keys() and attrs['hidden'] is not None:
            self.hidden = attrs['hidden']

        if 'ref' in attrs.keys() and attrs['ref'] is not None:
            self.ref = attrs['ref']
        if 'xid' in attrs.keys() and attrs['xid'] is not None:
            self.xid = attrs['xid']
        if 'selector' in attrs.keys():
            self.selector = attrs['selector']
        
        self.type_raw = ''
        if 'type' in attrs.keys() and attrs['type'] is not None:
            self.type_raw = attrs['type']

        self.class_id = ''
        if 'classes' in attrs.keys() and attrs['classes'] is not None:
            self.class_id  += attrs['classes'].replace('-', ' ').replace('.', ' ').replace('/', ' ').replace(',', ' ').replace('_', ' ')
        if 'id' in attrs.keys() and attrs['id'] is not None:
            self.class_id  += attrs['id'].replace('-', ' ').replace('.', ' ').replace('/', ' ').replace(',', ' ').replace('_', ' ')

        self.attributes = ''
        if 'attributes' in attrs.keys() and attrs['attributes'] is not None:
            for key, value in attrs['attributes'].items():
                if key == 'class':
                    continue
                self.attributes += key.replace('-', ' ').replace('.', ' ').replace('/', ' ').replace(',', ' ').replace('_', ' ')
                self.attributes += value.replace('-', ' ').replace('.', ' ').replace('/', ' ').replace(',', ' ').replace('_', ' ')
    
# variables stored as string with spaces (remove _case) and map to string
class Agent2:
    def __init__(self, webdriver):
        self.webdriver = webdriver
        # stores str and Element values. varname: value 
        self.all_vars = {}
        self.all_vars_embeddings = {} 
        self.embedding_model = SentenceTransformer('distilbert-base-nli-mean-tokens')
        self.dom = ''

    # get variable stored with closest name embedding 
    def getVariable(self, name): 
        
        name_embedding = self.embedding_model.encode([name])[0]
        scores = {} 
        for var_name, var_embedding in self.all_vars_embeddings.items():
            score = cs([name_embedding], [var_embedding])[0][0]
            scores[var_name] = score
        
        best_var_name = max(scores.items(), key=operator.itemgetter(1))[0]
        print('CHOSE THIS VARIABLE: ' + best_var_name + ' FOR ' + name)
        return self.all_vars[best_var_name]

    # filters is a dict of the form {filter: value} ex {'location': 'upperleft'}
    def passFilters(self, element, body_width, body_height, right=False, left=False, above=False, below=False, location=False, html_type=False, tag = '', type_raw=''):
        if right and element.right and (element.right < right.right or (element.right - right.right) / body_width > 0.2): 
            return False 
        if left and element.left and (element.left > left.left or (left.left - element.left) / body_width > 0.2): 
            return False
        if above and element.top and (element.top > above.top or (above.top - element.top) / body_height > 0.2): 
            return False 
        if below and element.bottom and (element.bottom < below.bottom or (element.bottom - below.bottom)  / body_height > 0.2): 
            return False 
        if location and element.location and location.value != element.location.value: 
            return False 
        if html_type and element.html_type and html_type.value != element.html_type.value: 
            return False 
        if type_raw and element.type_raw and type_raw != element.type_raw: 
            return False 
        if tag and element.tag and tag != element.tag: 
            return False 
        return True 

    async def getDOM(self):
        result = await self.webdriver.getDOMInfo()
        return result['info']
 
    def get_params_from_string(self, parsed_string): 
        params = {"description": '', "location": False, "html_type": False}
        if "param:description" in parsed_string: 
            params['description'] = parsed_string.split("param:description")[1].split("\"")[1].strip()
        if "param:text" in parsed_string: 
            params['text_var'] = parsed_string.split("param:text")[1].split("\"")[1].strip()
        if "param:location" in parsed_string: 
            params['location'] = Location(parsed_string.split("param:location")[1].split("enum:")[1].split("=>")[0].strip())
        if "param:type" in parsed_string: 
            params['html_type'] = Type(parsed_string.split("param:type")[1].split("enum:")[1].split("=>")[0].strip())
        return params 

    async def runParsedInstruction(self, parsed_wt):
        print("RUNNING INSTR: " + parsed_wt) 
        enum_dict = {}
        params = self.get_params_from_string(parsed_wt) 
        if parsed_wt.count("@webagent.retrieve") == 0 and parsed_wt.count("@webagent.say") == 1: 
            await self.say(parsed_wt.split("param:text")[-1].replace("\"", " ").replace("=", " ").strip())            
        elif parsed_wt.count("@webagent.retrieve") == 0 and parsed_wt.count("@webagent.ask") == 1: 
            await self.ask(parsed_wt.split("param:text")[-1].replace("\"", " ").replace("=", " ").strip())
        elif parsed_wt.count("@webagent.retrieve") == 0 and parsed_wt.count("@webagent.goto") == 1:
            await self.goto(parsed_wt.split("param:website")[-1].replace("\"", " ").replace("=", " ").strip())
        elif parsed_wt.count("@webagent.retrieve") == 1 and parsed_wt.count("@webagent.read") == 1:     
            await self.read(description = params['description'], location = params['location'], html_type = params['html_type'])
        elif parsed_wt.count("@webagent.retrieve") == 1 and parsed_wt.count("@webagent.click") == 1:     
            await self.click(description = params['description'], location = params['location'], html_type = params['html_type'])
        elif parsed_wt.count("@webagent.retrieve") == 1 and parsed_wt.count("@webagent.enter") == 1:     
            await self.enter(text_var = params['text_var'], description = params['description'], location = params['location'], html_type = params['html_type'])
        
        elif parsed_wt.count("@webagent.retrieve") == 2 and parsed_wt.count("@webagent.read") == 1: 
            first_params = self.get_params_from_string(parsed_wt.split("@webagent.retrieve")[1])  
            second_params = self.get_params_from_string(parsed_wt.split("@webagent.retrieve")[2].split("=>")[0]) 
            first_element = await self.retrieve(description = first_params['description'], location = first_params['location'], html_type = first_params['html_type'])
            first_element = first_element[0]
            if "param:left" in parsed_wt: 
                await self.read(description = second_params['description'], left = first_element, location = second_params['location'], html_type = second_params['html_type'])
            if "param:right" in parsed_wt: 
                await self.read(description = second_params['description'], right = first_element, location = second_params['location'], html_type = second_params['html_type'])
            if "param:above" in parsed_wt: 
                await self.read(description = second_params['description'], above = first_element, location = second_params['location'], html_type = second_params['html_type'])
            if "param:below" in parsed_wt: 
                await self.read(description = second_params['description'], below = first_element, location = second_params['location'], html_type = second_params['html_type'])
            
        elif parsed_wt.count("@webagent.retrieve") == 2 and parsed_wt.count("@webagent.click") == 1:    
            first_params = self.get_params_from_string(parsed_wt.split("@webagent.retrieve")[1])  
            second_params = self.get_params_from_string(parsed_wt.split("@webagent.retrieve")[2].split("=>")[0]) 
            first_element = await self.retrieve(description = first_params['description'], location = first_params['location'], html_type = first_params['html_type'])
            first_element = first_element[0]
            if "param:left" in parsed_wt: 
                self.click(description = second_params['description'], left = first_element, location = second_params['location'], html_type = second_params['html_type'])
            if "param:right" in parsed_wt: 
                self.click(description = second_params['description'], right = first_element, location = second_params['location'], html_type = second_params['html_type'])
            if "param:above" in parsed_wt: 
                self.click(description = second_params['description'], above = first_element, location = second_params['location'], html_type = second_params['html_type'])
            if "param:below" in parsed_wt: 
                self.click(description = second_params['description'], below = first_element, location = second_params['location'], html_type = second_params['html_type']) 
        
        elif parsed_wt.count("@webagent.retrieve") == 2 and parsed_wt.count("@webagent.enter") == 1:     
            first_params = self.get_params_from_string(parsed_wt.split("@webagent.retrieve")[1])  
            second_params = self.get_params_from_string(parsed_wt.split("@webagent.retrieve")[2].split("=>")[0]) 
            first_element = await self.retrieve(description = first_params['description'], location = first_params['location'], html_type = first_params['html_type'])
            first_element = first_element[0]
            if "param:left" in parsed_wt: 
                await self.enter(text_var = second_params['text_var'], description = second_params['description'], left = first_element, location = second_params['location'], html_type = second_params['html_type'])
            if "param:right" in parsed_wt: 
                await self.enter(text_var = second_params['text_var'], description = second_params['description'], right = first_element, location = second_params['location'], html_type = second_params['html_type'])
            if "param:above" in parsed_wt: 
                await self.enter(text_var = second_params['text_var'], description = second_params['description'], above = first_element, location = second_params['location'], html_type = second_params['html_type'])
            if "param:below" in parsed_wt: 
                await self.enter(text_var = second_params['text_var'], description = second_params['description'], below = first_element, location = second_params['location'], html_type = second_params['html_type']) 
        else: 
            print("Error in parse")
        
    async def amazonLogin(self): 
        await self.webdriver.goToPage('https://www.amazon.com/ap/signin?openid.pape.max_auth_age=0&openid.return_to=https%3A%2F%2Fwww.amazon.com%2F%3Fref_%3Dnav_custrec_signin&openid.identity=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.assoc_handle=usflex&openid.mode=checkid_setup&openid.claimed_id=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.ns=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0&')
        await self.webdriver.enter_text('#ap_email', '')
        await self.webdriver.click('#continue')
        await self.webdriver.enter_text('#ap_password', '')
        await self.webdriver.click('#signInSubmit')
        await self.webdriver.page.waitForNavigation()
        # await self.click('Click here to refresh the page', {})

    # TODO: define the remaining functions
    async def click(self, description='', right =False, left=False, above=False, below=False, location=False, html_type=False):
        elements = await self.retrieve(description=description, right=right, left=left,above=above, below=below, location=location, html_type=Type.button)
        element=  elements[0]
        # await self.webdriver.page.waitForNavigation()
        # elem = await self.webdriver.getElementFromXid(selector)
        print("CLICKING SELECTOR: " + str(element.ref))
        await self.webdriver.click(f'[xid="{element.ref}"]')

    # can enter from var of if string_val = True just use the val
    # type = 'text' and tag = 'input' 
    async def enter(self, text_var, description='', right =False, left=False, above=False, below=False, location=False, html_type=False):
        elements = await self.retrieve(description=description, right=right, left=left,above=above, below=below, location=location, html_type=html_type, tag = "INPUT", type_raw = "text")
        element=  elements[0]
        text_input = self.getVariable(text_var)
        await self.webdriver.enter_text(f'[xid="{element.ref}"]', text_input)

    # returns a selector corresponding to var value (basically store selector as var instead of click in CLICK)
    async def ask(self, var):
        val = input("(Alex): What is the " + var +" ? \n")
        self.all_vars[var] = val
        self.all_vars_embeddings[var] = self.embedding_model.encode([val])[0]
         
    def say(self, text):
        print("(Alex): " + text)

    async def goto(self, website): 
        await self.webdriver.goToPage(website)

    async def read(self, description='', right =False, left=False, above=False, below=False, location=False, html_type=False):
        elements = await self.retrieve(description = description, right = right, left = left,above = above, below = below, location = location, html_type = html_type)
        element = elements[0]
        print("(Alex): " + element.description)

    # find the element that best matches the descr and satisfies filters in the DOM
    # TODO: RUN AND MAKE SURE THE SELECTOR WORKS
    async def retrieve(self, description='', right =False, left=False, above=False, below=False, location=False, html_type=False, tag = '', type_raw = '', return_list = False):
        # dom = self.webdriver.get_elements_db()
        self.dom = await self.getDOM() 
        descr_embedding = self.embedding_model.encode([description])[0]
        scores = {}
        elements = {} 
        text_scores = {} 

        body_width = self.dom[0]['width']
        body_height = self.dom[0]['height']

        for el_row in self.dom:
            element = Element(el_row, self.embedding_model, body_height, body_width)
            if element.hidden == True or not self.passFilters(element, body_width, body_height, right, left, above, below, location, html_type, tag, type_raw):
                continue
            score = cs([descr_embedding], [element.descr_embedding])[0][0]
            scores[element.ref] = score
            elements[element.ref] = element 
            text_scores[element.description] = score

            if description == element.description: 
                scores[element.ref] = 1.1
                elements[element.ref] = element 
                text_scores[element.description] = 1.1
            if description in element.description: 
                scores[element.ref] = 0.94
                elements[element.ref] = element 
                text_scores[element.description] = 0.94
            num_words = len(description.split())
            num_in = 0 
            for word in description.split(): 
                if word.lower() in element.description.lower(): num_in += 1
            if num_in > 0: 
                scores[element.ref] = 0.8 + num_in / num_words * 0.14 - len(element.description.split()) * 0.01
                elements[element.ref] = element 
                text_scores[element.description] = 0.8 + num_in / num_words * 0.14 - len(element.description.split()) * 0.01

        # print("MATCH SCORES: ")
        # print({k: v for k, v in sorted(text_scores.items(), key=lambda item: item[1])})
        
        if len(list(scores.keys())) == 1: 
            return[elements[list(scores.keys())[0]]]
        
        best_xid = max(scores.items(), key=operator.itemgetter(1))[0]
        print(elements[best_xid].description)
        return [elements[best_xid]]

async def func():
    a = WebDriver()
    b = Agent2(a)
    await b.webdriver.openDriver()
    await b.runParsedInstruction("now => @webagent.goto param:website = \" https://www.amazon.com/ \"")
    await b.runParsedInstruction("let param:your_search = ( @webagent.ask param:text = \" your search \" )")
    await b.runParsedInstruction("now => @webagent.retrieve => @webagent.enter param:text = \" your search \" on param:element = param:id ")
    await b.runParsedInstruction("now => ( @webagent.retrieve param:description = \" epic daily deal\" ) join ( @webagent.retrieve param:description = \" see more \" ) on param:below = param:id => @webagent.read param:element = param:id")
    await asyncio.sleep(10000)

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
result = loop.run_until_complete(func())