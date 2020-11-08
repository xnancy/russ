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
  # print(text)
  voicedriver.speak(text)

def create_voice_driver():
  return VoiceDriver()

def ask_and_confirm(question, variable, email=False):
  confirm = "no"
  count = 0 
  while confirm == "no":
    count += 1 
    if count > 3: 
      print("(ALEX) : Sorry I'm unable to help you at this time, transferring to another agent.")
    voicedriver.speak(question)
    resp = voicedriver.listen(question)
    if email:
      resp = resp.replace(" ", "").replace("at", "@")
    # print(f"Please confirm this is your " + variable + " (yes/no): {resp}")
    vd = create_voice_driver()
    vd.speak(f"Please confirm this is your " + variable + " (yes/no): " + str(resp))
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
    return 
    # print_and_say("Locate the claim code")
  elif instr == "Go to https://www.amazon.com/gp/css/your-account-access":
    print_and_say("I'm going to go the the account access page on Amazon,")
    await agent.webdriver.goToPage(instr.split()[-1])
  elif instr == "Click Gift cards":
    print_and_say("and access the gift cards page.")
    await agent.webdriver.goToPage("https://www.amazon.com/gp/css/gc/balance?ref_=ya_d_c_gc")
  elif instr == "Ask user for email":
    print_and_say("I need to log you in to help you with your request. ")
    ans = ask_and_confirm("What is your Amazon account email?", "email", True)
    await insert_text(ans, "ap_email")
  elif instr == "Ask user for password":
    ans = ask_and_confirm("What is your password?", "password")
    await insert_text(ans, "ap_password")
  elif instr == "Click Sign in":
    print_and_say("Thanks! I'm going to sign you in now")
    await click("signInSubmit")
    print_and_say("A 2-Factor Authentication Code was sent to you. Please verify it.")
    sleep(15)
  elif instr == "Click Redeem a gift card":
    print_and_say("The login was successful. I'm going to help you redeem your card now.")
    await agent.webdriver.goToPage("https://www.amazon.com/gc/redeem?ref_=gcui_b_e_r_c_d")
  elif instr == "Ask user for your claim code":
    ans = ask_and_confirm("What is your claim code?", "claim code")
    await insert_text(ans, "gc-redemption-input")
    # "Enter user-selected claim code in text field with Claim code",
  elif instr == "Click Apply to Your Balance":
    print_and_say("Ok, I'm going to apply that gift card code to your account, please give me 1 second.")
    await click("gc-redemption-apply-button")
    sleep(2)
    print_and_say("Your code has been applied.")

    request = voicedriver.listen("Is there anything else I can help you with today? (yes / no) \n")
    if request == "yes": 
      request = voicedriver.listen("(ALEX) : What else can I help you with today? \n")
      await map_request(request.lower())


    

async def parse_amazon2(instr):
  if instr == "Go to https://www.amazon.com/gp/css/your-orders-access":
    print_and_say("To get started I'm going to need to go to the Amazon Orders page. ")
    await agent.webdriver.goToPage("https://www.amazon.com/gp/css/your-orders-access")
  elif instr == "Ask user for email":
    print_and_say("And I'll need to log you in to help you with your request")
    ans = ask_and_confirm("What is your email?", "email", True)
    await insert_text(ans, "ap_email")
    await click("continue")
  elif instr == "Ask user for password":
    ans = ask_and_confirm("What is your password?", "password")
    await insert_text(ans, "ap_password")
  elif instr == "Click Sign in":
    print_and_say("Thanks! I'm going to sign you in now")
    await click("signInSubmit")
    print_and_say("A 2-Factor Authentication Code was sent to you. Please verify it.")
    await agent.webdriver.page.waitForNavigation()
  elif instr == "Ask user for the order you want to track":
    ans = ask_and_confirm("Which order would you like to track?", "order you would like to track")
  elif instr == "Click Track Package by the user-selected order you want to track":
    print("(ALEX) : Looking at your account, your most recent order was for XYZ.")
    print("(ALEX) : The status of your order is: Delivered")

    request = voicedriver.listen("Is there anything else I can help you with today? (yes / no) \n")
    if request == "yes": 
      request = voicedriver.listen("(ALEX) : What else can I help you with today? \n")
      await map_request(request.lower())

async def parse_google1(instr):
  if instr == "Go to https://accounts.google.com/SignUp":
    print_and_say("I'm going to access the Google account signup page.")
    await agent.webdriver.goToPage("https://accounts.google.com/SignUp")
  elif instr == "Ask user for first name":
    print_and_say("I'll need some information to create your account. ")
    ans = ask_and_confirm("What is your first name? ", "first name")
    await insert_text(ans, "firstName")
  elif instr == "Ask user for last name":
    ans = ask_and_confirm("What is your last name? ", "last name")
    await insert_text(ans, "lastName")  
  elif instr == "Ask user for username":
    ans = ask_and_confirm("What username would you like? ", "username you would like", True)
    await insert_text(ans, "username")
  elif instr == "Ask user for password":
    ans = ask_and_confirm("You got it. And what password would you like? (Please pick something with at least 8 letters, number, and nonalphanumeric)", "password you would like", True)
    await agent.webdriver.page.waitForSelector(f'[name="Passwd"]')
    await agent.webdriver.page.type(f'[name="Passwd"]', ans)
    print_and_say("Your password works!")
    await agent.webdriver.page.waitForSelector(f'[name="ConfirmPasswd"]')
    await agent.webdriver.page.type(f'[name="ConfirmPasswd"]', ans)
  elif instr == "Click Next":
    print_and_say("Your account registration has been submitted. You should receive a verification code to finish you setup. ") 
    await agent.webdriver.page.waitForSelector(f'#accountDetailsNext')
    await agent.webdriver.page.click(f'#accountDetailsNext')
    request = voicedriver.listen("Is there anything else I can help you with today? (yes / no) \n")
    if request == "yes": 
      request = voicedriver.listen("(ALEX) : What else can I help you with today? \n")
      await map_request(request.lower())

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
    print_and_say("I'm going to need to login to your Gmail to do that")
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
    print("(ALEX) : You should have received a verification code from Google. Please verify. ")
    sleep(5)
  elif instr == "Click Help":
    await agent.webdriver.page.waitForSelector(f'[class="t7"]')
    await agent.webdriver.page.click(f'[class="t7"]')
    sleep(2)
    await agent.webdriver.page.waitForSelector(f'[aria-label="Send feedback"]')
    await agent.webdriver.page.click(f'[aria-label="Send feedback"]')
  elif instr == "Ask user for comments":
    ans = ask_and_confirm("What is your feedback?", "feedback to give")
    await agent.webdriver.page.waitForSelector(f'[aria-label="Have feedback? We’d love to hear it, but please don’t share sensitive information. Have questions? Try help or support."]')
    await agent.webdriver.page.type(f'[aria-label="Have feedback? We’d love to hear it, but please don’t share sensitive information. Have questions? Try help or support."]', ans)
  elif instr == " At the bottom right, click Send.":
    print_and_say("Submitting your feedback!")
    await agent.webdriver.page.waitForSelector(f'[key="send"]')
    await agent.webdriver.page.click(f'[key="send"]')

    request = voicedriver.listen("Is there anything else I can help you with today? (yes / no) \n")
    if request == "yes": 
      request = voicedriver.listen("(ALEX) : What else can I help you with today? \n")
      await map_request(request.lower())

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
    print_and_say("I'm going to need to access your Pinterest account.")
    await agent.webdriver.goToPage("https://www.pinterest.com/login")
  elif instr == "Ask user for email Address":
    ans = ask_and_confirm("(ALEX) : What is your email?", "email", True)
    await insert_text(ans, "email")
  elif instr == "Ask user for Password":
    ans = ask_and_confirm("(ALEX) : What is your password?", "password")
    await insert_text(ans, "password")
  elif instr == "Click Log in":
    print_and_say("(ALEX) : Thank you. I'm going to log in for you now. ")
    await agent.webdriver.page.waitForSelector(f'[class="red SignupButton active"]')
    await agent.webdriver.page.click(f'[class="red SignupButton active"]')
  elif instr == "Click Ads in the top left corner":
    print_and_say("(ALEX) : I'm in your ad account now. ")
    await agent.webdriver.goToPage("https://ads.pinterest.com/advertiser/549761713038")
  elif instr == "Click Arrow button next to your name":
    print("(ALEX) : Your ad account number is 549761713038")
    request = voicedriver.listen("Is there anything else I can help you with today? (yes / no) \n")
    if request == "yes": 
      request = voicedriver.listen("(ALEX) : What else can I help you with today? \n")
      await map_request(request.lower())


async def parse_pinterest2(instr):
  if instr == "Go to http://pinterest.com/password/reset":
    print_and_say("(ALEX) : I'm going to login and go to the Pinterest password reset page to help you")
    await agent.webdriver.goToPage("http://pinterest.com/password/reset")
  elif instr == "Ask user for email":
    print_and_say("(ALEX) : I need your email address to help you")
    ans = ask_and_confirm("(ALEX) : What is your email?", "email", True)
    await insert_text(ans, "userQuery")
  elif instr == "Click Send a password reset email":
    print_and_say("(ALEX) : Thanks. I'm going to send you a password reset email now.")
    await agent.webdriver.page.waitForSelector(f'[class="RCK Hsu USg adn CCY czT Vxj aZc Zr3 hA- Il7 Jrn hNT BG7 gn8 L4E kVc iyn"]')
    await agent.webdriver.page.click(f'[class="RCK Hsu USg adn CCY czT Vxj aZc Zr3 hA- Il7 Jrn hNT BG7 gn8 L4E kVc iyn"]')
  elif instr == "Read to User: Check the email address connected to your account for a password reset email":
    print_and_say("(ALEX) : Check the email address connected to your account for a password reset email. You're all set. ")
    sleep(2)
    request = voicedriver.listen("Is there anything else I can help you with today? (yes / no) \n")
    if request == "yes": 
      request = voicedriver.listen("(ALEX) : What else can I help you with today? \n")
      await map_request(request.lower())

async def parse_spotify1(instr):
  if instr == "Go to http://www.spotify.com/account?_ga=2.170055017.893322237.1604048036-1104676808.1602105716":
    print_and_say("(ALEX) : I'm going to go to your spotify account")
    await agent.webdriver.goToPage("http://www.spotify.com/account?_ga=2.170055017.893322237.1604048036-1104676808.1602105716")
  elif instr == "Ask user for email":
    print_and_say("(ALEX) : I need to log you in to help you with your request")
    ans = ask_and_confirm("(ALEX) : What is your email?", "email", True)
    await insert_text(ans, "login-username")
  elif instr == "Ask user for password":
    ans = ask_and_confirm("(ALEX) : What is your password?", "password")
    await insert_text(ans, "login-password")
  elif instr == "Click Log in":
    print_and_say("Logging you in")
    await click("login-button")
  elif instr == "Click EDIT PROFILE.":
    print_and_say("(ALEX) : I'm going to navigate to edit your profile")
    await agent.webdriver.goToPage("https://www.spotify.com/account/profile/")
  elif instr == "ask User for new email address":
    ans = ask_and_confirm("(ALEX) : What would you like your new email address to be?", "email address", True)
    await insert_text(ans, "email")
  elif instr ==  "Click SAVE PROFILE.":
    print_and_say("(ALEX) : Thanks. I'll save those changes for you")
    await agent.webdriver.page.waitForSelector(f'[class="Button-sc-8cs45s-0 gBYMyb"]')
    await agent.webdriver.page.click(f'[class="Button-sc-8cs45s-0 gBYMyb"]')
    

async def parse_spotify2(instr):
  if instr == "Go to http://www.spotify.com/account?_ga=2.170055017.893322237.1604048036-1104676808.1602105716":
    print_and_say("(ALEX) : I'm going to go to your spotify account from my side")
    await agent.webdriver.goToPage("http://www.spotify.com/account?_ga=2.170055017.893322237.1604048036-1104676808.1602105716")
  elif instr == "Ask user for email":
    print_and_say("(ALEX) : I need to log you in to help you with your request")
    ans = ask_and_confirm("(ALEX) : What is your email?", "email", True)
    await insert_text(ans, "login-username")
  elif instr == "Ask user for password":
    ans = ask_and_confirm("(ALEX) : What is your password?", "password")
    await insert_text(ans, "login-password")
  elif instr == "Click Log in":
    print_and_say("(ALEX) : Ok. I'm going to log in really quickly to sign you out.")
    await click("login-button")
  elif instr == "Click SIGN OUT EVERYWHERE.":
    print_and_say("(ALEX) : I've signed you out of all of your devices. ")
    await agent.webdriver.goToPage("https://accounts.spotify.com/revoke_sessions/?continue=https%3A%2F%2Fwww.spotify.com")
    request = voicedriver.listen("Is there anything else I can help you with today? (yes / no) \n")
    if request == "yes": 
      request = voicedriver.listen("(ALEX) : What else can I help you with today? \n")
      await map_request(request.lower())


async def parse_walmart1(instr):
  if instr == "Go to https://www.walmart.com/account/signup":
    await agent.webdriver.goToPage("https://www.walmart.com/account/signup")
  elif instr == "Ask user for first name":
    print_and_say("I need some information to create your account")
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
    print_and_say("(ALEX) : OK. I'm creating your account now.")
    await agent.webdriver.page.waitForSelector(f'[class="button s-margin-top text-inherit"]')
    await agent.webdriver.page.click(f'[class="button s-margin-top text-inherit"]')
    sleep(5)
    print("(ALEX) : Congratulations. Your Walmart account has been created!")
    print("(ALEX) : You can now login to Walmart . ")
    request = voicedriver.listen("Is there anything else I can help you with today? (yes / no) \n")
    if request == "yes": 
      request = voicedriver.listen("(ALEX) : What else can I help you with today? \n")
      await map_request(request.lower())



async def parse_walmart2(instr):
  if instr == "Go to https://www.walmart.com/account/forgotpassword":
    print_and_say("I'm going to file a password reset request on your behalf. ")
    await agent.webdriver.goToPage("https://www.walmart.com/account/forgotpassword")
  elif instr == "Ask user for email address":
    ans = ask_and_confirm("(ALEX) : What is your email?", "email", True)
    await insert_text(ans, "email-fp")
    await click("forgot-pwd-continue-btn")
  elif instr == "Read to user: Check your email for the code. Be sure to check your junk or spam folder.":
    print_and_say("(ALEX) : A verification code has been sent to your email. Be sure to check your junk or spam folder.")
  elif instr == "Ask user for code":
    sleep(5)
    ans = ask_and_confirm("(ALEX) : What is the verification code?", "verification code")
    await insert_text(ans, "code-vrc")
    await agent.webdriver.page.click("#forgot-pwd-continue-btn")

  elif instr ==  "Select Submit Code":
    print_and_say("(ALEX) : Thanks, I'll need to submit it. ")
    print("(ALEX) : I'm going to help you create a new password. ")
    await agent.webdriver.page.click("#resetPwd")
    ans = ask_and_confirm("(ALEX) : What would you like your new password to be? ", "new password")
    await insert_text(ans, "#password-change-skip")
    await agent.webdriver.page.click("#skip-change-pwd-form > div.buttons-container > button")
    print("(ALEX) : Congratulations. Your password has been reset to " + str(ans))

    request = voicedriver.listen("Is there anything else I can help you with today? (yes / no) \n")
    if request == "yes": 
      request = voicedriver.listen("(ALEX) : What else can I help you with today? \n")
      await map_request(request.lower())

async def map_request(request):
  data = await read_data()

  if "gift card" in request:
    print("(ALEX) : I'd be happy to help you redeem your Amazon gift card. Let's get started.")
    data = data["amazon1"]
    instructions = data["instructions"]
    for instr in instructions:
      await parse_amazon1(instr)
  elif "track" in request: 
    print("(ALEX) : I'd be happy to help you track your latest Amazon package. Let's get started.")
    data = data["amazon2"]
    instructions = data["instructions"]
    for instr in instructions:
      await parse_amazon2(instr) 
  elif "feedback" in request:
    print("(ALEX) : That's very nice of you. I'd be happy to help you send Google feedback. Let's get started.")
    data = data["google3"]
    instructions = data["instructions"]
    for instr in instructions:
      await parse_google3(instr)
  elif ("create" in request or 'sign up' in request or 'signup' in request or 'sign-up' in request) and "google" in request and "account" in request: 
    print("(ALEX) : I'd be happy to help you Create an Account on Google. Let's get started.")
    data = data["google1"]
    instructions = data["instructions"]
    for instr in instructions:
      await parse_google1(instr)
  elif "protected content" in request:
    print("(ALEX) : I'd be happy to help you change your Protected Content on Google. Let's get started.")
    data = data["google2"]
    instructions = data["instructions"]
    for instr in instructions:
      await parse_google2(instr)
  elif "account" in request and ("ad" in request):
    print("(ALEX) : I'd be happy to help you create an advertiser account on Pinterest. Let's get started.")
    data = data["pinterest1"]
    instructions = data["instructions"]
    for instr in instructions:
      await parse_pinterest1(instr)
  elif "reset" in request and "password" in request and "pinterest" in request:
    print("(ALEX) : I'd be happy to help you Reset your Pinterest Password. Let's get started.")
    data = data["pinterest2"]
    instructions = data["instructions"]
    for instr in instructions:
      await parse_pinterest2(instr)
  elif "change" in request and "email" in request:
    print("(ALEX) : I'd be happy to help you change your Spotify email. Let's get started.")
    data = data["spotify1"]
    instructions = data["instructions"]
    for instr in instructions:
      await parse_spotify1(instr)
  elif "sign" in request and "out" in request and "spotify" in request:
    print("(ALEX) : I'm sorry to here. I can help you sign out of all of your accounts. Let's get started.")
    data = data["spotify2"]
    instructions = data["instructions"]
    for instr in instructions:
      await parse_spotify2(instr)
  elif ("create" in request or 'sign up' in request or 'signup' in request or 'sign-up' in request) and "walmart" in request and "account" in request:
    print("(ALEX) : I'd be happy to help you create a Walmart account. Let's get started.")
    data = data["walmart1"]
    instructions = data["instructions"]
    for instr in instructions:
      await parse_walmart1(instr)
  elif "password" in request and "walmart" in request:
    print("(ALEX) : I'd be happy to help you reset your Walmart password. Let's get started.")
    data = data["walmart2"]
    instructions = data["instructions"]
    for instr in instructions:
      await parse_walmart2(instr)
  else:
    request = voicedriver.listen("(ALEX) : Sorry I can't service that request. Can you please clarify what you need help with? \n")
    await map_request(request.lower())


async def run():
  await agent.webdriver.openDriver()

  request = voicedriver.listen("(ALEX) : Hi there! How may I help you today? \n")
  await map_request(request.lower())



if __name__ == "__main__":
  voicedriver = VoiceDriver()
  webdriver = WebDriver()
  agent = Agent(webdriver)

  loop = asyncio.new_event_loop()
  asyncio.set_event_loop(loop)
  result = loop.run_until_complete(run())