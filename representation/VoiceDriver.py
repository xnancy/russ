import speech_recognition as sr

class VoiceDriver:
  def __init__(self):
    self.recognizer = sr.Recognizer()

  def listen(self):
    with sr.Microphone() as source:
      self.recognizer.adjust_for_ambient_noise(source)
      print("Please say something ")
      audio = self.recognizer.listen(source)
      print("Reconizing Now ... ")

      try:
        dest = self.recognizer.recognize_google(audio)
        print("You have said : " + dest)

      except Exception as e:
        print("Error : " + str(e))


# def main():
#     driver = VoiceDriver()
#     driver.listen()

# if __name__ == "__main__":
#     main()
