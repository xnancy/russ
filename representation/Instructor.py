#TODO figure out how to return 
# TODO figure out how to filter 
# TODO figure out why match is wrong for tracking button 
import re 
import asyncio 
from pyppeteer import launch

from Agent import Agent
from WebDriver import WebDriver
from SemnaticParser import SemnaticParser
# Instructor interacts with the user and parses the instruction templates

#TODO: build the semantic parser, and use in parse.py


class Instructor: 
    def __init__(self, webdriver, agent, semanticparser):
        self.agent = agent 
        self.webdriver = webdriver
        self.instructions = [] 
        self.var_sel = {} 
        self.var_text = {} 

        print("Hi I'm Alex! How can I help you today?")

    async def askQuestion(self): 
        inp = input("(Alex): How can I help you today?\n")
        if (inp == 'QUIT'):
            print("Bye!")
        else: 
            await self.search(inp)
            await self.askQuestion()
        
    async def search(self, query): 
        browser = await launch(headless = False, executablePath = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")
        page = await browser.newPage()


        formattedQuery = query.replace('/\s+/g', '+')
        searchQuery = "https://www.amazon.com/gp/help/customer/display.html/ref=hp_search_rd_gw?__mk_en_US=%C3%85M%C3%85%C5%BD%C3%95%C3%91&help_keywords=" + formattedQuery + "&search=true&nodeId=508510&kwHidden=true&sprefix=&locale=en_US"
        await page.goto(searchQuery)

        searchResults = await page.evaluate('''() => {
                let elements = document.getElementsByClassName('a-link-normal');
                let data = [];
            
                for (var element of elements) {
                    data.push([element.textContent.trim(), element.href])
                }
                return data;
            }''')
            
        choice = -1
        searchAgain = "y"
        while (searchAgain == "y") : 
            choice = await self.selectResponse(searchResults, len(searchResults))
            if (choice >= 0) : 
                await self.expandSearch(searchResults[choice][1], page)
                searchAgain = input("\nWould you like to revisit the search results (y/n)? ")
           
        await browser.close()
    

    async def selectResponse(self, searchResults, numResults, viewAll = False) : 
        choice = -1
        if (viewAll):
            choice = input("\n Which would you like to learn more about (QUIT to quit)? \n")
        else: 
            if (numResults == 0): 
                print("Sorry, I can't help with what you're looking for! Directing to agent...\n")   
            elif(numResults == 1): 
                choice = 0
            elif(numResults == 2): 
                print("(Alex) Happy to help with that! Which of the following would you like to do?:\n")
                print("1. "  + searchResults[0][0] + "\n2." + searchResults[1][0] + "\n")
                choice = input("Which would you like more information on (1 or 2)? ")
            else: 
                print("(Alex) Happy to help with that! Which of the following would you like to do?:\n")
                print("1. "  + searchResults[0][0] + "\n2." + searchResults[1][0] + "\n3." + searchResults[2][0] + "\n")
                choice = input("Which would you like more information on (1, 2, 3)? ")
    
        if (choice == "QUIT") :
            return choice
        else: 
            return int(choice) - 1
    
    # TODO: Split searchResults so that it returns phrases vs lines. Currently you don't know from the tuple if the line has multiple sentences which sentence hte link or bold is in. 
    async def expandSearch(self, searchUri, page) : 
        await page.goto(searchUri)
        searchResults = await page.evaluate('''() => {
            let data = [];
            let steps = [];
            let elements;
            if (document.getElementsByClassName('a-row cs-help-landing-section help-display-cond help-display-cond-hidden help-display-cond-rule-platform-DesktopBrowser').length > 0){
            elements = document.getElementsByClassName('a-column a-span4');
            let links = document.getElementsByClassName('a-list-item');
            for (var link of links) {
                let recurseLink; 
                if (link.innerHTML.toString().match(/href="([^"]*)/)) {
                    recurseLink = link.innerHTML.toString().match(/href="([^"]*)/)[1];
                } else {
                    recurseLink = null;
                }
                if (recurseLink && recurseLink.toString().substr(0, 4) != "http"){
                    recurseLink = "https://www.amazon.com" + recurseLink;
                }
                data.push([link.textContent, recurseLink, steps]);
                }
                } else if (document.getElementsByClassName('a-section a-spacing-large ss-landing-container-wide').length > 0) {
                    elements = document.getElementsByClassName('a-link-normal a-text-normal a-color-base')
                    for (var element of elements) {
                        data.push([element.textContent.trim(), element.href, steps]);
                    }
                } else {
                    elements = document.getElementsByClassName('help-content');
                    let stepsElement = document.getElementsByClassName('a-list-item');
                    for (var step of stepsElement){

                        if (step.innerHTML.toString().match(/href="([^"]*)/)) {
                        actionLink = step.innerHTML.toString().match(/href="([^"]*)/)[1];
                        if (actionLink.toString().substr(0, 4) != "http"){
                            actionLink = "https://www.amazon.com" + actionLink;
                        }
                        } else {
                        actionLink = null;
                        }

                        let boldStr; 
                        if (step.innerHTML.toString().match(/<strong>([\S\s]*?)<\/strong>/gi)) {
                        boldStr = step.innerHTML.toString().match(/<strong>([\S\s]*?)<\/strong>/gi)[0].toString(); // 0 index just grab first match
                        boldStr = boldStr.trim().substr(8, boldStr.length-17)
                        } else {
                        boldStr = null;
                        }

                        steps.push([step.textContent, actionLink, boldStr])
                    }
                for (var element of elements) {
                    data.push([element.textContent.trim(), element.href, steps]);
                }
            }
            return data;
        }''')
        
        recurseSearch = []
        for i in range(len(searchResults)) : 
            if (searchResults[i][1]): 
                recurseSearch.push([searchResults[i][0], searchResults[i][1]])
            
        if (recurseSearch and len(recurseSearch) > 0) : 
            print("\nFind out more about: ")
            for i in range(len(ecurseSearch)): 
                print(str(i+1) + ". " + re.sub(r'\n+', '\n', recurseSearch[i][0]).strip())
            
            choice = selectResponse(recurseSearch, len(ecurseSearch), true)
            if (choice == "QUIT" or  choice == '') : 
                browser.close() 
                return
        
            await expandSearch(recurseSearch[choice][1], page)
        else: 

            print("LOGGING IN")
            await self.agent.amazonLogin()

            print("GOING TO URL")
            print(page.url) 
            await self.webdriver.goToPage(page.url)

            for i in range(len(searchResults[0][2])) : 
                await self.stepHelpContent(page, searchResults[0][2][i])
                print("RUNNING")
                print(self.instructions)
                await self.runInstructions()

        await browser.close()

    async def runInstructions(self): 
        for i in range(len(self.instructions)): 
            action, arg1, arg2, arg3  = self.instructions.pop(0)

            await agent.runParsedInstruction(action, arg1, arg2, arg3)


    # each step is list of form ['text', 'link or None', 'bold text']
    async def stepHelpContent(self, page, step) : 
        text = re.sub(r'\ *\n+\ *', '\n', step[0]).replace("\t", "")
        actions = re.split(' and |\. |\n',text)
        actions = [(x.strip().lower(), step[1], step[2]) for x in actions if x and len(x.strip()) > 2]
        
        for action in actions: 
            self.instructions.extend(semanticparser.parse(action))

    async def parseHelpContent(self, step) : 
        KEYWORDS = ["select", "go to", "enter", "click"]
        res = []
        keywordIndices = []
        keywordIndex = -1
        for keyword in KEYWORDS : 
            print(step)
            keywordIndex = step.toLowerCase().trim().indexOf(keyword + ' ') 
            if(keywordIndex  >= 0): 
                keywordIndices.push(keywordIndex)
         
        for i in range(len(keywordIndices) - 1): 
            res.push(step.substr(keywordIndices[i], keywordIndices[i+1]))
        
        res.push(step.substr(keywordIndices[len(keywordIndices)-1], len(step) + 1))
        if (len(res) == 0):
            return [step]
        
        return res


loop = asyncio.get_event_loop()


driver = WebDriver()
loop.run_until_complete(driver.openDriver()) 
agent = Agent(driver)
semanticparser = SemanticParser()
instructor = Instructor(driver, agent, semanticparser)
loop.run_until_complete(instructor.askQuestion()) 
loop.close() 



