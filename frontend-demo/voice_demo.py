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

def print_and_say(text):
  print(text)
  voicedriver.speak(text)

def create_voice_driver():
  return VoiceDriver()

def ask_and_confirm(question, email=False):
  confirm = "no"
  while confirm == "no":
    voicedriver.speak(question)
    resp = voicedriver.listen(question)
    if email:
      resp = resp.replace(" ", "").replace("at", "@")
    print(f"Did you mean to say (yes/no): {resp}")
    vd = create_voice_driver()
    vd.speak(f"Did you mean to say: {resp}")
    confirm = vd.listen("").strip()
  return resp


async def click(id):
  await agent.webdriver.page.waitForSelector(f'[id="{id}"]')
  await agent.webdriver.page.click(f'[id="{id}"]')

async def insert_text(text, id):
  await agent.webdriver.page.waitForSelector(f'[id="{id}"]')
  await agent.webdriver.page.type(f'[id={id}]', text)


async def parse_amazon1(instr):
  if instr == "Read to user: Locate the claim code.":
    print_and_say("Locate the claim code")
  elif instr == "Go to https://www.amazon.com/gp/css/your-account-access":
    print_and_say("Taking you to your account access page")
    await agent.webdriver.goToPage(instr.split()[-1])
  elif instr == "Click Gift cards":
    print_and_say("Clicking the Gift cards button")
    await agent.webdriver.goToPage("https://www.amazon.com/gp/css/gc/balance?ref_=ya_d_c_gc")
  elif instr == "Ask user for email":
    print_and_say("I need to log you in to help you with your request")
    ans = ask_and_confirm("What is your email?", True)
    await insert_text(ans, "ap_email")
  elif instr == "Ask user for password":
    ans = ask_and_confirm("What is your password?")
    await insert_text(ans, "ap_password")
  elif instr == "Click Sign in":
    print_and_say("Signing you in now")
    await click("signInSubmit")
    print_and_say("Please verify Two Factor Authentication")
    sleep(15)
  elif instr == "Click Redeem a gift card":
    print_and_say("Clicking the redeem gift card button")
    await agent.webdriver.goToPage("https://www.amazon.com/gc/redeem?ref_=gcui_b_e_r_c_d")
  elif instr == "Ask user for your claim code":
    ans = ask_and_confirm("What is your claim code?")
    await insert_text(ans, "gc-redemption-input")
    # "Enter user-selected claim code in text field with Claim code",
  elif instr == "Click Apply to Your Balance":
    print_and_say("Applying the gift card to your account")
    await click("gc-redemption-apply-button")
    sleep(10)

async def parse_amazon2(instr):
  if instr == "Go to https://www.amazon.com/gp/css/your-orders-access":
    print_and_say("Taking you to your orders page")
    await agent.webdriver.goToPage("https://www.amazon.com/gp/css/your-orders-access")
  elif instr == "Ask user for email":
    print_and_say("I need to log you in to help you with your request")
    ans = ask_and_confirm("What is your email?", True)
    await insert_text(ans, "ap_email")
    await click("continue")
  elif instr == "Ask user for password":
    ans = ask_and_confirm("What is your password?")
    await insert_text(ans, "ap_password")
  elif instr == "Click Sign in":
    print_and_say("Signing you in now")
    await click("signInSubmit")
    print_and_say("Please verify Two Factor Authentication")
    sleep(15)
  elif instr == "Ask user for the order you want to track":
    ans = ask_and_confirm("Which order would you like to track?")
  elif instr == "Click Track Package by the user-selected order you want to track":
    print("tracking package")

async def parse_google1(instr):
  if instr == "Go to https://accounts.google.com/SignUp":
    print_and_say("Taking you to the sign up page")
    await agent.webdriver.goToPage("https://accounts.google.com/SignUp")
  elif instr == "Ask user for first name":
    print_and_say("I need some information to create your account")
    ans = ask_and_confirm("What is your first name")
    await insert_text(ans, "firstName")
  elif instr == "Ask user for last name":
    ans = ask_and_confirm("What is your last name")
    await insert_text(ans, "lastName")  
  elif instr == "Ask user for username":
    ans = ask_and_confirm("What username would you like", True)
    await insert_text(ans, "username")
  elif instr == "Ask user for password":
    ans = ask_and_confirm("What password would you like", True)
    await agent.webdriver.page.waitForSelector(f'[name="Passwd"]')
    await agent.webdriver.page.type(f'[name="Passwd"]', ans)
    print_and_say("Confirming your password")
    await agent.webdriver.page.waitForSelector(f'[name="ConfirmPasswd"]')
    await agent.webdriver.page.type(f'[name="ConfirmPasswd"]', ans)
  elif instr == "Click Next":
    print_and_say("Moving forward")
    await agent.webdriver.page.waitForSelector(f'[class="VfPpkd-LgbsSe VfPpkd-LgbsSe-OWXEXe-k8QpJ VfPpkd-LgbsSe-OWXEXe-dgl2Hf nCP5yc AjY5Oe DuMIQc qIypjc TrZEUc"]')
    await agent.webdriver.page.click(f'[class="VfPpkd-LgbsSe VfPpkd-LgbsSe-OWXEXe-k8QpJ VfPpkd-LgbsSe-OWXEXe-dgl2Hf nCP5yc AjY5Oe DuMIQc qIypjc TrZEUc"]')
    sleep(10)

async def parse_google2(instr):
  if instr == "Go to chrome://settings/":
    print_and_say("Taking you to your chrome settings")
    await agent.webdriver.goToPage("chrome://settings/")
  elif instr == "Click privacy and security":
    print_and_say("Taking you to your privacy settings")
    await agent.webdriver.goToPage("chrome://settings/privacy")
  elif instr == "Click Site settings":
    print_and_say("Taking you to your Site settings")
    await agent.webdriver.goToPage("chrome://settings/content")
  elif instr == "Click Protected Content":
    print_and_say("Taking you to your Protected Content")
    await agent.webdriver.goToPage("chrome://settings/content/protectedContent")
  elif instr == "Select the Turn off Allow sites to play protected content checkbox":
    print_and_say("Toggling Allow sites to play protected content")
    await click("control")

  
async def parse_google3(instr):
  if instr == "Go to mail.google.com":
    print_and_say("Taking you to gmail")
    await agent.webdriver.goToPage("https://mail.google.com/")
  elif instr == "Ask user for email":
    print_and_say("I need to log you in first")
    ans = ask_and_confirm("What is your email address?")
    await insert_text(ans, "identifierId")  
  elif instr == "Click Next":
    await agent.webdriver.page.waitForSelector(f'[class="VfPpkd-RLmnJb"]')
    await agent.webdriver.page.click(f'[class="VfPpkd-RLmnJb"]')
  elif instr ==  "Ask user for password":
    ans = ask_and_confirm("What is your password?")
    await agent.webdriver.page.waitForSelector(f'[class="VfPpkd-RLmnJb"]')
    await agent.webdriver.page.type(f'[class="whsOnd zHQkBf"]', ans)
    await agent.webdriver.page.waitForSelector(f'[class="VfPpkd-RLmnJb"]')
    await agent.webdriver.page.click(f'[class="VfPpkd-RLmnJb"]')
  elif instr == "Click Help":
    await agent.webdriver.page.waitForSelector(f'[class="t7"]')
    await agent.webdriver.page.click(f'[class="t7"]')
    sleep(2)
    await agent.webdriver.page.waitForSelector(f'[aria-label="Send feedback"]')
    await agent.webdriver.page.click(f'[aria-label="Send feedback"]')
  elif instr == "Ask user for comments":
    ans = ask_and_confirm("What is your feedback?")
    await agent.webdriver.page.waitForSelector(f'[aria-label="Have feedback? We’d love to hear it, but please don’t share sensitive information. Have questions? Try help or support."]')
    await agent.webdriver.page.type(f'[aria-label="Have feedback? We’d love to hear it, but please don’t share sensitive information. Have questions? Try help or support."]', ans)
  elif instr == " At the bottom right, click Send.":
    print_and_say("Submitting your feedback!")
    await agent.webdriver.page.waitForSelector(f'[key="send"]')
    await agent.webdriver.page.click(f'[key="send"]')

async def parse_pinterest1(instr):
      #   "Go to pinterest.com",
      # "Ask user for email Address",
      # "Enter user-selected Email Address in text field with Email Address text",
      # "Ask user for Password",
      # "Enter user-selected password in text field with password text",
      # "Click Log in",
      # "Click Ads in the top left corner",
      # "select Overview",
      # "Click Arrow button next to your name",
      # "Click Create new ad account ",
      # "Ask user for a name",
      # "Enter the user-selected name in text field with name",
      # "Click Save"
  if instr == "Go to https://www.pinterest.com/login":
    print_and_say("Taking you to your Pinterest account")
    await agent.webdriver.goToPage("https://www.pinterest.com/login")
  elif instr == "Ask user for email Address":
    print_and_say("I need to log you in to help you with your request")
    ans = ask_and_confirm("What is your email?", True)
    await insert_text(ans, "email")
  elif instr == "Ask user for Password":
    ans = ask_and_confirm("What is your password?")
    await insert_text(ans, "password")
  elif instr == "Click Log in":
    print_and_say("Logging you in")
    await agent.webdriver.page.waitForSelector(f'[class="red SignupButton active"]')
    await agent.webdriver.page.click(f'[class="red SignupButton active"]')
  elif instr == "Click Ads in the top left corner":
    print_and_say("Taking you to your Ad manager")
    await agent.webdriver.goToPage("https://ads.pinterest.com/advertiser/549761713038")
  elif instr == "Click Arrow button next to your name":
    await agent.webdriver.page.waitForSelector(f'[class="RCK Hsu USg adn CCY czT F10 xD4 fZz hUC bmw qJc hNT BG7 NTm KhY"]')
    await agent.webdriver.page.click(f'[class="RCK Hsu USg adn CCY czT F10 xD4 fZz hUC bmw qJc hNT BG7 NTm KhY"]')

async def parse_pinterest2(instr):
  if instr == "Go to http://pinterest.com/password/reset":
    print_and_say("Taking you to the Pinterest password reset page")
    await agent.webdriver.goToPage("http://pinterest.com/password/reset")
  elif instr == "Ask user for email":
    print_and_say("I need your email address to help you")
    ans = ask_and_confirm("What is your email?", True)
    await insert_text(ans, "userQuery")
  elif instr == "Click Send a password reset email":
    print_and_say("Sending you a password reset email")
    await agent.webdriver.page.waitForSelector(f'[class="RCK Hsu USg adn CCY czT Vxj aZc Zr3 hA- Il7 Jrn hNT BG7 gn8 L4E kVc iyn"]')
    await agent.webdriver.page.click(f'[class="RCK Hsu USg adn CCY czT Vxj aZc Zr3 hA- Il7 Jrn hNT BG7 gn8 L4E kVc iyn"]')
  elif instr == "Read to User: Check the email address connected to your account for a password reset email":
    print_and_say("Check the email address connected to your account for a password reset email")
    sleep(10)

async def parse_spotify1(instr):
  if instr == "Go to http://www.spotify.com/account?_ga=2.170055017.893322237.1604048036-1104676808.1602105716":
    print_and_say("Taking you to your spotify account")
    await agent.webdriver.goToPage("http://www.spotify.com/account?_ga=2.170055017.893322237.1604048036-1104676808.1602105716")
  elif instr == "Ask user for email":
    print_and_say("I need to log you in to help you with your request")
    ans = ask_and_confirm("What is your email?", True)
    await insert_text(ans, "login-username")
  elif instr == "Ask user for password":
    ans = ask_and_confirm("What is your password?")
    await insert_text(ans, "login-password")
  elif instr == "Click Log in":
    print_and_say("Logging you in")
    await click("login-button")
  elif instr == "Click EDIT PROFILE.":
    print_and_say("Taking you to edit your profile")
    await agent.webdriver.goToPage("https://www.spotify.com/account/profile/")
  elif instr == "ask User for new email address":
    ans = ask_and_confirm("What is your new email address?", True)
    await insert_text(ans, "email")
  elif instr ==  "Click SAVE PROFILE.":
    print_and_say("Saving these changes")
    await agent.webdriver.page.waitForSelector(f'[class="Button-sc-8cs45s-0 gBYMyb"]')
    await agent.webdriver.page.click(f'[class="Button-sc-8cs45s-0 gBYMyb"]')
    

async def parse_spotify2(instr):
  if instr == "Go to http://www.spotify.com/account?_ga=2.170055017.893322237.1604048036-1104676808.1602105716":
    print_and_say("Taking you to your spotify account")
    await agent.webdriver.goToPage("http://www.spotify.com/account?_ga=2.170055017.893322237.1604048036-1104676808.1602105716")
  elif instr == "Ask user for email":
    print_and_say("I need to log you in to help you with your request")
    ans = ask_and_confirm("What is your email?", True)
    await insert_text(ans, "login-username")
  elif instr == "Ask user for password":
    ans = ask_and_confirm("What is your password?")
    await insert_text(ans, "login-password")
  elif instr == "Click Log in":
    print_and_say("Logging you in")
    await click("login-button")
  elif instr == "Click SIGN OUT EVERYWHERE.":
    print_and_say("Signing you out everywhere")
    await agent.webdriver.goToPage("https://accounts.spotify.com/revoke_sessions/?continue=https%3A%2F%2Fwww.spotify.com")

async def parse_walmart1(instr):
  if instr == "Go to https://www.walmart.com/account/signup":
    print_and_say("Taking you to create a walmart account")
    await agent.webdriver.goToPage("https://www.walmart.com/account/signup")
  elif instr == "Ask user for first name":
    print_and_say("I need some information to create your account")
    ans = ask_and_confirm("What is your first name?")
    await insert_text(ans, "first-name-su")  
  elif instr == "Ask user for last name":
    ans = ask_and_confirm("What is your last name?")
    await insert_text(ans, "last-name-su")    
  elif instr == "Ask user for email":
    ans = ask_and_confirm("What is your email?", True)
    await insert_text(ans, "email-su")
  elif instr == "Ask user for password":
    ans = ask_and_confirm("What is your password?")
    await insert_text(ans, "password-su")
  elif instr == "Select Create Account":
    print_and_say("Creating your account")
    await agent.webdriver.page.waitForSelector(f'[class="button s-margin-top text-inherit"]')
    await agent.webdriver.page.click(f'[class="button s-margin-top text-inherit"]')
    sleep(10)


async def parse_walmart2(instr):
  if instr == "Go to https://www.walmart.com/account/forgotpassword":
    print_and_say("Taking you to your walmart account")
    await agent.webdriver.goToPage("https://www.walmart.com/account/forgotpassword")
  elif instr == "Ask user for email address":
    print_and_say("I need to log you in to help you with your request")
    ans = ask_and_confirm("What is your email?", True)
    await insert_text(ans, "email-fp")
    await click("forgot-pwd-continue-btn")
  elif instr == "Read to user: Check your email for the code. Be sure to check your junk or spam folder.":
    print_and_say("Check your email for the code. Be sure to check your junk or spam folder.")
  elif instr == "Ask user for code":
    sleep(5)
    ans = ask_and_confirm("What is the verification code?", True)
    await insert_text(ans, "code-vrc")
  elif instr ==  "Select Submit Code":
    print_and_say("submitting verification code")
    await agent.webdriver.page.waitForSelector(f'[class="button m-margin-top"]')
    await agent.webdriver.page.click(f'[class="button m-margin-top"]')
    await click("skip-page-submit")
        

async def map_request(request):
  data = await read_data()

  if request == "i want to redeem an amazon gift card":
    data = data["amazon1"]
    instructions = data["instructions"]
    for instr in instructions:
      await parse_amazon1(instr)
  elif request == "i want to track my amazon order":
    data = data["amazon2"]
    instructions = data["instructions"]
    for instr in instructions:
      await parse_amazon2(instr) 
  elif request == "i want to send google feedback":
    data = data["google3"]
    instructions = data["instructions"]
    for instr in instructions:
      await parse_google3(instr)
  elif request == "i want to create a google account":
    data = data["google1"]
    instructions = data["instructions"]
    for instr in instructions:
      await parse_google1(instr)
  elif request == "i want to change my protected content":
    data = data["google2"]
    instructions = data["instructions"]
    for instr in instructions:
      await parse_google2(instr)
  elif request == "how do i create an advertiser account":
    data = data["pinterest1"]
    instructions = data["instructions"]
    for instr in instructions:
      await parse_pinterest1(instr)
  elif request == "how do i reset my password":
    data = data["pinterest2"]
    instructions = data["instructions"]
    for instr in instructions:
      await parse_pinterest2(instr)
  elif request == "how do i change my email address":
    data = data["spotify1"]
    instructions = data["instructions"]
    for instr in instructions:
      await parse_spotify1(instr)
  elif request == "how do i logout of spotify":
    data = data["spotify2"]
    instructions = data["instructions"]
    for instr in instructions:
      await parse_spotify2(instr)
  elif request == "how do i create a walmart account":
    data = data["walmart1"]
    instructions = data["instructions"]
    for instr in instructions:
      await parse_walmart1(instr)
  elif request == "how do i reset my walmart password":
    data = data["walmart2"]
    instructions = data["instructions"]
    for instr in instructions:
      await parse_walmart2(instr)
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