
import pysrt
import pandas as pd
import re


class Sentences:
  def __init__(self, file):
    self.subs = pysrt.open(file)
    self.subs_df = self.__regex()
    self.sentence_df = self.__to_sentences()
    return self.sentence_df
    
    
  def __regex(self, subs):
    # Replace using regex without writing regex expression
    replacements = {"|": " ", "\n": " ", "...": ";"}
    replacements = dict((re.escape(k), v) for k, v in replacements.items())
    pattern = re.compile("|".join(replacements.keys()))

    subs_df = pd.DataFrame([[sub.start, sub.end, 
                             pattern.sub(lambda m: replacements[re.escape(m.group(0))], sub.text)] for sub in self.subs],
                           columns=["start", "end", "text"])
    return subs_df
  
  def __to_sentences(self):
    sentence = ""
    result = []

    for i, sub in self.subs_df.iterrows():
      if sentence == "":
        start = sub.start
      sentence = sub.text if sentence=="" else sentence + " " + sub.text 
      if re.search('[.?!]', sub.text):
        result.append((start, sub.end, sentence))
        sentence = ""
      
    return pd.DataFrame(result, columns=["start", "end", "sentence"])
