import nibabel as nib
import pandas as pd
import numpy as np
from pathlib import Path
import argparse

def get_slice_thickness(nii_file):
    """
    Extract slice thickness from a NIfTI file using the affine matrix.
    Computes voxel spacing along all 3 dimensions and returns the maximum.
    """
    try:
        img = nib.load(nii_file)
        affine = img.affine
        
        voxel_spacing = img.header['pixdim'][1:4]
        
        # Slice thickness is the maximum spacing
        slice_thickness = np.max(voxel_spacing)
        
        # Compute voxel spacing from affine matrix
        # The spacing is the norm of each column (excluding the last column)
        #voxel_spacing = np.sqrt(np.sum(affine[:3, :3]**2, axis=0))
        
        # Slice thickness is the maximum spacing
        #slice_thickness = np.max(voxel_spacing)
        
        return slice_thickness
    except Exception as e:
        print(f"Error processing {nii_file}: {e}")
        return None

def process_FOMO300K_datasets(input_dir='.', output_file='FOMO300K_slice_thickness.csv'):
    """
    Process all datasets in the specified directory 
    
    Args:
        input_dir: Directory containing PT* folders with NIfTI files (default: current directory)
        output_file: Output CSV filename (default: 'FOMO300K_slice_thickness.csv')
    """
    # Get input directory
    current_dir = Path(input_dir)
    
    if not current_dir.exists():
        print(f"Error: Directory {input_dir} does not exist!")
        return
    
    # List to store results
    results = []
    
    # Iterate through all subdirectories (PT datasets)
    for folder in current_dir.iterdir():
        if folder.is_dir():
            dataset_name = folder.name
            
            # Find all .nii.gz files in this folder (including subdirectories)
            nii_files = list(folder.rglob('*.nii.gz'))
            
            for nii_file in nii_files:
                thickness = get_slice_thickness(nii_file)
                
                if thickness is not None:
                    results.append({
                        'dataset_name': dataset_name,
                        'file_path': str(nii_file),
                        'slice_thickness': thickness
                    })
                    print(f"Processed: {nii_file} - Thickness: {thickness}")
    
    # Create DataFrame and save to CSV
    df = pd.DataFrame(results)
    df.to_csv(output_file, index=False)
    
    print(f"\nFOMO300K Analysis complete! Results saved to {output_file}")
    print(f"Total files processed: {len(results)}")

    # Print summary statistics
    if len(results) > 0:
        print(f"\nSlice thickness statistics:")
        print(df['slice_thickness'].describe())

def process_OpenMind_dataset(openmind_dir, output_file='OpenMind_slice_thickness.csv'):
    """
    Process OpenMind dataset structure, extracting only original images
    (excluding defaced versions and masks).
    
    Args:
        openmind_dir: Path to the OpenMind dataset directory
        output_file: Output CSV filename (default: 'OpenMind_slice_thickness.csv')
    """
    openmind_dir_path = Path(openmind_dir)
    
    if not openmind_dir_path.exists():
        print(f"Error: Directory {openmind_dir} does not exist!")
        return
    
    # List to store results
    results = []
    
    # Iterate through all dataset folders (ds_000001, ds_000002, etc.)
    for ds_folder in openmind_dir_path.iterdir():
        if ds_folder.is_dir() and ds_folder.name.startswith('ds'):
            dataset_name = ds_folder.name
            
            # Find all .nii.gz files in this dataset
            nii_files = list(ds_folder.rglob('*.nii.gz'))
            
            for nii_file in nii_files:
                
                # Skip files with 'mask' in the name
                if 'mask' in nii_file.name.lower():
                    continue
                
                # Skip files with 'deface' in the name
                if 'deface' in nii_file.name.lower():
                    continue
                
                thickness = get_slice_thickness(nii_file)
                
                if thickness is not None:
                    results.append({
                        'dataset_name': dataset_name,
                        'file_path': str(nii_file.relative_to(openmind_dir_path)),
                        'slice_thickness': thickness
                    })
                    print(f"Processed: {nii_file.name} - Thickness: {thickness}")
    
    # Create DataFrame and save to CSV
    df = pd.DataFrame(results)
    df.to_csv(output_file, index=False)
    
    print(f"\nOpenMind analysis complete! Results saved to {output_file}")
    print(f"Total files processed: {len(results)}")
    
    # Print summary statistics
    if len(results) > 0:
        print(f"\nSlice thickness statistics:")
        print(df['slice_thickness'].describe())

def process_FOMO60K_paths(paths_list, output_file='FOMO60K_slice_thickness.csv'):
    """
    Process specific paths provided in a list.
    Only processes files ending with .nii or .nii.gz
    
    Args:
        paths_list: List of paths to directories or files to process
        output_file: Output CSV filename (default: 'FOMO60K_slice_thickness.csv')
    """
    results = []
    
    for path_str in paths_list:
        path = Path(path_str)
        
        if not path.exists():
            print(f"Warning: Path does not exist: {path}")
            continue
        
        # Extract dataset name from the path (last directory name in the given path)
        dataset_name = path.name
        
        nii_files = []
        
        if path.is_file():
            # If it's a file, check if it's a NIfTI file
            if path.suffix == '.gz' and path.stem.endswith('.nii'):
                nii_files.append(path)
            elif path.suffix == '.nii':
                nii_files.append(path)
        elif path.is_dir():
            # If it's a directory, find all .nii and .nii.gz files
            nii_files.extend(path.rglob('*.nii.gz'))
            nii_files.extend(path.rglob('*.nii'))
        
        for nii_file in nii_files:
            thickness = get_slice_thickness(nii_file)
            
            if thickness is not None:
                results.append({
                    'dataset_name': dataset_name,
                    'file_path': str(nii_file),
                    'slice_thickness': thickness
                })
                print(f"Processed: {nii_file} - Thickness: {thickness}")
    
    # Create DataFrame and save to CSV
    df = pd.DataFrame(results)
    df.to_csv(output_file, index=False)
    
    print(f"\nFOMO60K analysis complete! Results saved to {output_file}")
    print(f"Total files processed: {len(results)}")
    
    # Print summary statistics
    if len(results) > 0:
        print(f"\nSlice thickness statistics:")
        print(df['slice_thickness'].describe())

def load_paths_from_file(filepath):
    """
    Load paths from a text file (one path per line).
    Lines starting with # are treated as comments.
    
    Args:
        filepath: Path to the text file containing paths
    
    Returns:
        List of paths
    """
    paths = []
    with open(filepath, 'r') as f:
        for line in f:
            line = line.strip()
            # Skip empty lines and comments
            if line and not line.startswith('#'):
                paths.append(line)
    return paths

def main():
    parser = argparse.ArgumentParser(
        description='Compute slice thickness from NIfTI files',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Process FOMO300K in current directory
  python script.py --FOMO300K
  
  # Process FOMO300K in specific directory with custom output
  python script.py --FOMO300K --input /path/to/datasets --output my_output.csv
  
  # Process OpenMind dataset
  python script.py --OpenMind --openmind-dir /path/to/OpenMind --output OpenMind.csv
  
  # Process FOMO60K with paths from file
  python script.py --FOMO60K --paths-file fomo60k_paths.txt --output FOMO60K.csv
  
  # Process FOMO60K with direct paths
  python script.py --FOMO60K --paths /path/to/aomic /path/to/arc
        """
    )
    
    # Dataset selection flags
    parser.add_argument('--FOMO300K', action='store_true', 
                        help='Process all datasets in input directory (FOMO300K)')
    parser.add_argument('--OpenMind', action='store_true',
                        help='Process OpenMind dataset')
    parser.add_argument('--FOMO60K', action='store_true',
                        help='Process FOMO60K dataset')
    
    # Input/output options
    parser.add_argument('-i', '--input', default='.',
                        help='Input directory for FOMO300K (default: current directory)')
    parser.add_argument('-o', '--output',
                        help='Output CSV filename (default depends on dataset type)')
    parser.add_argument('--openmind-dir',
                        help='Path to OpenMind dataset directory (required for --OpenMind)')
    parser.add_argument('--paths', nargs='+',
                        help='List of paths to process for FOMO60K (space-separated)')
    parser.add_argument('--paths-file',
                        help='Text file containing paths to process for FOMO60K (one per line)')
    
    args = parser.parse_args()
    
    # If no flags are provided, show help
    if not (args.FOMO300K or args.OpenMind or args.FOMO60K):
        parser.print_help()
        return
    
    # Execute requested functionalities
    if args.FOMO300K:
        print("=" * 60)
        print(f"Processing FOMO300K datasets in: {args.input}")
        print("=" * 60)
        output_file = args.output if args.output else 'FOMO300K_slice_thickness.csv'
        process_FOMO300K_datasets(args.input, output_file)
        print()
    
    if args.OpenMind:
        if not args.openmind_dir:
            print("Error: --openmind-dir is required when using --OpenMind")
            return
        
        print("=" * 60)
        print(f"Processing OpenMind dataset in: {args.openmind_dir}")
        print("=" * 60)
        output_file = args.output if args.output else 'OpenMind_slice_thickness.csv'
        process_OpenMind_dataset(args.openmind_dir, output_file)
        print()
    
    if args.FOMO60K:
        # Determine paths to process
        fomo60k_paths = []
        
        if args.paths_file:
            print(f"Loading paths from file: {args.paths_file}")
            fomo60k_paths = load_paths_from_file(args.paths_file)
        elif args.paths:
            fomo60k_paths = args.paths
        else:
            print("Error: Either --paths or --paths-file is required when using --FOMO60K")
            return
        
        print("=" * 60)
        print(f"Processing FOMO60K with {len(fomo60k_paths)} paths...")
        print("=" * 60)
        output_file = args.output if args.output else 'FOMO60K_slice_thickness.csv'
        process_FOMO60K_paths(fomo60k_paths, output_file)
        print()

if __name__ == "__main__":
    main()
