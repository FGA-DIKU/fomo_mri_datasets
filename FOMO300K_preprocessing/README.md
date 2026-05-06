# FOMO300K Preprocessing Scripts

## Preprocessing Scripts

The complete set of 36 preprocessing scripts used to reproduce the FOMO300K dataset as described in the paper are available [here](https://github.com/Sllambias/asparagus_preprocessing/tree/main/asparagus_preprocessing/datasets_pretraining). FOMO300K comprises the first 36 datasets named sequentially from `PT001_DatasetName` through `PT036_DatasetName`.
### Usage

To reproduce the exact FOMO300K dataset, run each script with the following flags:
```bash
python PT00X_DatasetX.py --bidsify --save-dset-metadata --save-as-nifti
```

These flags ensure:
- `--bidsify`: Converts data to BIDS format
- `--save-dset-metadata`: Saves dataset patient metadata
- `--save-as-nifti`: Saves outputs in NIfTI format

## Dataset Overview
For scripts to analyze and visualize the FOMO300K dataset, see the [`scripts/`](../scripts/) folder in this repository.

## Citation
If you use the FOMO300K dataset or these preprocessing scripts, please cite:
```bibtex
@article{Cerri2026large,
  title={A large-scale heterogeneous 3D magnetic resonance brain imaging dataset for self-supervised learning},
  author={Cerri, Stefano and Munk, Asbj{\o}rn and Llambias, Sebastian N{\o}rgaard and Ambsdorf, Jakob and Machnio, Julia and Nersesjan, Vardan and Hedeager Krag, Christian and Liu, Peirong and Rocamora Garc{\'\i}a, Pablo and Mehdipour Ghazi, Mostafa and Boesen, Mikael and Benros, Michael Eriksen and Iglesias, Juan Eugenio and Nielsen, Mads},
  journal={arXiv preprint arXiv:2506.14432},
  year={2026},
  url={https://arxiv.org/abs/2506.14432}
}
```
