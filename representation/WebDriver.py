from pyppeteer import launch
import asyncio
import json

class WebDriver:
	def __init__(self):
		pass

	async def openDriver(self):
		self.browser = await launch(headless = False, executablePath = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")
		self.pages = await self.browser.pages()
		self.page = self.pages[0]
		self.page.setDefaultNavigationTimeout(60000)

	async def goToPage(self, url):
		await self.page.goto(url)

	async def closeDriver(self):
		await self.browser.close()

	async def getDOMInfo(self):
		final_return = await self.page.evaluate('''async () => {
			var getDOMInfoOfElement = async function(element) {
				if (['STYLE', 'SCRIPT'].includes(element.tagName)
					|| element instanceof Comment) return null;
				let rect = element.getBoundingClientRect();
				let ref = allAnswers.length;
				let answer = {
					ref: ref, children: [],
					tag: element.tagName,
					left: rect.left, top: rect.top,
					width: rect.width, height: rect.height,
					id: element.getAttribute('id'),
					classes: element.getAttribute('class'),
					attributes: {}, styles: {}, selector: '', xid: ref
				};
				allAnswers.push(answer);
				// Record attributes
				element.setAttribute('xid', ref);

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
		}''')
		return final_return


	async def click(self, selector) :
		await self.page.click(selector)
		await self.page.waitForNavigation()

	async def enter_text(self, selector, text):
		await self.page.type(selector, text)
		await self.page.waitForNavigation()


	async def get_elements_db(self, save_to):
		dominfo = await self.getDOMInfo()

		with open(save_to + '.json', 'w') as outfile:
			json.dump(dominfo, outfile, sort_keys=True, indent=4)

		# dictionary with 2 keys: 'common_styles' and 'infos'
		return dominfo

url = 'https://www.amazon.com/gp/help/customer/display.html/ref=help_search_1-1?ie=UTF8&nodeId=201936940&qid=1603260667&sr=1-1'

webdriver = WebDriver()

loop = asyncio.get_event_loop()
loop.run_until_complete(webdriver.openDriver())
loop.run_until_complete(webdriver.goToPage(url))
result = loop.run_until_complete( webdriver.get_elements_db('sample-rep2'))
loop.run_until_complete( webdriver.closeDriver())

loop.close()



