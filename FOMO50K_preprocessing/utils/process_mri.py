import shutil
import os
import nibabel as nib
from os.path import join
from tqdm import tqdm
from batchgenerators.utilities.file_and_folder_operations import (
    join,
    maybe_mkdir_p as ensure_dir_exists,
)
from yucca.pipeline.task_conversion.utils import should_use_volume
from utils.process_dwi import extract_dwis, save_dwi

NUM_WORKERS = 12

# NB: This function doesnt allow for checking modalities.
def process_mri(mri):
    filename = mri["filename"]
    files_dir = mri["files_dir"]
    subject = mri["subject"]
    session = mri["session"]
    modality = mri["modality"]
    dest_path = mri["dest_path"]

    accepted = 0
    skipped_vols = []
    file_path = join(files_dir, filename)
    vol = nib.load(file_path)
    output_dir = join(dest_path, subject, session)

    if modality == "dwi":
        dwis = extract_dwis(vol, bvalues=[0, 1000], input_path=file_path)
        for dwi, bvalue in dwis:
            if save_dwi(
                dwi,
                affine=vol.affine,
                header=vol.header,
                output_dir=output_dir,
                filename=f"dwi_b{bvalue}",
                check_before_saving=True,
            ):
                accepted += 1
            else:
                skipped_vols.append(os.path.basename(file_path))
    else:
        if should_use_volume(vol):
            output_path = join(output_dir)
            ensure_dir_exists(output_path)
            if filename.endswith(".nii.gz"):
                shutil.copy2(file_path, output_path)
            else:
                new_filename = os.path.splitext(filename)[0] + ".nii.gz"
                nib.save(vol, join(output_path, new_filename))
            accepted += 1
        else:
            skipped_vols.append(os.path.basename(file_path))

    return accepted, skipped_vols
