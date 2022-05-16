# Deepdub
A complete end-to-end Deep Learning system to generate high quality human like speech in English for Korean Drama. (WIP)

# Status
Check [Projects](https://github.com/adhadse/Deepdub/projects/4).

# What am I doing here?
There are various steps, I came up with
![Overview Deepdub](/res/images/deepdub_overview.png)

### [Step 0](https://github.com/adhadse/Deepdub/blob/master/0_Sentence_generation_from_Subtitles.ipynb): Preprocessing subtitles to get sentences
The relies heavily on Subtitles for the dubbing procedure to work, i.e., the subs should match the intended audio in the video file. 
If they don't use `shift` parameter of `DeepdubSentence` constructor. These sentences (stored in `sentence_df`) are used to create audio segments in step 1.

### [Step 1](https://github.com/adhadse/Deepdub/blob/master/1_Generating_Audio_Segments.ipynb): Generating audio segments
The `sentence_df` can then be used to create audio segments, more than enough accurate mapping of sentences to spoken audio. We also create segments which does not contain any spoken sentence/dialog as per preprocessed subtitles and writing them to `<hash>.wav` (hash of the start and ending timestamp of sentence from `sentence_df`. All of these file names are written to `audio_segments_list.txt` to concatenate back the generated audio and other audio segments which doesn't contain any spoken dialog. `audio_df` dataframe stores all the audio segments information, storing exact start and stop time stamp.

### [Step 2](https://github.com/adhadse/Deepdub/blob/master/2_Source_separation_for_audio_segments.ipynb): Source separation/separating accompaniments and vocals.
The background sound effects/accompaniments will behave as noise for our next step 3, (and possibly step 4). This problem is solved by using source separation technique (using *Spleeter*) spliting original audio containing a speech, into `<hash>_vocals.wav` and `<hash>_accopaniments.wav`. This step is performed only for the audio segments containing known speech (i.e., based on `sentence_df`), completely retaining background sound effects for audio segments which doensn't contain any speech.

### [Step 3](https://github.com/adhadse/Deepdub/blob/master/3_Clustering_audio_segments_for_speaker_diarization.ipynb): Clustering audio Segments for speaker Diarization
We don't know who spoke a particular audio segment just from subtitles. We need to give labels to audio segments so that we can dub that particular audio segment into that particular speaker's voice. For this I have applied clustering to speaker embeddings of audio segments, creating labels. Check [this notebook with visualization](https://colab.research.google.com/drive/1ayeG_AL_RXvhiUoe0Me1q3TjqpIsrFjb?usp=sharing).

### Step 4: Voice Reproduction
We already know which audio segment is spoken by which speaker in previous step. We can use these speech segments for that particular speaker for voice adaptation, generating speech (`<hash>_gen.wav`) using a TTS (Text-To-Speech) model and preprocessed subs (sentences). 

### [Step 5](https://github.com/adhadse/Deepdub/blob/master/deepdub/deepdub_audio.py#L93-L107): Accompaniments Overlay and Concatenation of audio segments.
The generated speech (`<hash>.wav`) is overlayed with accompaniments (`<hash>_accompaniments.wav`) to get `<hash>_gen.wav`. This ensures that we have speech in intended language + sound effects are preserved. At last we use `audio_segments_list.txt` to concatenate back the audio segments and produce the final output audio.

# Want to Contribute?
Look into [issues](https://github.com/adhadse/Deepdub/issues). You can begin with issue tagged `good first issue` or if you want to suggest something else, open a new issue.

---
1. This project uses [Spleeter](https://github.com/deezer/spleeter) for source separation.
```BibTeX
@article{spleeter2020,
  doi = {10.21105/joss.02154},
  url = {https://doi.org/10.21105/joss.02154},
  year = {2020},
  publisher = {The Open Journal},
  volume = {5},
  number = {50},
  pages = {2154},
  author = {Romain Hennequin and Anis Khlif and Felix Voituret and Manuel Moussallam},
  title = {Spleeter: a fast and efficient music source separation tool with pre-trained models},
  journal = {Journal of Open Source Software},
  note = {Deezer Research}
}
```

Install dependencies for *Spleeter*:
```
conda install -c conda-forge ffmpeg libsndfile
pip install spleeter
```
2. This project also uses [Deep Speaker](https://github.com/philipperemy/deep-speaker/blob/master/LICENSE) for speaker identification.
Install it's requirements by:
```
pip install -r deep_speaker/requirements.txt
```

Download pretrained models weights from [here](https://drive.google.com/file/d/1SJBmHpnaW1VcbFWP6JfvbT3wWP9PsqxS/view) or [from here](https://drive.google.com/file/d/1c1E1e_GzLtW5jD5uakkwL_Rw5sFxkLT4/view?usp=sharing) and put in `./pretrained_models` folder of current directory.
