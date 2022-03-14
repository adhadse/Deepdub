import pysrt
import pandas as pd
import re


class Sentences:
  def __init__(self, file, hashed=True):
    self.subs = pysrt.open(file)
    self.sentence_df = self.__to_sentences(self.__regex(), hashed)
    return self.sentence_df


  def __regex(self, subs):
    # Replace using regex without writing regex expression
    replacements = {"|": " ", "\n": " ", "...": ";"}
    replacements = dict((re.escape(k), v) for k, v in replacements.items())
    pattern = re.compile("|".join(replacements.keys()))

    subs_df = pd.DataFrame([[sub.start, sub.end,
                             pattern.sub(lambda m: replacements[
                               re.escape(m.group(0))], sub.text)]
                            for sub in self.subs],
                           columns=["start", "end", "text"])

    # Replace anything inside () with '' and if whole row is '' replace with NaN and drop them
    subs_df[["text"]] = subs_df[["text"]].applymap(lambda row: re.sub("\\((.*)\\)", "", row)).replace("", np.nan)
    subs_df.dropna(inplace=True)
    return subs_df

  def __to_sentences(self, subs_df, hashed):
    sentence = ""
    result = []

    for i, sub in subs_df.iterrows():
      if sentence == "":
        start = sub.start
      sentence = sub.text if sentence == "" else sentence + " " + sub.text 
      if re.search('[.?!]', sub.text):
        result.append((start, sub.end, sentence))
        sentence = ""

    sentence_df = pd.DataFrame(result, columns=["start", "end", "sentence"])

    if hashed:
      # Set index as the hash of sentence.
      sentence_df.index = pd.util.hash_pandas_object(sentence_df["sentence"], index=False)
      sentence_df["start"] = pd.to_datetime(sentence_df["start"], format="%H:%M:%S,%f")
      sentence_df["end"] = pd.to_datetime(sentence_df["end"], format="%H:%M:%S,%f")
    else:
      # Otherwise set "start" and "end" and index for easy indexing
      sentence_df.set_index(["start", "end"], inplace=True)

    return sentence_df
