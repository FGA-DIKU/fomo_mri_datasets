# FOMO50K Preprocessing Scripts

This repository contains scripts for preprocessing brain MRI datasets to create FOMO50K. The preprocessing pipeline consists of three main stages that transform raw neuroimaging data into a standardized, BIDS-compatible format.

## Overview

The preprocessing pipeline handles structural and diffusion MRI data through three sequential stages:

1. **Initial Processing** (Python scripts): Filter and 4D-to-3D convert diffusion scans
2. **MRI Processing** (Bash scripts): RAS, coregister, and skull-strip
3. **Dataset Assembly** (Reshuffling script): Combine processed datasets into final BIDS-compatible FOMO50K structure

> **Note on FOMO50K vs. the original FOMO60K release:** FOMO50K is the current version of what was originally released as FOMO60K. The MGH-Wild dataset has been removed from the collection, and the remaining scans are now distributed as FOMO50K (gated, ~49K scans) and its open subset FOMO45K (~46K scans).

## Requirements

### Software Dependencies
- Python 3.x with the following packages:
  - nibabel
  - numpy
  - yucca
  - batchgenerators
- FreeSurfer (required for Stage 2)

## Pipeline Stages

### Stage 1: Initial Processing (Python Scripts)

Extract structural and diffusion scans from raw data and convert 4D diffusion scans to 3D.

#### Usage

For each dataset, run the corresponding Python script:
```bash
python DATASET_X.py --input /path/to/raw_data --output /path/to/temp_folder [--num_workers N]
```

#### Arguments
- `--input` or `-i`: Path to the raw dataset directory
- `--output` or `-o`: Path to temporary output folder for processed data
- `--num_workers` (optional): Number of parallel workers for processing (default: 1)

#### Example
```bash
# Process AOMIC dataset with 8 workers
python aomic.py --input /data/raw/aomic --output /data/temp/aomic --num_workers 8

# Process IXI dataset
python IXI.py -i /data/raw/IXI -o /data/temp/IXI
```

#### Output
- Temporary folder containing:
  - Structural scans (T1w, T2w, etc.)
  - Diffusion scans converted from 4D to 3D

### Stage 2: MRI Processing (Bash Scripts)

Apply RAS orientation conversion, MRI coregistration, and skull-stripping (dataset-dependent).

#### Usage

For each dataset, run the corresponding bash script:
```bash
bash DATASET_X.sh -i /path/to/temp_folder -o /path/to/output_folder
```

#### Arguments
- `-i`: Input directory (output from Stage 1)
- `-o`: Output directory for processed data

#### Requirements
- FreeSurfer must be installed and properly configured
- Set `FREESURFER_HOME` environment variable or pass it as argument `-f`

#### Example
```bash
# Process AOMIC dataset
bash aomic.sh -i /data/temp/aomic -o /data/processed/aomic

# Process IXI dataset
bash IXI.sh -i /data/temp/IXI -o /data/processed/IXI
```

#### Processing Steps
The bash scripts perform:
1. **RAS Conversion**: Convert all images to standard RAS orientation (Right-Anterior-Superior)
2. **MRI Coregistration**: Align scans within each session
3. **Skull-stripping**: Remove non-brain tissue (applied selectively based on dataset)

#### Output
- Processed dataset folder containing:
  - RAS-oriented volumes
  - Coregistered scans
  - Skull-stripped images (where applicable)

### Stage 3: Dataset Assembly (Reshuffling)

Combine all processed datasets into the final FOMO50K structure in modified BIDS format.

#### Usage
```bash
bash dataset_merger_and_bidsify.sh -i /path/to/dataset_list.txt -o /path/to/FOMO50K_output
```

#### Arguments
- `-i`: Path to text file containing list of processed dataset directories and their corresponding file names in the dataset (one per line)
- `-o`: Path to final FOMO50K output directory

#### Dataset List File Format

Create a text file (e.g., `datasets_to_include.txt`) with one dataset path per line:
```text
/data/processed/aomic PT001_AOMIC1000
/data/processed/arc PT002_ARC
/data/processed/brats24 PT003_BraTS-GEN
/data/processed/dlbs PT004_DLBS
/data/processed/IXI PT005_IXI
/data/processed/nki PT006_NKI
/data/processed/soop PT007_SOOP
```

Lines starting with `#` are treated as comments and ignored.

#### Example
```bash
# Create dataset list
cat > datasets_to_include.txt << EOF
/data/processed/aomic PT001_AOMIC1000
/data/processed/arc PT002_ARC
/data/processed/IXI PT003_IXI
EOF

# Run reshuffling
bash dataset_merger_and_bidsify.sh -i datasets_to_include.txt -o /data/FOMO50K
```

#### Output
- Final FOMO50K directory with:
  - Modified BIDS-compatible structure
  - Standardized naming conventions

## Complete Pipeline Example

Here's a complete example processing three datasets:
```bash
#!/bin/bash

# Stage 1: Initial processing
python aomic.py -i /raw/aomic -o /temp/aomic --num_workers 8
python IXI.py -i /raw/IXI -o /temp/IXI --num_workers 8
python nki.py -i /raw/nki -o /temp/nki --num_workers 8

# Stage 2: MRI processing (requires FreeSurfer)
source $FREESURFER_HOME/SetUpFreeSurfer.sh
bash aomic.sh -i /temp/aomic -o /processed/aomic
bash IXI.sh -i /temp/IXI -o /processed/IXI
bash nki.sh -i /temp/nki -o /processed/nki

# Stage 3: Create dataset list and assemble final FOMO50K
cat > datasets.txt << EOF
/processed/aomic PT001_AOMIC1000
/processed/IXI PT002_IXI
/processed/nki PT003_NKI
EOF

bash dataset_merger_and_bidsify.sh -i datasets.txt -o /final/FOMO50K
```

## Dataset-Specific Notes

### Removed source: MGH-Wild
MGH-Wild was part of the original FOMO60K release but has been removed from the FOMO50K and FOMO45K releases. Any scripts or dataset-list entries referencing MGH-Wild should be omitted.

### Skull-stripping
Not all datasets undergo skull-stripping in Stage 2. The decision is made per dataset based on whether the scans are already skull-stripped or not.

Check individual bash scripts to see if skull-stripping is enabled for a specific dataset.

## Output Structure

The final FOMO50K dataset follows a modified BIDS structure:
```
FOMO50K/
├── PT001_Dataset1/
│   ├── sub-x/
│   │   └── ses-y/
│   │       ├── anat/
│   │           └── FLAIR.nii.gz
│   │       └── dwi/
│   │           └── dwi.nii.gz 
│   └── sub-z/
├── PT002_Dataset2/
└── ...
```

## Note on Metadata

The metadata available on HuggingFace for FOMO50K was matched from the FOMO300K dataset and not regenerated during the FOMO50K preprocessing pipeline. For metadata generation scripts, please refer to the [FOMO300K preprocessing code](../FOMO300K_preprocessing/).

## Citation

If you use the FOMO50K dataset or these preprocessing scripts, please cite:
```bibtex
@article{Cerri2026large,
  title={A large-scale heterogeneous 3D magnetic resonance brain imaging dataset for self-supervised learning},
  author={Cerri, Stefano and Munk, Asbj{\o}rn and Llambias, Sebastian N{\o}rgaard and Ambsdorf, Jakob and Machnio, Julia and Nersesjan, Vardan and Hedeager Krag, Christian and Liu, Peirong and Rocamora Garc{\'\i}a, Pablo and Mehdipour Ghazi, Mostafa and Boesen, Mikael and Benros, Michael Eriksen and Iglesias, Juan Eugenio and Nielsen, Mads},
  journal={arXiv preprint arXiv:2506.14432},
  year={2026},
  url={https://arxiv.org/abs/2506.14432}
}
```