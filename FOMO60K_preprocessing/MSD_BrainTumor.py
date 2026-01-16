import os
import argparse
import shutil
import nibabel as nib
from os.path import join, basename, splitext
from tqdm import tqdm
from batchgenerators.utilities.file_and_folder_operations import maybe_mkdir_p as ensure_dir_exists


def main(source_path, dest_path, num_workers=12):
    subjects_dir = join(source_path, "imagesTr")

    if os.path.exists(dest_path):
        shutil.rmtree(dest_path)
    ensure_dir_exists(dest_path)

    nii_files = sorted([f for f in os.listdir(subjects_dir) if f.endswith(".nii.gz")])
    total_subjects = 0
    total_vols = 0

    for file in tqdm(nii_files, desc="Subjects"):
        subject_id = splitext(splitext(file)[0])[0]  # strips .nii.gz
        total_subjects += 1

        image_path = join(subjects_dir, file)
        vol = nib.load(image_path)

        # Split into modalities
        flair = vol.slicer[:, :, :, 0]
        t1w = vol.slicer[:, :, :, 1]
        t1gd = vol.slicer[:, :, :, 2]
        t2w = vol.slicer[:, :, :, 3]

        output_dir = join(dest_path, subject_id, "session_1")
        ensure_dir_exists(output_dir)

        # Save with preserved affine + header
        nib.save(nib.Nifti1Image(flair.get_fdata(), vol.affine, vol.header), join(output_dir, "flair.nii.gz"))
        nib.save(nib.Nifti1Image(t1w.get_fdata(), vol.affine, vol.header), join(output_dir, "t1w.nii.gz"))
        nib.save(nib.Nifti1Image(t1gd.get_fdata(), vol.affine, vol.header), join(output_dir, "t1gd.nii.gz"))
        nib.save(nib.Nifti1Image(t2w.get_fdata(), vol.affine, vol.header), join(output_dir, "t2w.nii.gz"))

        total_vols += 4

    print(f"Moved {total_vols} modality volumes from {total_subjects} subjects to {dest_path}")
    
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process data from MSD BrainTumor dataset")
    parser.add_argument(
        "--input",
        type=str,
        required=True,
        help="Path to MSD BrainTumor data directory"
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
