from nltk import *
import sys

verbs = ["RB", "RBR", "RBS", "VB", "VBD", "VBG", "VBN", "VBP", "VBZ", "WRB"]
nouns = ["NN", "NNS", "NNP", "NNPS"]
prepositions = ["IN", "TO", "CC", "PRP$"]
keywords = ["select", "click", "go"]

# text = word_tokenize(sys.argv[1].lower())
# tagged = pos_tag(text)

# found_verbs, found_nouns = [], []

# for word, tag in tagged:
#   print(word, tag)
#   if tag in verbs:
#     found_verbs.append(word)
#   elif tag in nouns:
#     found_nouns.append(word)

# print("Found verbs are ", found_verbs)
# print("Found nouns are ", found_nouns)

def remove_prepositions(text):
  tagged = pos_tag(text)
  res = ""
  print(tagged)
  for word, tag in tagged:
    print(word, tag)
    if tag not in prepositions:
      res += word + ' '
  return parse_sentence(res.strip())
      
def parse_sentence(sentence):
  res = []
  curr_sent = ""
  split_sentence = sentence.split()

  # go to first occurence of keyword
  for i, word in enumerate(split_sentence):
    if word in keywords:
      split_sentence = split_sentence[i:]
      break

  for i, word in enumerate(split_sentence):
    if word in keywords:
      if not i == 0:
        res.append(curr_sent)
      curr_sent = word + ' '
    else:
      curr_sent += word + '  '
  res.append(curr_sent.strip())
  return res
    

def find_verbs():
  print("find_verbs")

def find_nouns():
  print("find_nouns")
  
if __name__ == "__main__":
  text = word_tokenize(sys.argv[1].lower())
  command = sys.argv[2]

  if command == "find_verbs":
    print(find_verbs(text))
  elif command == "find_nouns":
    print(find_nouns(text))
  elif command == "remove_prepositions":
    print(remove_prepositions(text))
  
  sys.stdout.flush()