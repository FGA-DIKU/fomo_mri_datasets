import shutil
import re
import os
import argparse
import numpy as np
import nibabel as nib
from tqdm import tqdm
from utils.process_mri import process_mri
from tqdm.contrib.concurrent import process_map
from os.path import join
from batchgenerators.utilities.file_and_folder_operations import (
    join,
    maybe_mkdir_p as ensure_dir_exists,
    subfiles,
)
from yucca.pipeline.task_conversion.utils import (
    dirs_in_dir,
)


def process_task(args):
    filename, scans_dir, subject, session, modality, dest_path = args

    accepted = 0
    skipped_vols = []
    file_path = join(scans_dir, filename)
    vol = nib.load(file_path)
    output_dir = join(dest_path, subject, session)
    output_path = join(output_dir, f"{modality}.nii.gz")

    if should_use_volume(vol):
        ensure_dir_exists(output_path)
        shutil.copy2(file_path, output_path)
        accepted = 1
    else:
        skipped_vols.append(os.path.basename(file_path))

    return accepted, skipped_vols


def main(source_path, dest_path, num_workers=12):
    subjects_dir = join(source_path, "ds005602-1.0.0")

    if os.path.exists(dest_path):
        shutil.rmtree(dest_path)
    ensure_dir_exists(dest_path)

    ext = ".nii.gz"

    vols = 0
    subjects = 0
    sessions = 0

    tasks = []
    for subject in dirs_in_dir(subjects_dir):
        subjects += 1
        modalities_dir = join(subjects_dir, subject)
        for modality in dirs_in_dir(modalities_dir):
            if modality in ["anat"]:
                scans_dir = join(modalities_dir, modality)
                for filename in subfiles(scans_dir, join=False, suffix=ext):
                    tasks.append(
                        {
                            "filename": filename,
                                "files_dir": scans_dir,
                                "subject": subject,
                                "session": "session_1",
                                "modality": modality,
                                "dest_path": dest_path,
                        }
                    )
                    vols += 1

    results = process_map(process_mri, tasks, max_workers=num_workers, chunksize=1)

    total_accepted = 0
    total_skipped_volumes = []
    total_skipped_modalities = []
    for accepted, skipped_vols in results:
        total_accepted += accepted
        total_skipped_volumes.extend(skipped_vols)

    print("Skipped volumes", total_skipped_volumes)
    print(
        f"Skipped {len(total_skipped_volumes)} volumes and {len(total_skipped_modalities)} modalities"
    )

    print(
        f"TOTAL (before skip/accept) {vols} scans from {sessions} from {subjects} subjects"
    )
    print(f"Accepted volumes: {total_accepted}")
    
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process data from IDEAS dataset")
    parser.add_argument(
        "--input",
        type=str,
        required=True,
        help="Path to IDEAS data directory"
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
