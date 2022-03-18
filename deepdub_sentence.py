import pysrt
import pandas as pd
import re
import numpy as np


class DeepdubSentence:
  def __init__(self, project_name, subtitle_path,
               slice_from=None, slice_to=None, shift=None):
    """Create sentences out of sub file
    Parameters:
      - `project_name`: a project name you might want to give
      - `subtitle_path`: Path to complete subtitles
      - `slice_from` (default None): string formatted as `minute_seconds` to set
         where to clip subs from
      - `slice_to` (default None): string formatted as `minute_seconds` to set
         until where subs need to be clipped to.
      - `shift` (default None): a dictionary with shift values for keys in 
         (hours, minutes, seconds, milliseconds, ratio) negative values for
         reverse shift otherwise forward
    """
    self.SUBS_OUTPUT_PATH = f'./output_dir/{project_name}/subs_gen.srt'
    self.subs = pysrt.open(subtitle_path)

    # Slice subtitles and zero-centering
    if (slice_from is not None) and (slice_to is not None):
      start_after = {
        "min": int(slice_from.split("_")[0]),
        "sec": int(slice_from.split("_")[1])}
      ends_before = {
        "min": int(slice_to.split("_")[0]),
        "sec": int(slice_to.split("_")[1])}
      self.subs = self.subs.slice(
        starts_after={
          'minutes': start_after["min"],
          'seconds': start_after["sec"]},
        ends_before={
          'minutes': ends_before["min"],
          'seconds': ends_before["sec"]})
      self.subs.shift(
        minutes=-start_after["min"],
        seconds=-start_after["sec"])
    self.subs.shift(**shift)

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

    # Replace anything inside () with '' 
    # and if whole row is '' replace with NaN and drop them
    subs_df[["text"]] = subs_df[["text"]].applymap(
      lambda text: re.sub("\\((.*)\\)", "", text)).replace("", np.nan)
    subs_df.dropna(inplace=True)
    return subs_df

  def get_sentences(self):
    """
    Return preprocessed sentences of given a subtitle file.
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
    sentence_df["hash"] = pd.util.hash_pandas_object(
      sentence_df[["start", "end"]], index=False)
    return sentence_df

  def save_subs(self):
    self.subs.save(self.SUBS_OUTPUT_PATH, encoding='utf-8')
    return self.SUBS_OUTPUT_PATH
