# Deepdub
A complete end-to-end Deep Learning system to generate high quality human like speech in English for Korean Drama. (WIP)

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
