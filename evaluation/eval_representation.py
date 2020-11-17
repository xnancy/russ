from sklearn.metrics.pairwise import cosine_similarity as cs
from sentence_transformers import SentenceTransformer
import operator
import json
import csv
import numpy as np
import time
from enum import Enum
from nltk import edit_distance
import pylev
import json 
import re 

def camel_case_split(text):
    matches = re.sub('([A-Z][a-z]+)', r' \1', re.sub('([A-Z]+)', r' \1', text)).split()
    return " ".join(matches)

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
        
        self.description = ''
        if 'text' in attrs.keys():
            self.description = attrs['text'].lower() 
        if 'attributes' in attrs.keys() and 'placeholder' in attrs['attributes'].keys():
            self.description += (" " + attrs['attributes']['placeholder'].lower())
        if 'attributes' in attrs.keys() and 'name' in attrs['attributes'].keys():
            self.description += (" " + camel_case_split(attrs['attributes']['name']).lower().replace("-", " "))
        if 'attributes' in attrs.keys() and 'aria-label' in attrs['attributes'].keys():
            if self.description == '':
                self.description = camel_case_split(attrs['attributes']['aria-label']).lower().replace("-"," ")
        self.descr_embedding = np.zeros(768)
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
            elif (self.tag.strip().lower() == "datalist" or self.tag.strip().lower() == "dl" or self.tag.strip().lower() == "ol" or self.tag.strip().lower() == "select" or self.tag.strip().lower() == "ul" or self.tag.strip().lower() == "option"): 
                self.html_type = Type.dropdown
            elif (self.tag.strip().lower() == "input" or self.tag.strip().lower() == "kbd" or self.tag.strip().lower() == "textarea"):
                self.html_type = Type.input_el
        
        self.hidden = False
        if 'hidden' in attrs.keys() and attrs['hidden'] is not None:
            self.hidden = attrs['hidden']
            
        self.role = False 
        if 'role' in attrs.keys() and attrs['role'] is not None:
            self.role = attrs['role']
        if self.role: 
            if (self.role == "button"): 
                self.html_type = Type.button
            elif (self.role == "checkbox" or self.role == "switch" or self.role == "menuitemcheckbox" or self.role == "menuitemradio"): 
                self.html_type = Type.checkbox
                self.hidden = False 
            elif (self.role == "link"): 
                self.html_type = Type.link
                self.hidden = False 
            elif (self.role == "searchbox" or self.role =="textbox"):
                self.html_type = Type.input_el
                self.hidden = False 
            elif (self.role == "document" or self.role == "heading"): 
                self.html_type = Type.text
            elif (self.role == "figure" or self.role =="img"): 
                self.html_type = Type.image
        if 'attributes' in attrs.keys() and 'type' in attrs['attributes'].keys() and 'checkbox' in attrs['attributes']['type'].lower():
            self.html_type = Type.checkbox
            self.hidden = False 
        if 'attributes' in attrs.keys() and 'class' in attrs['attributes'].keys() and 'checkbox' in attrs['attributes']['class'].lower():
            self.html_type = Type.checkbox
            self.hidden = False

        if 'ref' in attrs.keys() and attrs['ref'] is not None:
            self.ref = attrs['ref']
        if 'xid' in attrs.keys() and attrs['xid'] is not None:
            self.xid = attrs['xid']
        
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
    
    def print(self): 
        print("Desc: " + self.description)
        print("XID: " + str(self.xid))
        print("html type: " + str(self.html_type))
        print("Tag: " + str(self.tag))
        print("Role: " + str(self.role))
        print("Location: " + str(self.location))
        print("Top: " + str(self.top))
        print("Bottom: " + str(self.bottom))
        print("Left: " + str(self.left))
        print("Right: " + str(self.right))
        print("Hidden: " + str(self.hidden))
        print("Type raw: " + str(self.type_raw))

# variables stored as string with spaces (remove _case) and map to string
class RepresentationAgent:
    def __init__(self, dom_file, var = False): 
        # stores str and Element values. varname: value 
        self.embedding_model = SentenceTransformer('distilbert-base-nli-mean-tokens')
        self.dom = json.load(open(dom_file))['info']
        self.var = var

    # filters is a dict of the form {filter: value} ex {'location': 'upperleft'}
    def printPassFilters(self, element, body_width, body_height, right=False, left=False, above=False, below=False, location=False, html_type=False, tag = '', type_raw=''):
        print("FILTERING " + str(element.xid))
        if right and element.right and (element.right < right.right or (element.right - right.right) / body_width > 0.2): 
            # print("A")
            print("END FILTERING")
            return
        if left and element.left and (element.left > left.left or (left.left - element.left) / body_width > 0.2): 
            print("B")
            print("END FILTERING")
            return
        if above and element.top and (element.top > above.top or (above.top - element.top) / body_height > 0.2): 
            print("C")
            print("END FILTERING")
            return
        
        if below and element.bottom and (element.bottom < below.bottom or (element.bottom - below.bottom)  / body_height > 0.2): 
            print("D")
            print("END FILTERING")
            return
        if location and element.location :
            if location.value == 'top': 
                if (element.location.value != 'top_left'  and element.location.value != 'top_right'): 
                    print("D1")  
                    print("END FILTERING")
                    return
            elif location.value == 'bottom': 
                if (element.location.value != 'bottom_left'  and element.location.value != 'bottom_right'): 
                    print("D2")
                    print("END FILTERING")
                    return  
            elif location.value == 'left': 
                if (element.location.value != 'top_left'  and element.location.value != 'bottom_left'): 
                    print("D3")
                    print("END FILTERING")
                    return  
            elif location.value == 'right': 
                if (element.location.value != 'top_right'  and element.location.value != 'bottom_right'): 
                    print("D4") 
                    print("END FILTERING")
                    return 
            elif location.value != element.location.value: 
                print("D5")  
                print("END FILTERING")
                return
        if html_type and (not element.html_type or html_type.value != element.html_type.value): 
            print("F")
            print("END FILTERING")
            return
        if type_raw and element.type_raw and element.type_raw.lower() not in [raw.lower() for raw in type_raw] : 
            print("G")
            print("END FILTERING")
            return
        if tag and element.tag and tag.lower() != element.tag.lower(): 
            print("H")
            print("END FILTERING")
            return
        print("END FILTERING")
        return True 

    # filters is a dict of the form {filter: value} ex {'location': 'upperleft'}
    def passFilters(self, element, body_width, body_height, right=False, left=False, above=False, below=False, location=False, html_type=False, tag = '', type_raw=''):    
        # print("FILTERING: " + str(element.xid))
        if right and element.right and (element.right < right.right or (element.right - right.right) / body_width > 0.4 or (element.top and element.bottom and right.top and right.bottom and (min(right.bottom, element.bottom) - max(right.top, element.top)) / body_height < -0.02)): 
            # print("A")
            return False 
        if left and element.left and (element.left > left.left or (left.left - element.left) / body_width > 0.4 or (element.top and element.bottom and left.top and left.bottom and (min(left.bottom, element.bottom) - max(left.top, element.top)) / body_height < -0.02)): 
            # print("B")
            # print(element.left > left.left)
            # print((left.left - element.left) / body_width)
            # print((min(left.bottom, element.bottom) - max(left.top, element.top)) / body_height)
            return False
        if above and element.top and (element.top > above.top or (above.top - element.top) / body_height > 0.3 or (element.left and element.right and above.left and above.right and (min(above.right, element.right) - max(above.left, element.left)) / body_width < -0.02)): 
            # print("C")
            return False 
        if below and element.bottom and (element.bottom < below.bottom or (element.bottom - below.bottom)  / body_height > 0.3 or (element.left and element.right and below.left and below.right and (min(below.right, element.right) - max(below.left, element.left)) / body_width < -0.02)): 
            # print("D")
            return False 
        if location and element.location :
            if location.value == 'top': 
                if (element.location.value != 'top_left'  and element.location.value != 'top_right'): 
                    # print("E")
                    return False 
            elif location.value == 'bottom': 
                if (element.location.value != 'bottom_left'  and element.location.value != 'bottom_right'): 
                    # print("F")
                    return False 
            elif location.value == 'left': 
                if (element.location.value != 'top_left'  and element.location.value != 'bottom_left'): 
                    # print("G")
                    return False 
            elif location.value == 'right': 
                if (element.location.value != 'top_right'  and element.location.value != 'bottom_right'): 
                    # print("H")
                    return False 
            elif location.value != element.location.value: 
                # print("I")
                return False 
        # print(html_type)
        # print(element.html_type)

        if html_type and (not element.html_type or html_type.value != element.html_type.value): 
            # print("J")
            return False 
        if type_raw and element.type_raw and element.type_raw.lower() not in [raw.lower() for raw in type_raw] : 
            # print("K")
            return False 
        if tag and element.tag and tag.lower() != element.tag.lower(): 
            # print("L")
            return False
        # print("M") 
        return True 
 
    def get_params_from_string(self, parsed_string): 
        params = {"description": '', "location": False, "html_type": False}
        if "param:description" in parsed_string: 
            # print("HERE")
            # print(parsed_string)
            # print(parsed_string.split("=", 1)[1])
            # print(parsed_string.split("=", 1)[1].split("param:description")[1])
            params['description'] = parsed_string.split("param:description")[1].split("\"")[1].replace("\"","").strip()
            if "param" in parsed_string.split("param:description")[1].split("\"")[0]: 
                params['description'] = self.var
        if "param:text" in parsed_string: 
            params['text_var'] = parsed_string.split("=", 1)[1].split("param:text")[1].split("\"")[1].replace("\"","").strip()
        if "param:location" in parsed_string: 
            params['location'] = Location(parsed_string.split("param:location")[1].split("enum:")[1].split(" ")[0].strip())
        if "param:type" in parsed_string: 
            temp_type = parsed_string.split("param:type")[1].split("enum:")[1].split(" ")[0].strip()
            if "input" == temp_type:
                temp_type = 'input_el' 

            params['html_type'] = Type(parsed_string.split("param:type")[1].split("enum:")[1].split(" ")[0].strip())
        return params 

    def runParsedInstruction(self, parsed_wt):
        enum_dict = {}
        params = self.get_params_from_string(parsed_wt) 
        if parsed_wt.count("@webagent.retrieve") == 0 and parsed_wt.count("@webagent.say") == 1: 
            return ("say",'-1')           
        elif parsed_wt.count("@webagent.retrieve") == 0 and parsed_wt.count("@webagent.ask") == 1: 
            return ("ask",'-1')
        elif parsed_wt.count("@webagent.retrieve") == 0 and parsed_wt.count("@webagent.goto") == 1:
            return ("goto",'-1')
        elif parsed_wt.count("@webagent.retrieve") == 1 and parsed_wt.count("@webagent.read") == 1:     
            return ("read", self.read(description = params['description'], location = params['location'], html_type = params['html_type']))
        elif parsed_wt.count("@webagent.retrieve") == 1 and parsed_wt.count("@webagent.click") == 1:     
            return ("click", self.click(description = params['description'], location = params['location'], html_type = params['html_type']))
        elif parsed_wt.count("@webagent.retrieve") == 1 and parsed_wt.count("@webagent.enter") == 1:     
            return ("enter", self.enter(text_var = params['text_var'], description = params['description'], location = params['location'], html_type = params['html_type']))
        elif parsed_wt.count("@webagent.retrieve") == 2 and parsed_wt.count("@webagent.read") == 1: 
            first_params = self.get_params_from_string(parsed_wt.split("@webagent.retrieve")[1])  
            second_params = self.get_params_from_string(parsed_wt.split("@webagent.retrieve")[2]) 
            first_element = self.retrieve(description = first_params['description'], location = first_params['location'], html_type = first_params['html_type'])
            first_element = first_element[0]
            # print("FIRST ELEMENT")
            # first_element.print()
            if "param:left" in parsed_wt: 
                return ('read', self.read(description = second_params['description'], left = first_element, location = second_params['location'], html_type = second_params['html_type']))
            if "param:right" in parsed_wt: 
                return ('read',self.read(description = second_params['description'], right = first_element, location = second_params['location'], html_type = second_params['html_type']))
            if "param:above" in parsed_wt: 
                return ('read',self.read(description = second_params['description'], above = first_element, location = second_params['location'], html_type = second_params['html_type']))
            if "param:below" in parsed_wt: 
                return ('read',self.read(description = second_params['description'], below = first_element, location = second_params['location'], html_type = second_params['html_type']))
            
        elif parsed_wt.count("@webagent.retrieve") == 2 and parsed_wt.count("@webagent.click") == 1:    
            first_params = self.get_params_from_string(parsed_wt.split("@webagent.retrieve")[1])  
            second_params = self.get_params_from_string(parsed_wt.split("@webagent.retrieve")[2]) 
            first_element = self.retrieve(description = first_params['description'], location = first_params['location'], html_type = first_params['html_type'])
            first_element = first_element[0]
            # print("FIRST ELEMENT")
            # first_element.print()
            if "param:left" in parsed_wt: 
                return ('click', self.click(description = second_params['description'], left = first_element, location = second_params['location'], html_type = second_params['html_type']))
            if "param:right" in parsed_wt: 
                return ('click', self.click(description = second_params['description'], right = first_element, location = second_params['location'], html_type = second_params['html_type']))
            if "param:above" in parsed_wt: 
                return ('click', self.click(description = second_params['description'], above = first_element, location = second_params['location'], html_type = second_params['html_type']))
            if "param:below" in parsed_wt: 
                return ('click', self.click(description = second_params['description'], below = first_element, location = second_params['location'], html_type = second_params['html_type']))
        
        elif parsed_wt.count("@webagent.retrieve") == 2 and parsed_wt.count("@webagent.enter") == 1:     
            first_params = self.get_params_from_string(parsed_wt.split("@webagent.retrieve")[1])  
            second_params = self.get_params_from_string(parsed_wt.split("@webagent.retrieve")[2]) 
            first_element = self.retrieve(description = first_params['description'], location = first_params['location'], html_type = first_params['html_type'])
            first_element = first_element[0]
            # print("FIRST ELEMENT")
            # first_element.print()
            if "param:left" in parsed_wt: 
                return ('enter', self.enter(text_var = second_params['text_var'], description = second_params['description'], left = first_element, location = second_params['location'], html_type = second_params['html_type']))
            if "param:right" in parsed_wt: 
                return ('enter', self.enter(text_var = second_params['text_var'], description = second_params['description'], right = first_element, location = second_params['location'], html_type = second_params['html_type']))
            if "param:above" in parsed_wt: 
                return ('enter', self.enter(text_var = second_params['text_var'], description = second_params['description'], above = first_element, location = second_params['location'], html_type = second_params['html_type']))
            if "param:below" in parsed_wt: 
                return ('enter', self.enter(text_var = second_params['text_var'], description = second_params['description'], below = first_element, location = second_params['location'], html_type = second_params['html_type']))
        else: 
            print("Error in parse")
    
    # TODO: define the remaining functions
    def click(self, description='', right =False, left=False, above=False, below=False, location=False, html_type=False):
        # print("Retrieving element to click")
        elements = self.retrieve(description=description, right=right, left=left,above=above, below=below, location=location, html_type=html_type)
        element=  elements[0]
        # print("FOUND: ")
        if element: 
            # element.print()
            return element.xid 
        else: 
            return "No matches"

    # can enter from var of if string_val = True just use the val
    # type = 'text' and tag = 'input' 
    def enter(self, text_var, description='', right =False, left=False, above=False, below=False, location=False, html_type=False):
        elements = self.retrieve(description=description, right=right, left=left,above=above, below=below, location=location, html_type=html_type, tag = '', type_raw = ["text", 'date', 'datetime-local', 'email', 'month', 'number','password', 'range', 'search', 'tel', 'url', 'week', 'color'])
        element=  elements[0]
        # print("FOUND: ")
        if element: 
            # element.print()
            return element.xid 
        else: 
            return "No matches"

    def read(self, description='', right =False, left=False, above=False, below=False, location=False, html_type=False):
        elements = self.retrieve(description = description, right = right, left = left,above = above, below = below, location = location, html_type = html_type)
        element = elements[0]
        # print("FOUND: ")
        if element: 
            # element.print()
            return element.xid 
        else: 
            return "No matches"

    # find the element that best matches the descr and satisfies filters in the DOM
    # TODO: RUN AND MAKE SURE THE SELECTOR WORKS
    def retrieve(self, description='', right =False, left=False, above=False, below=False, location=False, html_type=False, tag = '', type_raw = '', return_list = False):
        # dom = self.webdriver.get_elements_db()
        # print("RETRIEVE: description: " + description + " right: " + str(right) + " left: " + str(left) + " above: " + str(above) + " below: " + str(below) + " location: " + str(location) + " html type: " + str(html_type) + " tag: " + str(tag) + " type_raw: " + str(type_raw) + " return list: " + str(return_list)  )
        if not description: 
            description = ""
        description = description.lower().replace("?", " ").replace(".", " ")
        descr_embedding = self.embedding_model.encode([description])[0]
        scores = {}
        elements = {} 
        text_scores = {} 

        body_width = self.dom[0]['width']
        body_height = self.dom[0]['height']

        description_list =  description.lower().strip().split(" ")
        
        for el_row in self.dom:
            element = Element(el_row, self.embedding_model, body_height, body_width)
            if element.hidden == True or not self.passFilters(element, body_width, body_height, right, left, above, below, location, html_type, tag, type_raw):
                continue
            score = cs([descr_embedding], [element.descr_embedding])[0][0]
            
            # If no text and relative, score based on distance
            if right and description.replace(" ", "") == '':
                score = right.right - element.right
            if left and description.replace(" ", "") == '':
                score = element.left - left.left
            if above and description.replace(" ", "") == '':
                score = element.top - above.top
            if below and description.replace(" ", "") == '':
                score = below.bottom - element.bottom

            """
            # Compute word level lev distance
            score = pylev.levenshtein(description_list,  element.description.replace("?", "").replace(".", "").lower().strip().split(" "))

            score = 100 - score
            scores[element.xid] = score
            elements[element.xid] = element 
            text_scores[element.description] = score

            if description.strip().replace(" ", '') == element.description.replace("?", "").replace(".", "").lower().replace(" ", '').strip(): 
                return [element]

            if description.lower() in element.description.replace("?", "").replace(".", "").lower() or element.description.replace("?", "").replace(".", "").lower() in description.lower(): 
                scores[element.xid] = 100 + min(len(description.lower().split()), len(element.description.replace("?", "").replace(".", "").lower().split()))
                text_scores[element.description] = 100 + min(len(description.lower().split()), len(element.description.replace("?", "").replace(".", "").lower().split()))

            for word in description.split(): 
                if word in element.description.replace("?", "").replace(".", "").lower(): 
                    scores[element.xid] += 2
                    text_scores[element.description] += 2
            """
            scores[element.xid] = score
            elements[element.xid] = element 
            text_scores[element.description] = score

        # print("SCORES: ")
        # print({k: v for k, v in sorted(scores.items(), key=lambda item: item[1])})
        # print(text_scores)
        if len(scores.keys()) == 0: 
            return [False]
        best_xid = max(scores.items(), key=operator.itemgetter(1))[0]
        # print("Best element match contains text: " + str(elements[best_xid].description))
        return [elements[best_xid]]

def hash_to_parse(eval_webtalk_file): 
    eval_webtalk = csv.reader(open(eval_webtalk_file), delimiter="\t")
    parse_dict = {} 
    for row in eval_webtalk:
        parse_dict[row[0]] = row[2]
    return parse_dict

parse_dict = hash_to_parse("eval_webtalk.tsv")

total_tokens = 0 
total = 0 
correct = 0 
var = False 
for row in csv.reader(open("temp-eval_instructions-nancy-eval.tsv"), delimiter="\t"): 
    
    total_tokens += len(row[0].strip().split()) 

    if len(row) < 2 or row[0] == '':
        continue 

    if "v_" in row[0]: 
        
        var = row[0].split(":")[1].strip()
        continue 
    parse = parse_dict[row[1]]

    if "n/a" in parse.lower() or parse.lower().strip() == "na": 
        continue 

    agent = RepresentationAgent("eval_DOMs/" + str(row[3]).strip() + ".json", var)
    (action, xid) = agent.runParsedInstruction(parse)
    if action == 'enter' or action == 'click' or action == 'read': 
        total += 1
        if xid == row[2]: 
            correct += 1 
        else: 
            print("WRONG --------------------------")
            print(row)
            print(parse)
            print(xid)
    var = False 
print("AVERAGE TOKENS : " + str(total_tokens / total))
print("TOTAL : " + str(total))
print("CORRECT: " + str(correct))