from deepdub_sentence import DeepdubSentence
from deepdub_audio import DeepdubAudio
from deepdub_clusterer import DeepdubClusterer
import os
import uuid
from pathlib import Path
from IPython import display
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_audio
from moviepy.video.io.ffmpeg_tools import ffmpeg_merge_video_audio


class Deepdub:
  def __init__(self,
               slice_from, slice_to,
               project_name=None):
    """Deepdub
    Deepdub a given video.
    General pattern to work:
    1. Initialize this class.
    2. Get project dir using `get_project_dir()`
    3. Save video and subtitle (complete) in project dir.
    4. Call `deepdub(video_path, subs_path)
    ### Parameters:
    - `slice_from`: string formatted as `minute_seconds` to set
       where to clip subs from
    - `slice_to`: string formatted as `minute_seconds` to set
       until where subs need to be clipped to.
    - `project_name` (optional): a project name you might want to give
    """
    if project_name is None:
      self.project_name = str(uuid.uuid4())
    else:
      self.project_name = f'{project_name}_{str(uuid.uuid4())}'
    self.OUTPUT_DIR = f'./output_dir/{project_name}'
    self.slice_from = slice_from
    self.slice_to = slice_to
    Path(self.OUTPUT_DIR).mkdir(parents=True, exist_ok=True)

  def deepdub(self, clipped_video, subtitle_path,
              n_speakers,
              clipped_audio=None, shift=None):
    """Deepdubs a given video
    ### Parameters:
    - `clipped_video: Path to clipped video
    - `subtitle_path`: Path to complete subtitles (not expected to clipped)
       unlike `clipped_video`
    - `n_speakers`: Number of speakers in provided clip
    - `clipped_audio` (not required)(default: None): Path to clipped audio
    - `shift` (default None): a dictionary with shift values for keys in 
       (hours, minutes, seconds, milliseconds, ratio) negative values for
       reverse shift otherwise forward
    ### Returns:
    - `gen_clip_path`: Generated Clip path
    - `gen_subs_path`: Generated subtitles path"""
    if clipped_audio is None:
      clipped_audio = f'{self.OUTPUT_DIR}/audio.wav'
      ffmpeg_extract_audio(clipped_video, clipped_audio)
      
    # Step 1: Generate sentences and subs
    deep_s = DeepdubSentence(project_name=self.project_name,
                             subtitle_path=subtitle_path,
                             slice_from=self.slice_from,
                             slice_to=self.slice_to,
                             shift=shift)
    sentence_df = deep_s.get_sentences()
    gen_subs_path = deep_s.save_subs()
    
    # Step 2: Create audio clips and generate vocals and 
    # accompaniments
    deep_a = DeepdubAudio(project_name=self.project_name,
                          sentence_df=sentence_df,
                          audio_path=clipped_audio)
    deep_a.create_audio_segments()
    deep_a.extract_vocal_and_accompaniments()
    
    # Step 3: Generate Embeddings for vocals and cluster them
    # to identify speakers.
    # Edit `labels` column in sentence_df after this step if they are wrong
    deep_c = DeepdubClusterer(project_name=self.project_name,
                              sentence_df=sentence_df)
    sentence_df = deep_c.get_embeddings()
    sentence_df, kmeans = deep_c.cluster(n_speakers)
    
    # Step 5: Mix generated vocals with extracted accompaniments
    # Concatenate genrated audio segments
    # and create final generated video clip
    deep_a.mix_generated_vocals_and_accompaniments()
    generated_audio_path = deep_a.concatenate_generated_audio_segments()
    gen_clip_path = merge_video_audio(clipped_video, generated_audio_path)
    return gen_clip_path, gen_subs_path

  def create_sample_clip_and_audio(self, video_file, slice_from, slice_to):
    """
    Create Sample video and audio file from `video_file`.
    **WARNING**: Don't use in production, as `video_file` will be huge to store.
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

    clipped_video = f'{self.OUTPUT_DIR}/clip.mkv'
    clipped_audio = f'{self.OUTPUT_DIR}/audio.wav'

    ffmpeg_extract_subclip(video_file,
                           self.__to_sec(slice_from), self.__to_sec(slice_to),
                           targetname=clipped_video)
    ffmpeg_extract_audio(clipped_video, clipped_audio)
    return clipped_video, clipped_audio

  def merge_video_audio(self, clipped_video, output_audio):
    """Merges video """
    video_no_sound = f'{self.OUTPUT_DIR}/clip_no_sound.mkv'
    cmd = [get_setting("FFMPEG_BINARY"), "-y",
           "-i", clipped_video, 
           "-an",
           "-c", "copy",
           video_no_sound]
    subprocess_call(cmd)

    gen_clip_path = f'{self.OUTPUT_DIR}/clip_gen.mkv'
    ffmpeg_merge_video_audio(video_no_sound, output_audio, gen_clip_path)
    os.remove(video_no_sound)
    return gen_clip_path

  def get_project_dir(self):
    return self.OUTPUT_DIR

  def play_audio(path):
    return display.display(display.Audio(path))

  def play_video(path):
    return display.display(display.Video(path))

  def __to_sec(self, min_sec):
    """Convert a string formatted as `min_sec` or `h_min_sec`
       to int of total seconds.
    """
    return int(
      min_sec.split("_")[-2])*60 + int(
      min_sec.split("_")[-1])
