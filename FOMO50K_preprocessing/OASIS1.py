import os
import argparse
import shutil
import re
from os.path import join, basename, exists
from tqdm import tqdm
from batchgenerators.utilities.file_and_folder_operations import maybe_mkdir_p as ensure_dir_exists


def main(source_path, dest_path, num_workers=12):
    if exists(dest_path):
        shutil.rmtree(dest_path)
    ensure_dir_exists(dest_path)
    
    total_converted = 0
    
    # Get all subject directories
    all_subjects = sorted([d for d in os.listdir(source_path) 
                          if os.path.isdir(join(source_path, d))])
    
    for subject in tqdm(all_subjects, desc="Subjects"):
        # Expecting folder name like: OAS1_0001_MR1
        parts = subject.split('_')
        
        if len(parts) < 3 or not parts[2].startswith('MR'):
            print(f"Skipping unexpected folder format: {subject}")
            continue
        
        subject_id = f"{parts[0]}_{parts[1]}"
        session_number = parts[2][2:]  # Remove the "MR" prefix (e.g. "MR1" -> "1")
        session_label = f"session_{session_number}"
        
        session_path = join(source_path, subject, "RAW")
        
        if not exists(session_path):
            print(f"RAW folder not found for: {subject}")
            continue
        
        output_session_dir = join(dest_path, subject_id, session_label)
        ensure_dir_exists(output_session_dir)
        
        # Process .nii and .nii.gz files in the RAW folder only
        nii_files = [f for f in os.listdir(session_path) 
                     if f.endswith('.nii') or f.endswith('.nii.gz')]
        
        for filename in nii_files:
            # Skip files that contain ".4dfp." or do not have "mpr-"
            if ".4dfp." in filename or "mpr-" not in filename:
                continue
            
            # Remove the .nii or .nii.gz extension
            if filename.endswith('.nii.gz'):
                scan_base = filename[:-7]
            else:
                scan_base = filename[:-4]
            
            # Extract the part after "mpr-" up to the first underscore (e.g. from "mpr-1_anon", extract "1")
            match = re.search(r'mpr-([^_]*)', scan_base)
            if not match:
                continue
            
            t1_part = match.group(1)
            out_filename = f"T1_{t1_part}.nii.gz"
            out_path = join(output_session_dir, out_filename)
            
            # Copy the existing .nii or .nii.gz file
            src_file = join(session_path, filename)
            
            try:
                shutil.copy2(src_file, out_path)
                total_converted += 1
            except Exception as e:
                print(f"Error copying {src_file}: {e}")
                continue
    
    print(f"Converted {total_converted} scans into structured folders at: {dest_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process data from OASIS1 dataset")
    parser.add_argument(
        "--input",
        type=str,
        required=True,
        help="Path to OASIS1 data directory"
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
