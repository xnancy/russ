""" TODO: TRACK YOUR PACKAGE : "instructions": [
                    "Note:",
                    "Go to Your Orders.",
                    "Go to the order you want to track.",
                    "Click Track Package next to your order (if shipped separately). If your package or tracking information is missing, go to:"
                ],
"""

#TODO: Next to filter should be +- 

# Agent takes a semantic parse and executes the corresponding sequence of actions
from sklearn.metrics.pairwise import cosine_similarity as cs
from sentence_transformers import SentenceTransformer
import operator
import json
import numpy as np
import asyncio
import time

from representation.WebDriver import WebDriver
from representation.Element import Element
# from WebDriver import WebDriver
# from Element import Element 

class Agent:

    FILTERS = ['LOCATION', 'SIZE', 'ABOVE', 'LEFT', 'BELOW', 'RIGHT', 'TYPE']

    def __init__(self, webdriver):
        self.webdriver = webdriver
        # stores str and Element values. varname: value 
        self.all_vars = {}
        self.all_vars_embeddings = {} 
        self.embedding_model = SentenceTransformer('bert-base-nli-mean-tokens')

    # get variable stored with closest name embedding 
    def getVariable(self, name, type): 
        
        name_embedding = self.embedding_model.encode([name])[0]
        scores = {} 
        for var_name, var_embedding in self.all_vars_embeddings.items():
            if type == 'element' and not isinstance(self.all_vars[var_name], Element):
                continue 
            if type == 'text' and not isinstance(self.all_vars[var_name], str):
                continue 
            score = cs([name_embedding], [var_embedding])[0][0]
            scores[var_name] = score
        
        best_var_name = max(scores.items(), key=operator.itemgetter(1))[0]
        print('CHOSE THIS VARIABLE: ' + best_var_name + ' FOR ' + name)
        return self.all_vars[best_var_name]

    # filters is a dict of the form {filter: value} ex {'location': 'upperleft'}
    def passFilters(self, el, filters):
        if 'NEXTTO' in filters.keys():
            neighborVar = self.getVariable(filters['NEXTTO'],'element')
            return neighborVar.left <= el.left + el.width and el.left <= neighborVar.left + neighborVar.width
        if('LOCATION' in filters.keys() and el.location != filters['LOCATION']):
            return False
        if('SIZE' in filters.keys() and el.size != filters['SIZE']):
            return False
        if('CHILDOF' in filters.keys() and filters['CHILDOF'] not in el.childof):
            return False
        return True

    async def getDOM(self):
        result = await self.webdriver.getDOMInfo()
        return result['info']
 
    async def runParsedInstruction(self, action, arg1, arg2, arg3):
        print("RUNNING INSTR: " + str(action) + ', ' + str(arg1) + ', ' + str(arg2) + ', ' + str(arg3))
        if action == "CLICK": await self.click(arg1, arg2)
        elif action == "RESOLVE" : await self.resolve(arg1)
        elif action == "RESOLVE_TEXT": await self.resolveText(arg1)
        elif action == 'RESOLVE_LIST': await self.resolveList(arg1, arg2)
        elif action == 'OUTPUT': self.output(arg1)
        elif action == 'ACT': await self.act(arg1)
        elif action == 'ENTER': await self.enter(arg1, arg2, arg3)
        elif action == 'READ': await self.read(arg1, arg2)
        elif action == 'READ_LIST': await self.readList(arg1, arg2)
        elif action == 'NO_ACTION': return

    async def amazonLogin(self): 
        await self.webdriver.goToPage('https://www.amazon.com/ap/signin?openid.pape.max_auth_age=0&openid.return_to=https%3A%2F%2Fwww.amazon.com%2F%3Fref_%3Dnav_custrec_signin&openid.identity=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.assoc_handle=usflex&openid.mode=checkid_setup&openid.claimed_id=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.ns=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0&')
        await self.webdriver.enter_text('#ap_email', 'nancyxu97@gmail.com')
        await self.webdriver.click('#continue')
        await self.webdriver.enter_text('#ap_password', '!Test6261')
        await self.webdriver.click('#signInSubmit')
        await self.webdriver.page.waitForNavigation()
        # await self.click('Click here to refresh the page', {})


    # TODO: define the remaining functions
    async def click(self, descr, filters):
        # await self.webdriver.page.waitForNavigation()
        dom = await self.getDOM()
        element = self.matchElement(descr, filters, dom)
        print(element.text)
        # elem = await self.webdriver.getElementFromXid(selector)
        print("CLICKING SELECTOR: " + str(element.ref))
        await self.webdriver.click(f'[xid="{element.ref}"]')

    # returns a string of var value
    async def resolveText(self, var):
        val = input("(Alex): What is the " + var +" ? \n")
        self.all_vars[var] = val
        self.all_vars_embeddings[var] = self.embedding_model.encode([var])[0]
        return

    # returns a selector of item in list for var
    async def resolveList(self, var, filters):
        return

    # returns a selector corresponding to var value (basically store selector as var instead of click in CLICK)
    async def resolve(self, var):
        dom = await self.getDOM()
        val = input("(Alex): What is the " + var +" ? \n")
        el = self.matchElement(val, {}, dom)
        self.all_vars[var] = el
        self.all_vars_embeddings[var] = self.embedding_model.encode([var])[0] 
        
    def output(self, text):
        print("(Alex): " + text)

    async def act(self, action_id):
        return

    # can enter from var of if string_val = True just use the val
    async def enter(self, descr, filters, var_to_enter, str_val = False ):
        dom = await self.getDOM()
        el = self.matchElement(descr, filters, dom)
        selector = el.ref
        if str_val:
            text_to_enter = var_to_enter
        else:
            text_to_enter = self.getVariable(var_to_enter, 'text')
        await self.webdriver.enter_text(selector, text_to_enter)

    async def read(self, descr, filters):
        dom = await self.getDOM()
        selector = self.matchElement(descr, filters, dom).ref
        elem = await self.webdriver.getElementFromXid(selector)
        a = "innerText"
        text = await self.webdriver.page.evaluate(
                '(elem,a) => elem[a]',
                elem, a
		)
        print("(Alex): " + text)
        return text

    async def readList(self, descr, filters):
        dom = await self.getDOM()
        selector = self.matchElement(descr, filters, dom).ref
        elem = self.webdriver.getElementFromXid(selector)
        children = elem.children
        entries = []
        for c in children:
            elem = self.webdriver.getElementFromXid(c)
            entries.append(elem.innerText)
        return entries

    # find the element that best matches the descr and satisfies filters in the DOM
    # TODO: RUN AND MAKE SURE THE SELECTOR WORKS
    def retrieve(self, descr, filters, dom):
        # dom = self.webdriver.get_elements_db()
        dom = dom
        descr_embedding = self.embedding_model.encode([descr])[0]
        scores = {}
        elements = {} 
        text_scores = {} 
        print("MATCHING " + descr)

        for el_row in dom:
            element = Element(el_row, self.embedding_model)
            if element.hidden == True or not self.passFilters(element, filters):
                continue
            score = cs([descr_embedding], [element.text_emb])[0][0]
            scores[element.ref] = score
            elements[element.ref] = element 
            text_scores[element.text] = score

            if descr == element.text: 
                scores[element.ref] = 1.1
                elements[element.ref] = element 
                text_scores[element.text] = 1.1
            if descr in element.text: 
                scores[element.ref] = 0.94
                elements[element.ref] = element 
                text_scores[element.text] = 0.94
            num_words = len(descr.split())
            num_in = 0 
            for word in descr.split(): 
                if word.lower() in element.text.lower(): num_in += 1
            if num_in > 0: 
                scores[element.ref] = 0.8 + num_in / num_words * 0.14 - len(element.text.split()) * 0.01
                elements[element.ref] = element 
                text_scores[element.text] = 0.8 + num_in / num_words * 0.14 - len(element.text.split()) * 0.01

        print("MATCH SCORES: ")
        print({k: v for k, v in sorted(text_scores.items(), key=lambda item: item[1])})
        
        best_xid = max(scores.items(), key=operator.itemgetter(1))[0]
        print(elements[best_xid].text)
        return elements[best_xid]

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