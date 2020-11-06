from pyppeteer import launch
import asyncio
import json

class WebDriver:
	def __init__(self):
		pass

	async def openDriver(self):
		self.browser = await launch(headless = False, executablePath = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")
		self.page = await self.browser.newPage()
		# \self.page.setDefaultNavigationTimeout(60000)

	async def goToPage(self, url):
		await asyncio.wait([self.page.goto(url), self.page.waitForNavigation()])

	async def closeDriver(self):
		print('bye, closing driver')
		# await self.browser.close()

	async def getElementFromXid(self, xid):
		elem = await self.page.waitForSelector(f'[xid="{xid}"]')
		# a = "href"
		# prize_href = await self.page.evaluate(
        #         '(elem,a) => elem[a]',
        #         elem, a
		# )
		# print(prize_href)
		# props = await elem.getProperties()
		# print(props, 'hi')
		return elem
	
	async def getElementFromId(self, idParam):
		elem = await self.page.waitForSelector(f'[id="{idParam}"]')
		return elem


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
				// await page.evaluate(() => { element.attributes['xid'] = ref; });

				Array.from(element.attributes).forEach(x =>
					answer.attributes[x.name] = x.value
				);

				// if (answer.attributes['data-xid'] !== undefined) {
					// answer.xid = +answer.attributes['data-xid'];
				// }

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
							xid: ref,
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

	# TODO: fix this, selector might exist on prevoius page 
	async def click(self, selector):
		print("AWAITING CLICK")
		# self.page.waitForSelector(selector)
		# await self.page.click(selector) 
		await asyncio.wait([self.page.click(selector), self.page.waitForNavigation()])
		print("CLICKED")
		pages = await self.browser.pages()
		self.page = pages[len(pages) - 1]

	async def enter_text(self, selector, text):
		await self.page.type(selector, text)

	async def get_elements_db(self, save_to):
		dominfo = await self.getDOMInfo()

		with open(save_to + '.json', 'w') as outfile:
			json.dump(dominfo, outfile, sort_keys=True, indent=4)

		# dictionary with 2 keys: 'common_styles' and 'infos'
		return dominfo

async def func():
	a = WebDriver()
	await a.openDriver()
	await a.goToPage("https://www.amazon.com/gp/help/customer/display.html")
	c = await a.get_elements_db('test')
	elem = await a.getElementFromXid(16)
	g = await a.page.evaluate(elem)
	await asyncio.sleep(10000)

# loop = asyncio.new_event_loop()
# asyncio.set_event_loop(loop)
# result = loop.run_until_complete(func())
