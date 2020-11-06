import json
import sys
sys.path.append('..')
from representation.VoiceDriver import VoiceDriver
from representation.WebDriver import WebDriver
from representation.Agent import Agent
from time import sleep, process_time
import asyncio

async def read_data():
  with open('../data/user-studies-data.json') as f:
    data = json.load(f)
    return data

async def slow_print(text):
  for ch in text:
    print(ch, end = '', flush=True)
    sleep(.05)
  print("")

def create_voice_driver():
  return VoiceDriver()

def ask_and_confirm(question, email=False):
  confirm = "no"
  while confirm is "no":
    voicedriver.speak(question)
    resp = voicedriver.listen(question)
    if email:
      resp = resp.replace(" ", "").replace("at", "@")
    sleep(5)
    print(f"Did you mean to say (yes/no): {resp}")
    vd = create_voice_driver()
    vd.speak(f"Did you mean to say (yes/no): {resp}")
    confirm = vd.listen("").strip()
  return resp


async def click(id):
  await agent.webdriver.page.waitForSelector(f'[id="{id}"]')
  await agent.webdriver.page.click(f'[id="{id}"]')

async def insert_text(text, id):
  await agent.webdriver.page.waitForSelector(f'[id="{id}"]')
  await agent.webdriver.page.type(f'[id={id}]', text)


async def parse_amazon_one(instr):
  if instr == "Read to user: Locate the claim code.":
    print("Locate the claim code")
    voicedriver.speak("Locate the claim code")
  elif instr == "Go to https://www.amazon.com/gp/css/your-account-access":
    print("Taking you to your account access page")
    voicedriver.speak("Taking you to your account access page")
    await agent.webdriver.goToPage(instr.split()[-1])
  elif instr == "Click Gift cards":
    print("Clicking the Gift cards button")
    voicedriver.speak("Clicking the Gift cards button")
    await agent.webdriver.goToPage("https://www.amazon.com/gp/css/gc/balance?ref_=ya_d_c_gc")
  elif instr == "Ask user for email":
    print("I need to log you in to help you with your request")
    voicedriver.speak("I need to log you in to help you with your request")
    ans = ask_and_confirm("What is your email?", True)
    await insert_text(ans, "ap_email")
  elif instr == "Ask user for password":
    ans = ask_and_confirm("What is your password?")
    await insert_text(ans, "ap_password")
  elif instr == "Click Sign in":
    print("Signing you in now")
    voicedriver.speak("Signing you in now")
    await click("signInSubmit")
    sleep(15)
  elif instr == "Click Redeem a gift card":
    print("Clicking the redeem gift card button")
    voicedriver.speak("Clicking the redeem gift card button")
    await agent.webdriver.goToPage("https://www.amazon.com/gc/redeem?ref_=gcui_b_e_r_c_d")
  elif instr == "Read to user: Locate the claim code.":
    voicedriver.speak("Please locate your claim code")
    print("Please locate your claim code")
  elif instr == "Ask user for your claim code":
    ans = ask_and_confirm("What is your claim code?")
    await insert_text(ans, "gc-redemption-input")
    # "Enter user-selected claim code in text field with Claim code",
  elif instr == "Click Apply to Your Balance":
    voicedriver.speak("Applying the gift card to your account")
    print("Applying the gift card to your account")
    await click("gc-redemption-apply-button")
    sleep(10)

async def map_request(request):
  data = await read_data()

  if request == "i want to redeem an amazon gift card":
    data = data["amazon1"]
    instructions = data["instructions"]
    for instr in instructions:
      await parse_amazon_one(instr)
  elif request == "i want to track my amazon order":
    data = data["amazon2"]
    instructions = data["instructions"]
    print(instructions)
    # for instr in instructions:
    #   await parse_amazon2(instr)
  elif request == "i want to create a google account":
    data = data["google1"]
    instructions = data["instructions"]
    print(instructions)
  elif request == "i want to give google feedback":
    data = data["google2"]
    instructions = data["instructions"]
    print(instructions)
  elif request == "how do i create an advertiser account":
    data = data["pinterest1"]
    instructions = data["instructions"]
    print(instructions)
  elif request == "how do i create a campaign":
    data = data["pinterest2"]
    instructions = data["instructions"]
    print(instructions)
  elif request == "how do i edit one of my reviews":
    data = data["yelp1"]
    instructions = data["instructions"]
    print(instructions)
  elif request == "how do i remove a review i posted":
    data = data["yelp2"]
    instructions = data["instructions"]
    print(instructions)
  elif request == "how do i cancel or edit an order":
    data = data["walmart1"]
    instructions = data["instructions"]
    print(instructions)
  elif request == "how do i reset my password":
    data = data["walmart2"]
    instructions = data["instructions"]
    print(instructions)
  else:
    print("not found")


async def run():
  await agent.webdriver.openDriver()

  voicedriver.speak("How may I help you today?")
  request = voicedriver.listen("How may I help you today?")
  await map_request(request.lower())



if __name__ == "__main__":
  voicedriver = VoiceDriver()
  webdriver = WebDriver()
  agent = Agent(webdriver)

  loop = asyncio.new_event_loop()
  asyncio.set_event_loop(loop)
  result = loop.run_until_complete(run())