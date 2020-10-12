const puppeteer = require('puppeteer');
const readline = require('readline').createInterface({
  input: process.stdin,
  output: process.stdout
});
const prompt = require('prompt-sync')();

CHROME_EXEC_PATH = '/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome'; 
HEADLESS = false; 


console.log("Hey there, I'm Alex, and I'm here to help you with Amazon Customer Support!\n\
  Type QUIT to quit, otherwise feel free to ask any questions!");

function askQuestion() {
  readline.question('(Alex): How can I help you today?\n ', async function(question){
    if (question == 'QUIT') {
      console.log("Bye!")
      readline.close();
    } else {
      await search(question);
      askQuestion();
    }  
  });
}

async function expandSearch(searchUri) {
  const browser = await puppeteer.launch({headless: HEADLESS, executablePath: CHROME_EXEC_PATH});
  const page = await browser.newPage();
  await page.goto(searchUri);
  let searchResults = await page.evaluate(() => {
    let elements = document.getElementsByClassName('help-content');
    let data = [];

    for (var element of elements) {
      data.push([element.innerText.trim(), element.href])
    }
    return data;
  });
  console.log(searchResults[0].toString().replace(/\n\s*\n/g, '\n'));
  browser.close();
}

function selectResponse(searchResults, numResults) {
  let choice = -1;
  if (numResults == 0){
    console.log("Sorry, we couldn't find what you were looking for!");
  } else if(numResults == 1){
    choice = 0;
  } else if(numResults == 2){
    console.log(`The top search results are: \n1. ${searchResults[0][0]}, \n2. ${searchResults[1][0]}`);
    choice = prompt("Which would you like more information on (1 or 2), or 0 for ask a new question? ")
  } else{
    console.log(`The top 3 search results are: \n1. ${searchResults[0][0]}, \n2. ${searchResults[1][0]}, \n3. ${searchResults[2][0]}`);
    choice = prompt("Which would you like more information on (1, 2, 3), or 0 for ask a new question? ")
  }
  return choice - 1
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
      choice = selectResponse(searchResults, searchResults.length);
      if (choice >= 0) {
        await expandSearch(searchResults[choice][1]);
        searchAgain = prompt("\nWould you like to revisit the search results (y/n)? ")
      }
    }
    browser.close();
}

askQuestion();