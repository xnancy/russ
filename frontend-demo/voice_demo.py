import json
import sys
sys.path.append('..')
from representation.VoiceDriver import VoiceDriver
from time import sleep

def read_data():
  print("Running demo on Amazon example...\n")
  with open('../data-generator/eval-clean.json') as f:
    data = json.load(f)
    data = data["website"]["https://www.amazon.com/gp/help/customer/display.html"][0]
    return data

def slow_print(text):
  for ch in text:
    print(ch, end = '', flush=True)
    sleep(.05)
  print("")

def run():
  data = read_data()
  url = data["url"]
  instructions = data["instructions"]
  print("url is ", url)
  print("instructions is ", instructions)
  for instr in instructions:
    slow_print(instr)
    VoiceDriver.speak(instr)



if __name__ == "__main__":
  VoiceDriver = VoiceDriver()
  run()