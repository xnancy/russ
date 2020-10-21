const puppeteer = require('puppeteer');
const optimalSelect = require('optimal-select'); 
const fs = require('fs') ;

// TODO FIX SELECTOR 
async function getDOMInfo(page) {
	var selectf = optimalSelect.select; 
	await page.exposeFunction("selectf",selectf);
	const final_return = await page.evaluate(async () => {
		var getDOMInfoOfElement = async function(element) {
			if (['STYLE', 'SCRIPT'].includes(element.tagName)
				|| element instanceof Comment) return null;
			let rect = element.getBoundingClientRect();
			let ref = allAnswers.length;
			var sel = window.selectf(element); 
			let answer = {
				ref: ref, children: [],
				tag: element.tagName,
				left: rect.left, top: rect.top,
				width: rect.width, height: rect.height,
				id: element.getAttribute('id'),
				classes: element.getAttribute('class'),
				attributes: {}, styles: {}, selector: sel, 
			};
			allAnswers.push(answer);
			// Record attributes
			Array.from(element.attributes).forEach(x =>
				answer.attributes[x.name] = x.value
			);
			if (answer.attributes['data-xid'] !== undefined) {
				answer.xid = +answer.attributes['data-xid'];
			}
			// Record styles
			let computedStyle = window.getComputedStyle(element);
			for (let idx = 0; idx < computedStyle.length; idx++) {
				answer.styles[computedStyle[idx]] = computedStyle[computedStyle[idx]];
			}
			// For <input>, also add input type and value
			if (element instanceof HTMLInputElement) {
				let inputType = element.type;
				answer.type = inputType;
				if (inputType === 'checkbox' || inputType === 'radio') {
				answer.value = element.checked;
				} else {
				answer.value = element.value;
				}
			} else if (element instanceof HTMLTextAreaElement) {
				answer.value = element.value;
			}
			// Record visibility
			var topEl = document.elementFromPoint(
				answer.left + (element.offsetWidth || 0) / 2,
				answer.top + (element.offsetHeight || 0) / 2);
			answer.topLevel = (topEl !== null && (topEl.contains(element) || element.contains(topEl)));
			answer.hidden = ((element.offsetParent === null && element.tagName !== 'BODY')
				|| element.offsetWidth === 0 || element.offsetHeight === 0);
			// Traverse children
			if (element.tagName == 'SVG') {
				// Don't traverse anymore
				answer.text = '';
			} else {
				// Read the children
				let filteredChildNodes = [], textOnly = true;
				element.childNodes.forEach(function (child) {
				if (child instanceof Text) {
					if (!/^\s*$/.test(child.data)) {
					filteredChildNodes.push(child);
					}
				} else if (child instanceof Element) {
					filteredChildNodes.push(child);
					textOnly = false;
				}
				});
				if (textOnly) {
				answer.text = filteredChildNodes.map(function (x) {
					return x.data.trim();
				}).join(' ');
				} else {
				filteredChildNodes.forEach(async function (child) {
					if (child instanceof Text) {
					let range = document.createRange();
					range.selectNode(child);
					let childRect = range.getBoundingClientRect(), childText = child.data.trim();
					if (rect.width > 0 && rect.height > 0 && childText) {
						let childRef = allAnswers.length;
						allAnswers.push({
						ref: allAnswers.length,
						tag: "t",
						left: childRect.left, top: childRect.top,
						width: childRect.width, height: childRect.height,
						text: childText,
						});
						answer.children.push(childRef);
					}
					} else {
					child = await getDOMInfoOfElement(child);
					if (child !== null)
						answer.children.push(child.ref);
					}
				});
				}
			}
			return answer;
		}; 
		let allAnswers = [];
		await getDOMInfoOfElement(document.body);
		let commonStyles = {};
		for (let x in allAnswers[0].styles) {
		commonStyles[x] = allAnswers[0].styles[x];
		}
		allAnswers.forEach(function (item) {
		if (!(item.styles)) return;
		let filtered = {};
		for (let x in item.styles) {
			if (item.styles[x] != commonStyles[x])
			filtered[x] = item.styles[x];
		}
		item.styles = filtered;
		});
		return {'common_styles': commonStyles, 'info': allAnswers};
	});
	return final_return; 
  }

async function get_elements(page, browser, url) {
    try {
		dominfo = await getDOMInfo(page); 
		// stringify 
		dominfo = JSON.stringify(dominfo); 

		// write JSON string to a file
		fs.writeFile(url.replace(/\//g, '-') + '.json', dominfo, (err) => {
			if (err) {
				throw err;
			}
		});
		// \\await browser.close();
	} catch (err) {
		console.error(err);
	}
}

(async function main() {
	url = 'https://www.amazon.com/gp/help/customer/display.html/ref=help_search_1-1?ie=UTF8&nodeId=201936940&qid=1603260667&sr=1-1'

	const browser = await puppeteer.launch({headless:false, executablePath: '/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome'});
	const [page] = await browser.pages();
	page.setDefaultNavigationTimeout(60000);
	
	await page.goto(url, { waitUntil: 'networkidle0' });
	
	get_elements(page, browser,url); 
})(); 



