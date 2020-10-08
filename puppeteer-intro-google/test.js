const puppeteer = require('puppeteer');
const fs = require('fs')
//const SEARCH_URI = 'https://www.google.com/search?hl=en&tbm=shop&sxsrf=ALeKk00rPcy0SI31kpLp58SY2eH1UIuaGQ%3A1602030091711&psb=1&q=macbook&oq=macbook&gs_lcp=Cgtwcm9kdWN0cy1jYxADMgQIIxAnMggIABCxAxCDATIICAAQsQMQgwEyCAgAELEDEIMBMggIABCxAxCDATICCAAyCAgAELEDEIMBMgIIADICCAAyCAgAELEDEIMBOgQIABAYOgYIABAHEB46BAgAEEM6BAgAEAM6BwgjEOoCECdQsBNY9DZg4ThoAXAAeACAAaUCiAG2DJIBBTAuNi4zmAEAoAEBqgEPcHJvZHVjdHMtY2Mtd2l6sAECwAEB&sclient=products-cc';
const SEARCH_URI = 'https://www.google.com/search?hl=en&tbm=shop&sxsrf=ALeKk00c98MtDd4P0jKm838xU6LlzV5hMg%3A1602098719641&psb=1&q=chromebook&oq=chromebook&gs_lcp=Cgtwcm9kdWN0cy1jYxADMggIABCxAxCDATIICAAQsQMQgwEyCAgAELEDEIMBMggIABCxAxCDATIICAAQsQMQgwEyCAgAELEDEIMBMggIABCxAxCDATIICAAQsQMQgwEyCAgAELEDEIMBMggIABCxAxCDAToECAAQDToECCMQJzoCCABQ2PcOWNmAD2D3gQ9oAHAAeACAAXKIAbQGkgEDOS4xmAEAoAEBqgEPcHJvZHVjdHMtY2Mtd2l6wAEB&sclient=products-cc';

(async () => {
  const browser = await puppeteer.launch();
  const page = await browser.newPage();
  await page.goto(SEARCH_URI);

  let file1 = await page.evaluate(() => {
    // let elements = document.getElementsByClassName('sh-dr__g');
    // let elements = document.getElementsByClassName('sh-dlr__list-result');
    let data = [];
    let names = document.getElementsByClassName('VZTCjd') // name
    let descriptions = document.querySelectorAll('div[class="hBUZL"]'); // descriptions
    let prices = document.getElementsByClassName('h1Wfwb') // price
    let n = Math.min(names.length, descriptions.length, prices.length);
    for (var i = 0; i < n; i++) {
      data.push(`Name: ${names[i].textContent}` + '\n' + `Price: ${prices[i].textContent}` + '\n' + `Description: ${descriptions[i].textContent}`)
    }
    return data;
  });

  let file2 = await page.evaluate(() => {
    let elements = document.getElementsByClassName('sh-dr__g');
    let data = [];

    for (var element of elements) {
      data.push(element.textContent)
    }
    return data;
  });

  await fs.writeFile('product-description2.txt',
    file1.join('\n\n'),
    function (err) { console.log(err ? 'Error :'+err : 'File written!') }
  );

  await fs.writeFile('filters2.txt',
    file2.join('\n\n'),
    function (err) { console.log(err ? 'Error :'+err : 'File written!') }
  );

  browser.close();
})();