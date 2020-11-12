import json
import sys
sys.path.append('..')
from representation.WebDriver import WebDriver
from representation.Agent import Agent
from time import sleep, process_time
import asyncio

GREEN = '\033[92m'
END = '\033[0m'

async def read_data():
  with open('../data/user-studies-data.json') as f:
    data = json.load(f)
    return data

async def slow_print(text):
  for ch in text:
    print(ch, end = '', flush=True)
    sleep(.05)
  print("")

def ask_and_confirm(question, variable, email=False):
  print(GREEN + question + END + "\n")
  confirm = "no"
  count = 0 
  while confirm == "no":
    count += 1 
    if count > 3: 
      print("(ALEX) : Sorry I'm unable to help you at this time, transferring to another agent.")
    resp = input("")
    if email:
      resp = resp.replace(" ", "").replace("at", "@")
    confirm = input(GREEN + f"Please confirm this is your " + variable + f" (yes/no): {resp}" + END + "\n")
  return resp

async def click(id):
  await agent.webdriver.page.waitForSelector(f'[id="{id}"]')
  await agent.webdriver.page.click(f'[id="{id}"]')

async def insert_text(text, id):
  await agent.webdriver.page.waitForSelector(f'[id="{id}"]')
  await agent.webdriver.page.type(f'[id={id}]', text)


async def parse_amazon(instr):
  if instr == "Read to user: Locate the claim code.":
    print("Please locate your gift card claim code \n")
  elif instr == "Go to https://www.amazon.com/gp/css/your-account-access":
    print("I'm going to go the the account access page on Amazon,")
    await agent.webdriver.goToPage(instr.split()[-1])
  elif instr == "Click Gift cards":
    print("and access the gift cards page.")
    await agent.webdriver.goToPage("https://www.amazon.com/gp/css/gc/balance?ref_=ya_d_c_gc")
  elif instr == "Ask user for email":
    print("I need to log you in to help you with your request.")
    ans = ask_and_confirm("What is your Amazon account email?", "email", True)
    await insert_text(ans, "ap_email")
  elif instr == "Ask user for password":
    ans = ask_and_confirm("What is your password?", "password")
    await insert_text(ans, "ap_password")
  elif instr == "Click Sign in":
    print("Thanks! I'm going to sign you in now \n")
    await click("signInSubmit")
    print("A 2-Factor Authentication Code was sent to you. Please verify it. \n")
    sleep(15)
  elif instr == "Click Redeem a gift card":
    print("The login was successful. I'm going to help you redeem your card now. \n")
    await agent.webdriver.goToPage("https://www.amazon.com/gc/redeem?ref_=gcui_b_e_r_c_d")
  elif instr == "Ask user for your claim code":
    ans = ask_and_confirm("What is your claim code?", "claim code", True)
    await insert_text(ans, "gc-redemption-input")
    # "Enter user-selected claim code in text field with Claim code",
  elif instr == "Click Apply to Your Balance":
    print("Ok, I'm going to apply that gift card code to your account, please give me 1 second. \n")
    await click("gc-redemption-apply-button")
    sleep(2)
    print("Your code has been applied. \n")

    request = input("Is there anything else I can help you with today? (yes / no) \n")
    if request == "yes": 
      request = input("(ALEX) : What else can I help you with today? \n")
      await map_request(request.lower())


  
async def parse_google(instr):
  if instr == "Go to mail.google.com":
    print("I'm going to need to login to your Gmail to do that")
    await agent.webdriver.goToPage("https://mail.google.com/")
  elif instr == "Ask user for email":
    ans = ask_and_confirm("What is your email address?", "email address")
    await insert_text(ans, "identifierId")  
  elif instr == "Click Next":
    await agent.webdriver.page.waitForSelector(f'[class="VfPpkd-RLmnJb"]')
    await agent.webdriver.page.click(f'[class="VfPpkd-RLmnJb"]')
  elif instr ==  "Ask user for password":
    ans = ask_and_confirm("What is your password?", "password")
    await agent.webdriver.page.waitForSelector(f'[class="VfPpkd-RLmnJb"]')
    await agent.webdriver.page.type(f'[class="whsOnd zHQkBf"]', ans)
    await agent.webdriver.page.waitForSelector(f'[class="VfPpkd-RLmnJb"]')
    await agent.webdriver.page.click(f'[class="VfPpkd-RLmnJb"]')
    print("(ALEX) : Signing you in now.")
    sleep(30)
  elif instr == "Click Help":
    await agent.webdriver.page.waitForSelector(f'[class="t7"]')
    await agent.webdriver.page.click(f'[class="t7"]')
    sleep(2)
    await agent.webdriver.page.waitForSelector(f'[aria-label="Send feedback"]')
    await agent.webdriver.page.click(f'[aria-label="Send feedback"]')
  elif instr == "Ask user for comments":
    ans = ask_and_confirm("What is your feedback?", "feedback to give")
    await agent.webdriver.page.type(f'[aria-label="Have feedback? We’d love to hear it, but please don’t share sensitive information. Have questions? Try help or support."]', ans)
    print("Submitting your feedback!")
    print("Your feedback was submitted.")
    request = voicedriver.listen(GREEN + "Is there anything else I can help you with today? (yes / no) \n" + END)
    if request == "yes": 
      request = voicedriver.listen(GREEN + "(ALEX) : What else can I help you with today? \n" + END)
      await map_request(request.lower())

async def parse_pinterest(instr):
  if instr == "Go to https://www.pinterest.com/login":
    print("I'm going to need to access your Pinterest account.")
    await agent.webdriver.goToPage("https://www.pinterest.com/login")
  elif instr == "Ask user for email Address":
    ans = ask_and_confirm("(ALEX) : What is your email?", "email", True)
    await insert_text(ans, "email")
  elif instr == "Ask user for Password":
    ans = ask_and_confirm("(ALEX) : What is your password?", "password")
    await insert_text(ans, "password")
  elif instr == "Click Log in":
    print("(ALEX) : Thank you. I'm going to log in for you now. ")
    await agent.webdriver.page.waitForSelector(f'[class="red SignupButton active"]')
    await agent.webdriver.page.click(f'[class="red SignupButton active"]')
  elif instr == "Click Ads in the top left corner":
    print("(ALEX) : I'm in your ad account now. ")
    await agent.webdriver.goToPage("https://ads.pinterest.com/advertiser/549761713038")
  elif instr == "Click Arrow button next to your name":
    print("(ALEX) : Your ad account number is " + GREEN + "549761713038" + END)
    sleep(2)
    request = input(GREEN + "Is there anything else I can help you with today? (yes / no) \n" + END)
    if request == "yes": 
      request = input(GREEN + "(ALEX) : What else can I help you with today? \n" + END)
      await map_request(request.lower())


async def parse_spotify(instr):
  if instr == "Go to http://www.spotify.com/account?_ga=2.170055017.893322237.1604048036-1104676808.1602105716":
    print("(ALEX) : I'm going to go to your spotify account from my side")
    await agent.webdriver.goToPage("http://www.spotify.com/account?_ga=2.170055017.893322237.1604048036-1104676808.1602105716")
  elif instr == "Ask user for email":
    print("(ALEX) : I need to log you in to help you with your request")
    ans = ask_and_confirm("(ALEX) : What is your email?", "email", True)
    await insert_text(ans, "login-username")
  elif instr == "Ask user for password":
    ans = ask_and_confirm("(ALEX) : What is your password?", "password")
    await insert_text(ans, "login-password")
  elif instr == "Click Log in":
    print("(ALEX) : Ok. I'm going to log in really quickly to sign you out.")
    await click("login-button")
  elif instr == "Click SIGN OUT EVERYWHERE.":
    print("(ALEX) : I've signed you out of all of your devices. ")
    await agent.webdriver.goToPage("https://accounts.spotify.com/revoke_sessions/?continue=https%3A%2F%2Fwww.spotify.com")
    request = input(GREEN + "Is there anything else I can help you with today? (yes / no) \n" + END)
    if request == "yes": 
      request = input(GREEN + "(ALEX) : What else can I help you with today? \n" + END)
      await map_request(request.lower())

async def parse_walmart(instr):
  if instr == "Go to https://www.walmart.com/account/signup":
    await agent.webdriver.goToPage("https://www.walmart.com/account/signup")
  elif instr == "Ask user for first name":
    print("I need some information to create your account")
    ans = ask_and_confirm("What is your first name?", "first name")
    await insert_text(ans, "first-name-su")  
  elif instr == "Ask user for last name":
    ans = ask_and_confirm("What is your last name?", "last name")
    await insert_text(ans, "last-name-su")    
  elif instr == "Ask user for email":
    ans = ask_and_confirm("(ALEX) : What is your email?", "email", True)
    await insert_text(ans, "email-su")
  elif instr == "Ask user for password":
    ans = ask_and_confirm("(ALEX) : What would you like your password to be?", "chosen password")
    await insert_text(ans, "password-su")
  elif instr == "Select Create Account":
    print("(ALEX) : OK. I'm creating your account now.")
    await agent.webdriver.page.waitForSelector(f'[class="button s-margin-top text-inherit"]')
    await agent.webdriver.page.click(f'[class="button s-margin-top text-inherit"]')
    sleep(3)
    print("(ALEX) : Congratulations. Your Walmart account has been created!")
    print("(ALEX) : You can now login to Walmart . ")
    request = input(GREEN + "Is there anything else I can help you with today? (yes / no) \n" + END)
    if request == "yes": 
      request = input(GREEN + "(ALEX) : What else can I help you with today? \n" + END)
      await map_request(request.lower())

async def map_request(request):
  data = await read_data()

  if "gift card" in request:
    print("(ALEX) : I'd be happy to help you redeem your Amazon gift card. Let's get started.")
    data = data["amazon1"]
    instructions = data["instructions"]
    for instr in instructions:
      await parse_amazon(instr)
  elif "feedback" in request:
    print("(ALEX) : That's very nice of you. I'd be happy to help you send Google feedback. Let's get started.")
    data = data["google3"]
    instructions = data["instructions"]
    for instr in instructions:
      await parse_google(instr)
  elif "account" in request and ("ad" in request):
    print("(ALEX) : I'd be happy to help you create an advertiser account on Pinterest. Let's get started.")
    data = data["pinterest1"]
    instructions = data["instructions"]
    for instr in instructions:
      await parse_pinterest(instr)
  elif "sign" in request or "log" in request and "out" in request and "spotify" in request:
    print("(ALEX) : I'm sorry to hear. I can help you sign out of all of your accounts. Let's get started.")
    data = data["spotify2"]
    instructions = data["instructions"]
    for instr in instructions:
      await parse_spotify(instr)
  elif ("create" in request or 'sign up' in request or 'signup' in request or 'sign-up' in request) and "walmart" in request and "account" in request:
    print("(ALEX) : I'd be happy to help you create a Walmart account. Let's get started.")
    data = data["walmart1"]
    instructions = data["instructions"]
    for instr in instructions:
      await parse_walmart(instr)
  else:
    request = input("(ALEX) : Sorry I can't service that request. Can you please clarify what you need help with? \n")
    await map_request(request.lower())


async def run():
  await agent.webdriver.openDriver()
  request = input(GREEN + "(ALEX) : Hi there! How may I help you today?" + END + "\n")
  await map_request(request.lower())



if __name__ == "__main__":
  webdriver = WebDriver()
  agent = Agent(webdriver)

  loop = asyncio.new_event_loop()
  asyncio.set_event_loop(loop)
  result = loop.run_until_complete(run())