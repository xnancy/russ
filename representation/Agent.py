# Agent takes a semantic parse and executes the corresponding sequence of actions 
from sklearn.metrics.pairwise import cosine_similarity as cs 
from sentence_transformers import SentenceTransformer
import operator 
import json
import numpy as np 

class Element: 
# get the data and compute the additional representations here 
    def __init__(self, attrs, embedding_model): 
        self.attributes = ''
        self.selector = 'TEST'
        self.text = ''
        self.class_id = ''
        self.attributes = ''
        self.tag = ''
        self.role = ''
        self.hidden = False
        self.top = 0
        self.left = 0
        self.width = 0
        self.height = 0
        self.children = []
        self.text_emb = np.zeros(768)

        self.ref = attrs['ref']
        if 'selector' in attrs.keys(): 
            self.selector = attrs['selector']
        if 'text' in attrs.keys(): 
            self.text = attrs['text']

        self.class_id = '' 
        if 'classes' in attrs.keys() and attrs['classes'] is not None: 
            self.class_id  += attrs['classes'].replace('-', ' ').replace('.', ' ').replace('/', ' ').replace(',', ' ').replace('_', ' ')
        if 'id' in attrs.keys() and attrs['id'] is not None: 
            self.class_id  += attrs['id'].replace('-', ' ').replace('.', ' ').replace('/', ' ').replace(',', ' ').replace('_', ' ')

        self.tag = attrs['tag']

        if 'attributes' in attrs.keys() and attrs['attributes'] is not None: 
            for key, value in attrs['attributes'].items():
                if key == 'class': 
                    continue 
                self.attributes += key.replace('-', ' ').replace('.', ' ').replace('/', ' ').replace(',', ' ').replace('_', ' ')
                self.attributes += value.replace('-', ' ').replace('.', ' ').replace('/', ' ').replace(',', ' ').replace('_', ' ')
        if 'role' in attrs.keys() and attrs['role'] is not None: 
            self.role = attrs['role']
        if 'hidden' in attrs.keys() and attrs['hidden'] is not None:
            self.hidden = attrs['hidden']
        if 'top' in attrs.keys() and attrs['top'] is not None:
            self.top = attrs['top']
        if 'left' in attrs.keys() and attrs['left'] is not None:
            self.top = attrs['left']
        if 'width' in attrs.keys() and attrs['width'] is not None:
            self.top = attrs['width']
        if 'height' in attrs.keys() and attrs['height'] is not None:
            self.top = attrs['height']
        if 'children' in attrs.keys() and attrs['children'] is not None:
            self.top = attrs['children']
        if self.text != '': 
            self.text_emb = embedding_model.encode([self.text])[0]
        # TODO: compute Location, size, childof


class Agent: 

    FILTERS = ['location', 'size', 'childof']

    def __init__(self, webdriver):
        self.webdriver = webdriver 
        self.all_vars = {} 
        self.embedding_model = SentenceTransformer('bert-base-nli-mean-tokens')

    # filters is a dict of the form {filter: value} ex {'location': 'upperleft'} 
    def pass_filters(self, el, filters): 
        if('location' in filters.keys() and el.location != filters['location']): 
            return False 
        if('size' in filters.keys() and el.size != filters['size']): 
            return False 
        if('childof' in filters.keys() and filters['childof'] not in el.childof): 
            return False 
        return True  

    def run_parsed_instruction(action, arg1, arg2, arg3): 
        switch(action) {
            case 'CLICK': self.click(arg1, arg2);
            case 'RESOLVE': self.resolve(arg1);
            case 'RESOLVE_LIST': self.resolve_list(arg1, arg2);
            case 'OUTPUT': self.output(arg1);
            case 'ACT': self.act(arg1);
            case 'ENTER': self.enter(arg1, arg2, arg3);
            case 'READ': self.read(arg1, arg2);
            case 'READ_LIST': self.read_list(arg1, arg2);
            case 'NO_ACTION': return 
        }

    # TODO: define the remaining functions 
    def click(self, descr, filters, dom): 
        selector = self.match_element(descr, filters, dom)
        self.webdriver.click(selector)

    # returns a string of var value 
    def resolve(self, var, filters): 
        return 


    # returns a selector of item in list for var 
    def resolve_list(self, var, filters): 
        return 

    def output(self, text): 
        return 

    def act(self, action_id): 
        return 

    def enter(self, descr, filters, str_var_to_enter): 
        return 

    def read(self, descr, filters): 
        return 

    def read_list(self, descr, filters): 
        return 

    # find the element that best matches the descr and satisfies filters in the DOM 
    # TODO: remove dom arg to get from webdriveer 
    def match_element(self, descr, filters, dom): 
        # dom = self.webdriver.get_elements_db() 
        dom = dom
        descr_embedding = self.embedding_model.encode([descr])[0]
        scores = {} 
        for el_row in dom: 
            element = Element(el_row, self.embedding_model)
            if element.hidden == True or not self.pass_filters(element, filters): 
                continue 
            score = cs([descr_embedding], [element.text_emb])[0][0]
            scores[element.ref] = score
        best_selector = max(scores.items(), key=operator.itemgetter(1))[0]
        print(best_selector)
        return best_selector
           
f = open("AmazonSample.json")
data = json.load(f)
dom = data['info']

agent = Agent('webdriver')
agent.click('go to customer service', {}, dom)
agent.click('show me my orders', {}, dom)

