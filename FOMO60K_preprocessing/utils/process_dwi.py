import os
import numpy as np
import nibabel as nib
from os.path import join
from batchgenerators.utilities.file_and_folder_operations import (
    join,
    maybe_mkdir_p as ensure_dir_exists,
)
from yucca.pipeline.task_conversion.utils import should_use_volume


def get_best_basis(bvecs):
    """Finds the indices of the three bvecs closest to X, Y, and Z directions."""
    standard_basis = np.array(
        [[1, 0, 0], [0, 1, 0], [0, 0, 1]]  # X direction  # Y direction  # Z direction
    )

    best_match = []
    for std_vec in standard_basis:
        best_idx = None
        max_cosine = -1
        for i in range(bvecs.shape[1]):
            norm_bvec = np.linalg.norm(bvecs[:, i])
            if norm_bvec == 0:
                continue
            cos_sim = np.dot(bvecs[:, i], std_vec) / norm_bvec  # Normalized dot product
            if cos_sim > max_cosine:
                max_cosine = cos_sim
                best_idx = i
        best_match.append(best_idx)

    assert len(best_match) == 3
    return best_match


def get_data_for_bval(target_bvalue, bvals, bvecs, data):
    if target_bvalue == 0:
        b0_indices = np.where(bvals == 0)[0]
        if len(b0_indices) > 0:
            # Take the first volume instead of averaging
            return data[..., b0_indices[0]]

    # bval > 0
    target_bval_idx = np.where(bvals == target_bvalue)[0]
    if len(target_bval_idx) == 1:
        return data[..., target_bval_idx[0]]

    basis = get_best_basis(bvecs[:, target_bval_idx])
    selected_volumes = data[..., [target_bval_idx[i] for i in basis]]
    return np.mean(selected_volumes, axis=-1)


def extract_dwis(vol, bvalues, input_path):
    if input_path.endswith(".nii.gz"):
        base = input_path[:-7]  # strip ".nii.gz"
    else:
        base, _ = os.path.splitext(input_path)

    bvals_path = base + ".bval"
    bvecs_path = base + ".bvec"

    # Skip this volume if .bval or .bvec is missing
    if not os.path.exists(bvals_path) or not os.path.exists(bvecs_path):
        print(f"[SKIPPED] Missing bval or bvec for: {input_path}")
        return []  # Return empty list so nothing is saved

    bvals = np.loadtxt(bvals_path)
    bvecs = np.loadtxt(bvecs_path)

    dwis = []
    for bvalue in bvalues:
        if np.any(bvals == bvalue):
            dwi = get_data_for_bval(bvalue, bvals, bvecs, vol.get_fdata())
            dwis.append((dwi, bvalue))

    return dwis


def save_dwi(fdata, affine, header, output_dir, filename, check_before_saving=True):
    ensure_dir_exists(output_dir)
    output_path = join(output_dir, f"{filename}.nii.gz")

    # Make a copy of the header and fix the dim field
    new_header = header.copy()
    new_header.set_data_shape(fdata.shape)

    new_dwi = nib.Nifti1Image(fdata, affine=affine, header=new_header)

    use = should_use_volume(new_dwi) if check_before_saving else True

    if use:
        nib.save(new_dwi, output_path)

    return use
