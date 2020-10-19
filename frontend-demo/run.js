const puppeteer = require('puppeteer');
const readline = require('readline');


const black = "\x1b[1m\x1b[30m%s\x1b[0m"
const red = "\x1b[1m\x1b[31m%s\x1b[0m"
const green = "\x1b[1m\x1b[32m%s\x1b[0m"
const yellow = "\x1b[1m\x1b[1m\x1b[33m%s\x1b[0m"
const blue = "\x1b[34m%s\x1b[0m"
const magenta = "\x1b[1m\x1b[35m%s\x1b[0m"
const cyan = "\x1b[1m\x1b[36m%s\x1b[0m"
const white = "\x1b[1m\x1b[37m%s\x1b[0m"


CHROME_EXEC_PATH = '/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome'; 
HEADLESS = true; 

async function getUserInput(query) {
  const rl = readline.createInterface({
      input: process.stdin,
      output: process.stdout,
  });

  return new Promise(resolve => rl.question(query, ans => {
      rl.close();
      resolve(ans);
  }))
}

async function greet(){
  console.log(green, "Hey there, I'm Alex, and I'm here to help you with Amazon Customer Support!\n Type QUIT to quit, otherwise feel free to ask any questions!\n")
}

async function askQuestion() {
  const inp = await getUserInput("(Alex): How can I help you today?\n");
  if (inp === 'QUIT'){
    console.log(cyan, "Bye!")
    readline.close();
  } else {
    await search(inp);
    askQuestion();
  }  
}

// async function pythonParse(page, step) {
  // const spawn = require("child_process").spawn;
  // const pythonProcess = spawn('python', ["./parse.py", text, 'remove_prepositions']);
  // console.log("before await")
  // let data = "";
  // for await (const chunk of pythonProcess.stdout) {
  //   data += chunk;
  // }
  // console.log("result is ", data)

  // if (link) {
  //   await page.goto(link);
  //   await page.screenshot({path: 'test.png'});
  //   console.log("Taking you to ", link)
  // } else{
  //   console.log(text)
  //   console.log("bold is ", bold)
  // }
// }

async function parseHelpContent(step) {
  const KEYWORDS = ["select", "go to", "enter", "click"]
  let res = [];
  let keywordIndices = [];
  let keywordIndex = -1;
  for (var keyword of KEYWORDS){
    keywordIndex = step.toLowerCase().trim().indexOf(keyword + ' ') 
    if(keywordIndex  >= 0){
      keywordIndices.push(keywordIndex);
    }
  }
  for (var i = 0; i < keywordIndices.length - 1; i++){
    res.push(step.substr(keywordIndices[i], keywordIndices[i+1]));
  }
  res.push(step.substr(keywordIndices[keywordIndices.length-1], step.length + 1));
  if (res.length == 0){
    return [step];
  }
  return res;
}

function delay(delayInms) {
  return new Promise(resolve => {
    setTimeout(() => {
      resolve(2);
    }, delayInms);
  });
}


async function slowPrint(sentence){
  for (var ch of sentence){
    await delay(50)
    process.stdout.write(ch);
  }
  console.log("")
}

async function stepHelpContent(page, step) {
  let text = step.toString().replace(/\n\s*\n/g, '\n').split('\n')[0];
  let actions = await parseHelpContent(text);
  for (var action of actions) {
    action = action.trim().replace('.', '');
    if(action.substr(0, "go to".length).toLowerCase() == "go to"){
      console.log(green, `Sending "${action.substr("go to".length, action.length)}" to model`);
      await slowPrint(`Taking you to ${action.substr("go to".length, action.length)}\n`);
    } else if(action.substr(0, "select".length).toLowerCase() == "select"){
      console.log(green, `Sending "${action.substr("select".length, action.length)}" to model`);
      await slowPrint(`Selecting "${action.substr("select".length, action.length)}"\n`);
    } else if(action.substr(0, "click".length).toLowerCase() == "click"){
      console.log(green, `Sending "${action.substr("click".length, action.length)}" to model`);
      await slowPrint(`Clicking "${action.substr("click".length, action.length)}"\n`);
    } else if(action.substr(0, "enter".length).toLowerCase() == "enter"){
      console.log(green, `Sending "${action.substr("enter".length, action.length)}" to model`);
      await slowPrint(`Please enter "${action.substr("enter".length, action.length)}": \n`);
      const enteredValue = await getUserInput("");
      await slowPrint(`Filling in "${enteredValue}" for "${action.substr("enter".length, action.length)}"\n`)
    } else{
      await slowPrint(action + "\n")
    }
  }
}

async function expandSearch(searchUri) {
  const browser = await puppeteer.launch({headless: HEADLESS, executablePath: CHROME_EXEC_PATH});
  const page = await browser.newPage();
  await page.goto(searchUri);
  let searchResults = await page.evaluate(() => {
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
  });

  let recurseSearch = []
  for (var i = 0; i < searchResults.length; i++){
    if (searchResults[i][1]){
      recurseSearch.push([searchResults[i][0], searchResults[i][1]]);
    } else{
      // console.log(searchResults[i][0].toString().replace(/\n\s*\n/g, '\n'));
    }
  }
  
  if (recurseSearch && recurseSearch.length > 0){
    console.log("\nFind out more about: ");
    for (var i = 0; i < recurseSearch.length; i++){
      console.log(`${i+1}. ` + recurseSearch[i][0].toString().replace(/\n\s*\n/g, '\n'));
    }
    let choice = selectResponse(recurseSearch, recurseSearch.length, true);
    if (choice === "QUIT" || choice === '') {
      browser.close(); 
      return;
    }
    await expandSearch(recurseSearch[choice][1]);
  } else{
    for (var i = 0; i < searchResults[0][2].length; i++) {
      await stepHelpContent(page, searchResults[0][2][i])
      // console.log("the step is", searchResults[0][2][i].toString().replace(/\n\s*\n/g, '\n').split('\n')[0])
      // console.log(searchResults[0][2][i][1])
    }
  }

  browser.close();
}

async function selectResponse(searchResults, numResults, viewAll = false) {
  let choice = -1;
  if (viewAll){
    choice = await getUserInput("\n Which would you like to learn more about (QUIT to quit)? \n");
  } else {
    if (numResults == 0){
      await slowPrint("Sorry, we couldn't find what you were looking for!\n");
    } else if(numResults == 1){
      choice = 0;
    } else if(numResults == 2){
      await slowPrint("The top search results are:\n");
      console.log(green, `1. ${searchResults[0][0]}, \n2. ${searchResults[1][0]}\n`);
      choice = await getUserInput("Which would you like more information on (1 or 2)? ")
    } else{
      await slowPrint("The top 3 search results are:\n")
      console.log(green, `1. ${searchResults[0][0]}, \n2. ${searchResults[1][0]}, \n3. ${searchResults[2][0]}\n`);
      choice = await getUserInput("Which would you like more information on (1, 2, 3)? ")
    }
  }
  if (choice === "QUIT") {
    return choice;
  } else{
    return choice - 1
  } 
}

async function search(query) {
    const browser = await puppeteer.launch({headless: HEADLESS, executablePath: CHROME_EXEC_PATH});
    const page = await browser.newPage();

    let formattedQuery = query.replace(/\s+/g, '+');
    let searchQuery = `https://www.amazon.com/gp/help/customer/display.html/ref=hp_search_rd_gw?__mk_en_US=%C3%85M%C3%85%C5%BD%C3%95%C3%91&help_keywords=${formattedQuery}&search=true&nodeId=508510&kwHidden=true&sprefix=&locale=en_US`;
    await page.goto(searchQuery);

    let searchResults = await page.evaluate(() => {
      let elements = document.getElementsByClassName('a-link-normal');
      let data = [];
  
      for (var element of elements) {
        data.push([element.textContent.trim(), element.href])
      }
      return data;
    });
    let choice = -1;
    let searchAgain = "y";
    while (searchAgain == "y"){
      choice = await selectResponse(searchResults, searchResults.length);
      if (choice >= 0) {
        await expandSearch(searchResults[choice][1]);
        searchAgain = await getUserInput("\nWould you like to revisit the search results (y/n)? ")
      }
    }
    browser.close();
}

async function run(){
  await greet();
  askQuestion();
}

run();