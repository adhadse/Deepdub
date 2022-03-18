# Deepdub
A complete end-to-end Deep Learning system to generate high quality human like speech in English for Korean Drama. (WIP)

---
This project uses [Spleeter](https://github.com/deezer/spleeter) for source separation.

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

This software uses code of <a href=http://ffmpeg.org>FFmpeg</a> licensed under the <a href=http://www.gnu.org/licenses/old-licenses/lgpl-2.1.html>LGPLv2.1</a> and its source can be downloaded <a href=link_to_your_sources>here</a>
