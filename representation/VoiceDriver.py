import speech_recognition as sr
import pyttsx3

class VoiceDriver:
  def __init__(self):
    self.recognizer = sr.Recognizer()
    self.speaker = pyttsx3.init() 

  def listen(self):
    with sr.Microphone() as source:
      self.recognizer.adjust_for_ambient_noise(source)
      print("Please say something ")
      audio = self.recognizer.listen(source)
      print("Reconizing Now ... ")

      try:
        dest = self.recognizer.recognize_google(audio)
        print("You have said : " + dest)
        return dest

      except Exception as e:
        print("Error : " + str(e))

  def speak(self, text): 
    self.speaker.say(text)  
    self.speaker.runAndWait() 


def main():
    driver = VoiceDriver()
    text = driver.listen()
    driver.speak(text)

if __name__ == "__main__":
    main()
