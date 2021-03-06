# Copyright 2022 The Deepdub Authors. All Rights Reserved.
# This file is part of Deepdub.
#
# Deepdub is free software: you can redistribute it and/or modify it under the terms of
# the GNU General Public License as published by the Free Software Foundation, either
# version 2 of the License, or (at your option) any later version.
#
# Deepdub is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
# PURPOSE. See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with Deepdub.
# If not, see <https://www.gnu.org/licenses/>.

import random
import numpy as np
from deep_speaker.audio import read_mfcc
from deep_speaker.batcher import sample_from_mfcc
from deep_speaker.constants import SAMPLE_RATE, NUM_FRAMES
from deep_speaker.conv_models import DeepSpeakerModel

from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
import pandas as pd

np.random.seed(123)
random.seed(123)

class DeepdubClusterer:
  """This Class is used for speaker diarization of audio segments.
  
  The idea to generate embeddings of audio segments of utterances by all 
  speakers and cluster these embeddings; thus identifying speakers and 
  their utterances. 
   
  Args:
    project_name: a project name you might want to give
    sentence_df: pd.DataFrame object created by 
      DeepdubSentence.get_sentences() method
    model_path: optional path leading to where the model used 
      generating embeddings is stored. 
      If not declared requires `ResCNN_triplet_training_checkpoint_265.h5`
      file stored in `pretrained_models` dir of base dir.
  """
  def __init__(self, project_name, sentence_df, model_path=None):
    self.model = DeepSpeakerModel()
    self.AUDIO_OUTPUT_DIR = f'./output_dir/{project_name}/audio_segments'
    self.sentence_df = sentence_df
    if model_path is not None:
      self.model.m.load_weights(model_path, by_name=True)
    else:
      self.model.m.load_weights(
        './pretrained_models/ResCNN_triplet_training_checkpoint_265.h5',
        by_name=True)
    
  def get_embeddings(self):
    """
    Applies embedding generating function for vocal audio files.
    Saves in `embedding` column and returns generated DataFrame
    
    Returns:
      sentence_df: generated sentence_df with `embedding` column
    """
    self.sentence_df[["embedding"]] = self.sentence_df[["hash"]].applymap(
      self.__generate_embedding)
    return self.sentence_df

  def __generate_embedding(self, h):
    """
    Generates a embedding given a `h` hash of audio segment
    """
    mfcc = sample_from_mfcc(read_mfcc(
      f'{self.AUDIO_OUTPUT_DIR}/{h}_vocals.wav', SAMPLE_RATE), NUM_FRAMES)
    # Call the model to get the embeddings of shape (1, 512) for each file.
    embedding = model.m.predict(np.expand_dims(mfcc, axis=0))
    return embedding.reshape((512,))
  
  def cluster(self, n_clusters, random_state=123):
    """
    Cluster generated embeddings to label them with one particular speaker
    in `label` column. 
    Args:
      n_cluster: number of cluster/speakers speaking in the clip
      random_state (optional): set random state for kmeans
    Returns:
      sentence_df: generated sentence_df with `label` column
      kmeans: scikit-learn kmeans object
    """
    embeddings = np.array(self.sentence_df["embedding"].tolist())
    kmeans = KMeans(n_clusters=n_clusters,
                    random_state=random_state).fit(
      embeddings
    )
    self.sentence_df['label'] = kmeans.labels_
    return self.sentence_df, kmeans

  def generate_scatter_3d():
    """
    Generate scatter 3d plotly plot of clustered embeddings
    by applying Pricipal Component Analysis.
    """
    pca = PCA(n_components=3)

    embeddings = np.array(self.sentence_df["embedding"].tolist())
    embeddings_df = self.sentence_df[["hash", "sentence"]].copy()
    embeddings_df['label'] = self.sentence_df['label'].copy()
    embeddings_df = pd.concat([
      embeddings_df, 
      pd.DataFrame(pca.fit_transform(embeddings))
    ], axis=1)
    
    total_var = pca.explained_variance_ratio_.sum() * 100
    fig = px.scatter_3d(
        embeddings_df,x=0, y=1, z=2, color='label',
        title=f'Total Explained Variance: {total_var:.2f}%<br>Hotel Del Luna Ep6 | from 00:06:26 to 00:08:50',
        labels={'0': 'PC 1', '1': 'PC 2', '2': 'PC 3'},
        hover_name="sentence", 
        hover_data=["label", "hash"]
    )
    fig.show()
