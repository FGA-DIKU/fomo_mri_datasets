import shutil
import os
import argparse
from os.path import join
from tqdm import tqdm
from batchgenerators.utilities.file_and_folder_operations import (
    join,
    maybe_mkdir_p as ensure_dir_exists,
    subfiles,
)
from yucca.pipeline.task_conversion.utils import dirs_in_dir


def main(source_path, dest_path, num_workers=12):
    subjects_dir = join(source_path, "train", "ISBI2024-BraTS-GoAT-TrainingData")

    if os.path.exists(dest_path):
        shutil.rmtree(dest_path)
    ensure_dir_exists(dest_path)

    ext = ".nii.gz"
    vols = 0
    subjects = 0

    for subject in tqdm(dirs_in_dir(subjects_dir)):
        modalities_dir = join(subjects_dir, subject)
        subjects += 1
        for filename in subfiles(modalities_dir, join=False, suffix=ext):
            if "_seg" in filename:
                continue
            if "-seg" in filename:
                continue
            file_path = join(modalities_dir, filename)
            output_path = join(dest_path, subject, "session_1")
            ensure_dir_exists(output_path)
            shutil.copy2(file_path, output_path)
            vols += 1

    print(f"Moved: {vols} scans from {subjects} subjects")
    

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process data from BraTS-GEN dataset")
    parser.add_argument(
        "--input",
        type=str,
        required=True,
        help="Path to BraTS-GEN data directory"
    )
    parser.add_argument(
        "--output",
        type=str,
        required=True,
        help="Path to output directory"
    )
    parser.add_argument(
        "--num_workers",
        type=int,
        default=12,
        help="Number of worker processes (default: 12)"
    )
    
    args = parser.parse_args()
    
    main(args.input, args.output, args.num_workers)
