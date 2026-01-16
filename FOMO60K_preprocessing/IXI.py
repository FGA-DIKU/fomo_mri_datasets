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
    file_path, subject, filename, dest_path, modality = args

    accepted = 0
    skipped_vols = []

    subject_dir = join(dest_path, subject, "session_1")  # Ensure "session_1" subdir
    ensure_dir_exists(subject_dir)

    if modality == "DTI":
        # Extract b0 (first volume ending with "-00.nii.gz")
        b0_path = file_path
        if not os.path.exists(b0_path):
            print(f"Warning: Missing b0 file for {subject}")
            return 0, []

        img_b0 = nib.load(b0_path)
        data_b0 = img_b0.get_fdata()
        affine = img_b0.affine
        header = img_b0.header

        output_b0 = join(subject_dir, filename.replace(".nii.gz", "_b0.nii.gz"))
        nib.save(nib.Nifti1Image(data_b0, affine, header), output_b0)
        print(f"Saved b0 image: {output_b0}")

        # Extract b1000 (average of "-01.nii.gz", "-02.nii.gz", "-03.nii.gz")
        b1000_filenames = [
            filename.replace("-DTI-00.nii.gz", f"-DTI-{i:02d}.nii.gz")
            for i in range(1, 4)
        ]
        b1000_paths = [
            join(os.path.dirname(file_path), fname) for fname in b1000_filenames
        ]
        valid_b1000_paths = [p for p in b1000_paths if os.path.exists(p)]

        if len(valid_b1000_paths) == 3:
            imgs_b1000 = [nib.load(p).get_fdata() for p in valid_b1000_paths]
            data_b1000 = np.mean(
                np.stack(imgs_b1000, axis=-1), axis=-1
            )  # Averaging over volumes
            output_b1000 = join(
                subject_dir, filename.replace(".nii.gz", "_b1000.nii.gz")
            )
            nib.save(nib.Nifti1Image(data_b1000, affine, header), output_b1000)
            print(f"Saved b1000 image: {output_b1000}")
        else:
            print(
                f"Warning: Missing b1000 volumes for {subject}. Found {len(valid_b1000_paths)}"
            )

        accepted = 1

    else:
        # Preserve original file name and copy it to session_1
        output_path = join(subject_dir, filename)
        ensure_dir_exists(subject_dir)
        shutil.copy2(file_path, output_path)  # Copying without modifying input
        accepted = 1

    return accepted, skipped_vols


def get_tasks(dir, modality, dest_path):
    tasks = []
    for filename in subfiles(dir, join=False, suffix=".nii.gz"):
        if modality == "DTI" and not filename.endswith("-DTI-00.nii.gz"):
            continue  # Only process the first volume for DTI; others handled inside process_task

        file_path = join(dir, filename)
        subject = filename.split("-")[0]  # Extracts IXI number
        tasks.append((file_path, subject, filename, dest_path, modality))

    return tasks


def main(source_path, dest_path, num_workers=12):

    # Ensure the output directory is safe to use
    if os.path.exists(dest_path):
        shutil.rmtree(dest_path)
    ensure_dir_exists(dest_path)

    tasks = []
    tasks.extend(get_tasks(join(source_path, "T1"), "T1", dest_path))
    tasks.extend(get_tasks(join(source_path, "T2"), "T2", dest_path))
    tasks.extend(get_tasks(join(source_path, "PD"), "PD", dest_path))
    tasks.extend(get_tasks(join(source_path, "DTI"), "DTI", dest_path))

    results = process_map(process_task, tasks, max_workers=num_workers, chunksize=1)

    total_accepted = sum(result[0] for result in results)
    total_skipped_volumes = [v for result in results for v in result[1]]

    print(f"Skipped {len(total_skipped_volumes)} volumes")
    print("Skipped volumes:", total_skipped_volumes)
    print(f"Accepted volumes: {total_accepted}")
    
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process data from IXI dataset")
    parser.add_argument(
        "--input",
        type=str,
        required=True,
        help="Path to IXI data directory"
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
