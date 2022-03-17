import numpy as np
import pandas as pd
from pathlib import Path
from moviepy.config import get_setting
from moviepy.tools import subprocess_call
from pyffmpeg import FFprobe


class DeepdubAudio():
  def __init__(self, project_name, sentence_df, audio_path):
    """
    Manages audio for Deepdub.
    - `audio_df` will contains information required to clip audio,
      including parts where sentences are spoken and where they are not.
    ### Parameters:
    - `project_name`: name for which you want to deepdub
    - `sentence_df`: a `DeepdubSentences.get_sentences()` instance
    - `audio_path`: path to extracted audio of clipped video
    """
    self.sentence_df = sentence_df.reset_index().set_index(["hash"])
    self.audio_path = audio_path
    self.OUTPUT_DIR = f'./output_dir/{project_name}'

    # `audio_df` requires ranges where sentences are spoken and also where
    # they are not in whole `audio_path` file.
    vals = sentence_df[['start', 'end']].stack().unique()
    vals2 = np.concatenate([np.array([0], dtype=vals.dtype), vals])
    self.audio_df = pd.DataFrame(zip(vals2, vals), columns=['start', 'end'])

    # DataFrame doesn't have information about last clip,
    # after all the sentences has ended
    self.audio_df = pd.concat([
      self.audio_df, pd.DataFrame({
        "start": [self.audio_df.iloc[-1].end],
        "end": [pd.to_datetime(FFprobe(self.audio_path).duration, format="%H:%M:%S.%f")]
      })], ignore_index=True, axis=0)
    self.audio_df["hash"] = pd.util.hash_pandas_object(self.audio_df[["start", "end"]], index=False)
    
    self.audio_df[["path"]] = self.audio_df[["hash"]].applymap(
      lambda h: str(h) + "_gen.mp3" if h in self.sentence_df.index else str(h) + ".mp3")

  def create_audio_segments(self):
    """Create audio clips based on `audio_df`"""
    output_clips_path = f"{self.OUTPUT_DIR}/audio_segments"
    Path(output_clips_path).mkdir(parents=True, exist_ok=True)

    for index, row in self.audio_df.iterrows():
      audio_clip_path = f'{output_clips_path}/{row.hash}.mp3'
      self.segment_audio(self.audio_path,
                      self.__timestamp_to_seconds(row["start"]),
                      self.__timestamp_to_seconds(row["end"]),
                      audio_clip_path)

    # Save path to segments to `audio_segments_list.txt`
    audio_segments_list = f'{output_clips_path}/audio_segments_list.txt'
    with open(audio_segments_list, 'w') as fout:
      for i, row in self.audio_df.iterrows():
        fout.write(f'file {row["path"]}\n')

  def segment_audio(self, input_audio, clip_from, clip_to, output, bitrate=3000, fps=44100):
    """Clip audio from another audio file and save it in `output`"""
    cmd = [get_setting("FFMPEG_BINARY"), "-y",
           "-ss", "%0.3f" % clip_from,
           "-i", input_audio,
           "-t", "%0.3f" % (clip_to-clip_from),
           "-ab", "%dk" % bitrate,
           "-ar", "%d" % fps, output]
    subprocess_call(cmd)

  def concatenate_audio_segments(self):
    """Concatenate audio segments using `audio_segments_list.txt`
    to generate `audio_gen.mp3`
    ### Returns:
    - `generated_audio_path`
    """
    generated_audio_path = f'{self.OUTPUT_DIR}/audio_segments/audio_gen.mp3'
    cmd = [get_setting("FFMPEG_BINARY"), "-y",
           "-f", "concat",
           "-safe", "0",
           "-i", f'{self.OUTPUT_DIR}/audio_segments/audio_segments_list.txt',
           "-c", "copy", 
           generated_audio_path]
    subprocess_call(cmd)
    return generated_audio_path

  def __timestamp_to_seconds(self, timestamp):
    """Convert Pandas timestamp object to float seconds with decimal
       part representing milliseconds"""
    return timestamp.hour + timestamp.second + timestamp.microsecond/1000000
