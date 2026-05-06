# FOMO-MRI Dataset Preprocessing

**Links**: [[Paper]](https://arxiv.org/abs/2506.14432) | [[Pretraining Code]](https://github.com/Sllambias/asparagus) | [[FOMO300K]](https://huggingface.co/datasets/FOMO-MRI/FOMO300K) | [[FOMO260K]](https://huggingface.co/datasets/FOMO-MRI/FOMO260K) | [[FOMO50K]](https://huggingface.co/datasets/FOMO-MRI/FOMO50K) | [[FOMO45K]](https://huggingface.co/datasets/FOMO-MRI/FOMO45K)

This repository contains the preprocessing scripts to reproduce the FOMO-MRI datasets described in the paper:

**A large-scale heterogeneous 3D magnetic resonance brain imaging dataset for self-supervised learning**

The repository for pretraining and finetuning models as described in the paper is available here: https://github.com/Sllambias/asparagus

## Overview

The FOMO-MRI collection contains brain MRI scans from 900+ diverse sources, designed for self-supervised learning research. The collection is organized around two supersets — FOMO300K (raw) and FOMO50K (a co-registered, skull-stripped subset) — each with an openly licensed counterpart (FOMO260K and FOMO45K respectively) that excludes constituent datasets requiring Data Use Agreements. All datasets include varied acquisition protocols, scanner types, and patient populations.

## Dataset Access

The preprocessed datasets are available on HuggingFace:

| Dataset | Scans | Access | Description |
| --- | --- | --- | --- |
| [FOMO300K](https://huggingface.co/datasets/FOMO-MRI/FOMO300K) | 306,207 | Gated (auto-approved) | The full superset across the collection. Gated because some constituent datasets require Data Use Agreements. |
| [FOMO260K](https://huggingface.co/datasets/FOMO-MRI/FOMO260K) | 260,927 | Open (CC-BY-NC-SA) | The freely accessible subset of FOMO300K. No login or access request required. |
| [FOMO50K](https://huggingface.co/datasets/FOMO-MRI/FOMO50K) | 49,193 | Gated (auto-approved) | A co-registered, skull-stripped, and/or defaced subset of FOMO300K. |
| [FOMO45K](https://huggingface.co/datasets/FOMO-MRI/FOMO45K) | 46,149 | Open (CC-BY-NC-SA) | The freely accessible subset of FOMO50K. No login or access request required. |

> ⚠️ **Do not combine datasets from this collection.** Because each dataset is a subset of FOMO300K, combining them will result in duplicated scans.

## Repository Structure

- [`FOMO300K_preprocessing/`](./FOMO300K_preprocessing/) - Preprocessing scripts and dataset generation for FOMO300K (and its open subset FOMO260K)
- [`FOMO50K_preprocessing/`](./FOMO50K_preprocessing/) - FOMO50K subset preprocessing with coregistration and skull-stripping (and its open subset FOMO45K)
- [`scripts/`](./scripts/) - Analysis and visualization scripts

## Citation

If you use any of the FOMO-MRI datasets, please cite:

```bibtex
@article{Cerri2026large,
  title={A large-scale heterogeneous 3D magnetic resonance brain imaging dataset for self-supervised learning},
  author={Cerri, Stefano and Munk, Asbj{\o}rn and Llambias, Sebastian N{\o}rgaard and Ambsdorf, Jakob and Machnio, Julia and Nersesjan, Vardan and Hedeager Krag, Christian and Liu, Peirong and Rocamora Garc{\'\i}a, Pablo and Mehdipour Ghazi, Mostafa and Boesen, Mikael and Benros, Michael Eriksen and Iglesias, Juan Eugenio and Nielsen, Mads},
  journal={arXiv preprint arXiv:2506.14432},
  year={2026},
  url={https://arxiv.org/abs/2506.14432}
}
```