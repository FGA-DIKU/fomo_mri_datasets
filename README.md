# FOMO300K and FOMO60K Preprocessing

This repository contains the preprocessing scripts to reproduce the FOMO300K and FOMO60K datasets described in the paper:

**A large-scale heterogeneous 3D magnetic resonance brain imaging dataset for self-supervised learning**

The repository for pretraining and finetuning models as described in the paper is available here: https://github.com/Sllambias/asparagus

## Overview

FOMO300K and FOMO60K are datasets of brain MRI scans from 900+ diverse sources, designed for self-supervised learning research. FOMO300K contains ~300,000 scans, while FOMO60K is a subset of ~60,000 scans with additional coregistration and skull-stripping preprocessing. Both datasets include varied acquisition protocols, scanner types, and patient populations.

## Dataset Access

The preprocessed datasets are available on HuggingFace:

- **FOMO300K**: https://huggingface.co/datasets/FOMO-MRI/FOMO300K
- **FOMO60K**: https://huggingface.co/datasets/FOMO-MRI/FOMO60K

## Repository Structure

- [`FOMO300K_preprocessing/`](./FOMO300K_preprocessing/) - Preprocessing scripts and dataset generation for FOMO300K
- [`FOMO60K_preprocessing/`](./FOMO60K_preprocessing/) - FOMO60K subset preprocessing (with coregistration and skull-stripping)
- [`scripts/`](./scripts/) - Analysis and visualization scripts

## Citation

If you use the FOMO300K or FOMO60K datasets, please cite:

```bibtex
@article{Cerri2025,
      title={{A large-scale heterogeneous 3D magnetic resonance brain imaging dataset for self-supervised learning}}, 
      author={Stefano Cerri* and Asbjørn Munk* Jakob Ambsdorf and Julia Machnio and Sebastian Nørgaard Llambias and Vardan Nersesjan and Christian Hedeager Krag and Peirong Liu and Pablo Rocamora García and Mostafa Mehdipour Ghazi and Mikael Boesen and Michael Eriksen Benros and Juan Eugenio Iglesias and Mads Nielsen},
      year={2025},
      url={https://arxiv.org/abs/2506.14432}, 
}
```