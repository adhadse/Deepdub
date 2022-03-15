from moviepy.config import get_setting
from moviepy.tools import subprocess_call
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_audio

class Deepdub:
  def create_sample_clip_and_audio(video_file, slice_from, slice_to):
    """
    Create Sample video and audio file from `video_file`
    Parameters:
      - `video_file`: path to video file
      - `slice_from`: string formatted as `min_sec` or 'h_min_sec'
         indicating where to begin slicing
      - `slice_to`: string formatted as `min_sec` or 'h_min_sec'
         indicating where to end slicing
    Returns:
      - `clipped_video`: path to clipped video
      - `clipped_audio`: path to clipped audio
    """
    Path(f"./output_dir/{self.project_name}").mkdir(parents=True, exist_ok=True)
    
    clipped_video = f'./output_dir/{self.project_name}/clip.mp4'
    clipped_audio = f'./output_dir/{self.project_name}/clip.mp3'
    
    ffmpeg_extract_subclip(video_file, __to_sec(slice_from), __to_sec(slice_to),
                           targetname=clipped_video)
    ffmpeg_extract_audio(clipped_video, clipped_audio)
    return clipped_video, clipped_audio

  def __to_sec(min_sec):
    """Convert a string formatted as `min_sec` or 'h_min_sec' 
       to int of total seconds.
    """
    return int(
      min_sec.split("_")[-2])*60 + int(
      min_sec.split("_")[-1])
