import speech_recognition as sr
import pyttsx3

class VoiceDriver:
  def __init__(self):
    self.recognizer = sr.Recognizer()
    self.speaker = pyttsx3.init() 

  def listen(self, text):
    with sr.Microphone() as source:
      self.recognizer.adjust_for_ambient_noise(source)
      print(text)
      print("Recognizing Now ... ")
      audio = self.recognizer.listen(source)

      try:
        dest = self.recognizer.recognize_google(audio)
        if dest is not None:
          return dest
        else:    
          print("I didn't catch that")    
          self.speak("I didn't catch that")
          self.speak(text)
          self.listen(text)

      except Exception as e:
        print("I didn't catch that")
        self.speak("I didn't catch that")
        self.speak(text)
        return self.listen(text)

  def speak(self, text): 
    self.speaker.say(text)  
    self.speaker.runAndWait() 


def main():
    driver = VoiceDriver()
    text = driver.listen()
    driver.speak(text)

if __name__ == "__main__":
    main()
