import pandas as pd
import os
from pathlib import Path
import argparse


def merge_subjects_csv(input_folder='.', output_folder='.'):
    """
    Merge participants.tsv, mapping.tsv, and mri_info.tsv files from PT* folders.
    
    Args:
        input_folder: Path to folder containing PT* directories (default: current directory)
        output_folder: Path to folder where merged files will be saved (default: current directory)
    """
    input_path = Path(input_folder)
    output_path = Path(output_folder)
    
    # Create output folder if it doesn't exist
    output_path.mkdir(parents=True, exist_ok=True)
    
    subjects_dfs = []
    mapping_dfs = []
    mri_info_dfs = []
    missing_files = []
    
    # Process PT folders
    for folder in sorted(input_path.glob('PT*')):
        if not folder.is_dir():
            continue
            
        if folder.name == 'PT030_OpenNeuro':
            # Handle OpenNeuro subfolders
            for subfolder in folder.glob('ds*'):
                dataset_name = f'PT030_OpenNeuro/{subfolder.name}'
                subjects_path = subfolder / 'participants.tsv'
                mapping_path = subfolder / 'mapping.tsv'
                mri_info_path = subfolder / 'mri_info.tsv'
                
                subjects_exists = subjects_path.exists()
                mapping_exists = mapping_path.exists()
                mri_info_exists = mri_info_path.exists()
                
                # Check for missing files and warn
                if subjects_exists and not mapping_exists:
                    missing_files.append(f"{dataset_name}: has participants.tsv but missing mapping.tsv")
                elif mapping_exists and not subjects_exists:
                    missing_files.append(f"{dataset_name}: has mapping.tsv but missing participants.tsv")
                elif not subjects_exists and not mapping_exists:
                    missing_files.append(f"{dataset_name}: missing both participant.tsv and mapping.tsv")
                
                # Process participants.tsv
                if subjects_exists:
                    df = pd.read_csv(subjects_path, sep='\t')
                    df.insert(0, 'dataset', dataset_name)
                    subjects_dfs.append(df)
                
                # Process mapping.tsv
                if mapping_exists:
                    df = pd.read_csv(mapping_path, sep='\t')
                    df.insert(0, 'dataset', dataset_name)
                    mapping_dfs.append(df)
                
                # Process mri_info.tsv
                if mri_info_exists:
                    df = pd.read_csv(mri_info_path, sep='\t')
                    df.insert(0, 'dataset', dataset_name)
                    mri_info_dfs.append(df)
        else:
            # Handle regular PT folders
            dataset_name = folder.name
            subjects_path = folder / 'participants.tsv'
            mapping_path = folder / 'mapping.tsv'
            mri_info_path = folder / 'mri_info.tsv'
            
            subjects_exists = subjects_path.exists()
            mapping_exists = mapping_path.exists()
            mri_info_exists = mri_info_path.exists()
            
            # Check for missing files and warn
            if subjects_exists and not mapping_exists:
                missing_files.append(f"{dataset_name}: has participants.tsv but missing mapping.tsv")
            elif mapping_exists and not subjects_exists:
                missing_files.append(f"{dataset_name}: has mapping.tsv but missing participants.tsv")
            elif not subjects_exists and not mapping_exists:
                missing_files.append(f"{dataset_name}: missing both participants.tsv and mapping.tsv")
            
            # Process participants.tsv
            if subjects_exists:
                df = pd.read_csv(subjects_path, sep='\t')
                df.insert(0, 'dataset', dataset_name)
                subjects_dfs.append(df)
            
            # Process mapping.tsv
            if mapping_exists:
                df = pd.read_csv(mapping_path, sep='\t')
                df.insert(0, 'dataset', dataset_name)
                mapping_dfs.append(df)
            
            # Process mri_info.tsv
            if mri_info_exists:
                df = pd.read_csv(mri_info_path, sep='\t')
                df.insert(0, 'dataset', dataset_name)
                mri_info_dfs.append(df)
    
    # Print warnings for missing files
    if missing_files:
        print("WARNING: Missing files detected:")
        for warning_msg in missing_files:
            print(f"  {warning_msg}")
        print()
    
    # Merge subjects dataframes
    if subjects_dfs:
        merged_subjects = pd.concat(subjects_dfs, ignore_index=True, sort=False)
        
        # Keep only specified columns for subjects
        columns_to_keep = ['dataset', 'participant_id', 'session_id', 'sex', 'age', 'handedness', 'group']
        merged_subjects = merged_subjects.reindex(columns=columns_to_keep)
        
        merged_subjects.to_csv(output_path / 'participants.tsv', sep='\t', index=False)
        print(f"Merged {len(subjects_dfs)} participants TSV files -> {output_path / 'participants.tsv'}")
    else:
        print("No participant.tsv files found")
    
    # Merge mapping dataframes
    if mapping_dfs:
        merged_mapping = pd.concat(mapping_dfs, ignore_index=True, sort=False)
        merged_mapping.to_csv(output_path / 'mapping.tsv', sep='\t', index=False)
        print(f"Merged {len(mapping_dfs)} mapping TSV files -> {output_path / 'mapping.tsv'}")
    else:
        print("No mapping.tsv files found")
    
    # Merge mri_info dataframes
    if mri_info_dfs:
        merged_mri_info = pd.concat(mri_info_dfs, ignore_index=True, sort=False)
        merged_mri_info.to_csv(output_path / 'mri_info.tsv', sep='\t', index=False)
        print(f"Merged {len(mri_info_dfs)} mri_info TSV files -> {output_path / 'mri_info.tsv'}")
    else:
        print("No mri_info.tsv files found")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Merge participants.tsv, mapping.tsv, and mri_info.tsv files from PT* folders'
    )
    parser.add_argument(
        '-i', '--input',
        default='.',
        help='Input folder containing PT* directories (default: current directory)'
    )
    parser.add_argument(
        '-o', '--output',
        default='.',
        help='Output folder for merged TSV files (default: current directory)'
    )
    
    args = parser.parse_args()
    merge_subjects_csv(args.input, args.output)
