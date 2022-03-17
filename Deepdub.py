from deepdub_sentence import DeepdubSentence
from deepdub_audio import DeepdubAudio
import os
import uuid
from pathlib import Path
from IPython import display
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_audio
from moviepy.video.io.ffmpeg_tools import ffmpeg_merge_video_audio


class Deepdub:
  def __init__(self, 
               project_name, 
               subtitle_path,
               slice_from, slice_to):
    """TODO
    """
    self.project_name = project_name + str(uuid.uuid4())
    self.OUTPUT_DIR = f'./output_dir/{project_name}'
    self.subtitle_path = subtitle_path
    self.slice_from = slice_from
    self.slice_to = slice_to

  def deepdub(self, clipped_video, clipped_audio):
    """TODO"""
    # Step 1: Generate sentences
    deep_s = DeepdubSentence(subtitle_path=self.subtitle_path,
                             slice_from=self.slice_from,
                             slice_to=self.slice_to)
    sentence_df = deep_s.get_sentences(hashed=True)
    
    # Step 2: Create audio clips
    deep_a = DeepdubAudio(project_name=self.project_name,
                          sentence_df=sentence_df,
                          audio_path=clipped_audio)
    deep_a.create_audio_segments()
    
    
  def create_sample_clip_and_audio(self, video_file, slice_from, slice_to):
    """
    Create Sample video and audio file from `video_file`
    ### Parameters:
    - `video_file`: path to video file
    - `slice_from`: string formatted as `min_sec` or `h_min_sec`
    indicating where to begin slicing
    - `slice_to`: string formatted as `min_sec` or `h_min_sec`
    indicating where to end slicing
    ### Returns:
    - `clipped_video`: path to clipped video
    - `clipped_audio`: path to clipped audio
    """
    Path(self.OUTPUT_DIR).mkdir(parents=True, exist_ok=True)

    clipped_video = f'{self.OUTPUT_DIR}/clip.mp4'
    clipped_audio = f'{self.OUTPUT_DIR}/clip.mp3'

    ffmpeg_extract_subclip(self.video_file,
                           self.__to_sec(slice_from), self.__to_sec(slice_to),
                           targetname=clipped_video)
    ffmpeg_extract_audio(clipped_video, clipped_audio)
    return clipped_video, clipped_audio

  def merge_video_audio(self, clipped_video, output_audio):
    """Merges video """
    video_no_sound = f'{self.OUTPUT_DIR}/clip_no_sound.mp4'
    cmd = [get_setting("FFMPEG_BINARY"), "-y",
           "-i", clipped_video, 
           "-an",
           "-c", "copy",
           video_no_sound]
    subprocess_call(cmd)

    gen_clip_path = f'{self.OUTPUT_DIR}/clip_gen.mp4'
    ffmpeg_merge_video_audio(video_no_sound, output_audio, gen_clip_path)
    os.remove(video_no_sound)
    return gen_clip_path

  def play_audio(path):
    return display.display(display.Audio(path))

  def play_video(path):
    display.display(display.Video(path))

  def __to_sec(self, min_sec):
    """Convert a string formatted as `min_sec` or `h_min_sec`
       to int of total seconds.
    """
    return int(
      min_sec.split("_")[-2])*60 + int(
      min_sec.split("_")[-1])
