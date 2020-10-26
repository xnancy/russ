# Agent takes a semantic parse and executes the corresponding sequence of actions
from sklearn.metrics.pairwise import cosine_similarity as cs
from sentence_transformers import SentenceTransformer
import operator
import json
import numpy as np
import asyncio

from WebDriver import WebDriver

class Element:
# get the data and compute the additional representations here
    def __init__(self, attrs, embedding_model):
        # print (attrs)
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
        if 'ref' in attrs.keys() and attrs['ref'] is not None:
            self.ref = attrs['ref']
        if 'xid' in attrs.keys() and attrs['xid'] is not None:
            self.xid = attrs['xid']
        if 'selector' in attrs.keys():
            self.selector = attrs['selector']
        if 'text' in attrs.keys():
            self.text = attrs['text']

        self.class_id = ''
        if 'classes' in attrs.keys() and attrs['classes'] is not None:
            self.class_id  += attrs['classes'].replace('-', ' ').replace('.', ' ').replace('/', ' ').replace(',', ' ').replace('_', ' ')
        if 'id' in attrs.keys() and attrs['id'] is not None:
            self.class_id  += attrs['id'].replace('-', ' ').replace('.', ' ').replace('/', ' ').replace(',', ' ').replace('_', ' ')
        if 'tag' in attrs.keys() and attrs['tag'] is not None:
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
    def passFilters(self, el, filters):
        if('location' in filters.keys() and el.location != filters['location']):
            return False
        if('size' in filters.keys() and el.size != filters['size']):
            return False
        if('childof' in filters.keys() and filters['childof'] not in el.childof):
            return False
        return True

    async def getDOM(self):
        result = await self.webdriver.getDOMInfo()
        return result['info']

    async def runParsedInstruction(self, action, arg1, arg2, arg3):
        if action == "CLICK": await self.click(arg1, arg2)
        elif action == "RESOLVE" : await self.resolve(arg1)
        elif action == 'resolveList': await self.resolveList(arg1, arg2)
        elif action == 'OUTPUT': self.output(arg1)
        elif action == 'ACT': await self.act(arg1)
        elif action == 'ENTER': await self.enter(arg1, arg2, arg3)
        elif action == 'READ': await self.read(arg1, arg2)
        elif action == 'readList': await self.readList(arg1, arg2)
        elif action == 'NO_ACTION': return

    # TODO: define the remaining functions
    async def click(self, descr, filters):
        dom = await self.getDOM()
        selector = self.matchElement(descr, filters, dom)
        print(selector)
        # elem = await self.webdriver.getElementFromXid(selector)
        await self.webdriver.click(f'[xid="{selector}"]')

    # returns a string of var value
    async def resolve(self, var):
        val = input("(Alex): What is the " + var +" ? \n")
        self.all_vars[var] = val
        return


    # returns a selector of item in list for var
    async def resolveList(self, var, filters):
        return

    def output(self, text):
        return

    async def act(self, action_id):
        return

    # can enter from var of if string_val = True just use the val
    async def enter(self, descr, filters, var_to_enter, str_val = False ):
        dom = await self.getDOM()
        selector = self.matchElement(descr, filters, dom)
        if str_val:
            text_to_enter = var_to_enter
        else:
            text_to_enter = self.all_vars[var_to_enter]
        await self.webdriver.enter_text(selector, text_to_enter)

    async def read(self, descr, filters):
        dom = await self.getDOM()
        selector = self.matchElement(descr, filters, dom)
        elem = await self.webdriver.getElementFromXid(selector)
        a = "innerText"
        text = await self.webdriver.page.evaluate(
                '(elem,a) => elem[a]',
                elem, a
		)
        print(text)
        return text

    async def readList(self, descr, filters):
        dom = await self.getDOM()
        selector = self.matchElement(descr, filters, dom)
        elem = self.webdriver.getElementFromXid(selector)
        children = elem.children
        entries = []
        for c in children:
            elem = self.webdriver.getElementFromXid(c)
            entries.append(elem.innerText)
        return entries

    # find the element that best matches the descr and satisfies filters in the DOM
    # TODO: RUN AND MAKE SURE THE SELECTOR WORKS
    def matchElement(self, descr, filters, dom):
        # dom = self.webdriver.get_elements_db()
        dom = dom
        descr_embedding = self.embedding_model.encode([descr])[0]
        scores = {}
        for el_row in dom:
            element = Element(el_row, self.embedding_model)
            if element.hidden == True or not self.passFilters(element, filters):
                continue
            score = cs([descr_embedding], [element.text_emb])[0][0]
            scores[element.ref] = score
        # print(scores)
        best_xid = max(scores.items(), key=operator.itemgetter(1))[0]
        best_selector = best_xid
        return best_selector


# async def func():
#     a = WebDriver()
#     b = Agent(a)
#     await b.webdriver.openDriver()
#     await b.webdriver.goToPage("https://www.amazon.com/gp/help/customer/display.html")
#     test = await b.click("search", {})
#     print(test)

#     await asyncio.sleep(10000)



# loop = asyncio.new_event_loop()
# asyncio.set_event_loop(loop)
# result = loop.run_until_complete(func())