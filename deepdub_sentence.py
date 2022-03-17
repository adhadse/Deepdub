import pysrt
import pandas as pd
import re
import numpy as np


class DeepdubSentence:
  def __init__(self, subtitle_path, slice_from=None, slice_to=None):
    """Create sentences out of sub file
    Parameters:
      - `file`: input path to subtitle file
      - `slice_from` (default None): string formatted as `minute_seconds` to set
         where to clip subs from
      - `slice_to` (default None): string formatted as `minute_seconds` to set
         until where subs need to be clipped to.
    """
    self.subs = pysrt.open(subtitle_path)

    # Slice subtitles and zero-centering
    if (slice_from is not None) and (slice_to is not None):
      start_after = {"min": int(slice_from.split("_")[0]), "sec": int(slice_from.split("_")[1])}
      ends_before = {"min": int(slice_to.split("_")[0]),  "sec": int(slice_to.split("_")[1])}
      self.subs = self.subs.slice(
        starts_after={'minutes': start_after["min"], 'seconds': start_after["sec"]},
        ends_before={'minutes': ends_before["min"],  'seconds': ends_before["sec"]})
      self.subs.shift(
        minutes=-start_after["min"],
        seconds=-start_after["sec"])

  def __regex(self):
    """Replace using regex without writing regex expression"""
    replacements = {"|": " ", "\n": " ", "...": ";"}
    replacements = dict((re.escape(k), v) for k, v in replacements.items())
    pattern = re.compile("|".join(replacements.keys()))

    subs_df = pd.DataFrame([[sub.start, sub.end,
                             pattern.sub(lambda m: replacements[
                               re.escape(m.group(0))], sub.text)]
                            for sub in self.subs],
                           columns=["start", "end", "text"])

    # Replace anything inside () with '' and if whole row is '' replace with NaN and drop them
    subs_df[["text"]] = subs_df[["text"]].applymap(lambda text: re.sub("\\((.*)\\)", "", text)).replace("", np.nan)
    subs_df.dropna(inplace=True)
    return subs_df

  def get_sentences(self, hashed=True):
    """
    Return preprocessed sentences of given a subtitle file.
    ### Parameters:
    - `hashed` (bool, default is True): if true return hash of
    starting and ending time as index,
    otherwise use starting and ending time as index
    """
    sentence = ""
    result = []

    for i, sub in self.__regex().iterrows():
      if sentence == "":
        start = sub.start
      sentence = sub.text if sentence == "" else sentence + " " + sub.text
      if re.search('[.?!]', sub.text):
        result.append((start, sub.end, sentence))
        sentence = ""

    # Convert SubRipTime to pd.Timestamp for `start` and `end` and create hash of them
    sentence_df = pd.DataFrame(result, columns=["start", "end", "sentence"])
    sentence_df["start"] = pd.to_datetime(sentence_df["start"], format="%H:%M:%S,%f")
    sentence_df["end"] = pd.to_datetime(sentence_df["end"], format="%H:%M:%S,%f")
    sentence_df["hash"] = pd.util.hash_pandas_object(sentence_df[["start", "end"]], index=False)

    if hashed:
      sentence_df.set_index(["hash"], inplace=True)
    else:
      sentence_df.set_index(["start", "end"], inplace=True)

    return sentence_df

  def save_subs(self, path_to_file):
    self.subs.save(path_to_file, encoding='utf-8')
