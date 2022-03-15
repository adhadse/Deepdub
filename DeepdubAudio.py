import numpy as np
import pandas as pd
from pathlib import Path
from moviepy.config import get_setting
from moviepy.tools import subprocess_call


class DeepdubAudio():
  def __init__(self, project_name, sentence_df, audio_path):
    """
    Manages audio for Deepdub.
    - `audio_df` will contains information required to clip audio,
      including parts where sentences are spoken and where they are not.
    """
    self.sentence_df = sentence_df
    self.project_name = project_name
    self.audio_path = audio_path
    
    # `audio_df` requires ranges where sentences are spoken and also where 
    # they are not in whole `audio_path` file.
    vals = sentence_df.reset_index()[['start', 'end']].stack().unique()
    vals2 = np.concatenate([np.array([0], dtype=vals.dtype), vals])
    self.audio_df = pd.DataFrame(zip(vals2, vals), columns=['start', 'end'])
    self.audio_df["hash"] = pd.util.hash_pandas_object(audio_df[["start", "end"]], index=False)

  def create_audio_clips():
    """Create audio clips based on `audio_df`"""
    output_path = f"./output_dir/{self.project_name}/audio_clips"
    Path(output_path).mkdir(parents=True, exist_ok=True)
    
    for index, row in self.audio_df.iterrows():
      audio_clip_path = output_path + f'/{row.hash}.mp3'
      clip_audio(self.audio_path, 
                 __timestamp_to_seconds(row["start"]),
                 __timestamp_to_seconds(row["end"]),
                 audio_clip_path)

  def clip_audio(input_audio, clip_from, clip_to, output, bitrate=3000, fps=44100):
    """Clip audio from another audio file and save it in `output`"""
    cmd = [get_setting("FFMPEG_BINARY"), "-y",
           "-ss", "%0.3f"%clip_from,
           "-i", input_audio,
           "-t", "%0.3f"%(clip_to-clip_from),
           "-ab", "%dk"%bitrate,
           "-ar", "%d"%fps, output]
    subprocess_call(cmd)

  def __timestamp_to_seconds(timestamp):
    """Convert Pandas timestamp object to float seconds with decimal
       part representing milliseconds"""
    return timestamp.hour + timestamp.second + timestamp.microsecond/1000000
