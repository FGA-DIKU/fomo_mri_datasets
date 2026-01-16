# FOMO300K Preprocessing Scripts

## Preprocessing Scripts

The complete set of 37 preprocessing scripts used to reproduce the FOMO300K dataset as described in the paper are available [here](https://github.com/Sllambias/asparagus_preprocessing/tree/main/asparagus_preprocessing/datasets_pretraining). FOMO300K comprises the first 37 datasets named sequentially from `PT001_DatasetName` through `PT037_DatasetName`.
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
@article{Cerri2025,
      title={{A large-scale heterogeneous 3D magnetic resonance brain imaging dataset for self-supervised learning}}, 
      author={Stefano Cerri* and Asbjørn Munk* Jakob Ambsdorf and Julia Machnio and Sebastian Nørgaard Llambias and Vardan Nersesjan and Christian Hedeager Krag and Peirong Liu and Pablo Rocamora García and Mostafa Mehdipour Ghazi and Mikael Boesen and Michael Eriksen Benros and Juan Eugenio Iglesias and Mads Nielsen},
      year={2025},
      url={https://arxiv.org/abs/2506.14432}, 
}
```
