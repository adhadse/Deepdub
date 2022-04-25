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

class DeepdubClusterer():
  def __init__(self, project_name, sentence_df, model_path=None):
    """
    TODO
    """
    self.model = DeepSpeakerModel()
    self.AUDIO_OUTPUT_DIR = f'./output_dir/{project_name}/audio_segments'
    self.sentence_df = sentence_df
    if model_path is not None:
      self.model.m.load_weights(MODEL_PATH, by_name=True)
    else:
      self.model.m.load_weights(
        './pretrained_models/ResCNN_triplet_training_checkpoint_265.h5',
        by_name=True)
    
  def get_embeddings(self):
    """
    Applies embedding generating function for vocal audio files.
    Saves in `embedding` column and returns generated DataFrame
    ### Returns:
    - sentence_df: generated sentence_df with `embedding` column
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
    ### Parameters:
    - n_cluster: number of cluster/speakers speaking in the clip
    - random_state (optional): set random state for kmeans
    ### Returns:
    - sentence_df: generated sentence_df with `label` column
    - kmeans: scikit-learn kmeans object
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
