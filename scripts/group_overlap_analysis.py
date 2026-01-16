import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import argparse
from pathlib import Path
from data_utils import merge_groups, COLORS

sns.set_style("whitegrid", {'grid.linestyle': '--', 'grid.alpha': 0.3})
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.size'] = 14

def load_datasets(fomo60k_path, fomo300k_path, openmind_path):
    """Load participant data from all three datasets"""
    fomo60k = pd.read_csv(fomo60k_path, sep='\t')
    fomo300k = pd.read_csv(fomo300k_path, sep='\t')
    openmind = pd.read_csv(openmind_path)  # CSV not TSV
    
    print(f"\nLoaded FOMO-60K: {len(fomo60k):,} sessions from {fomo60k_path}")
    print(f"Loaded FOMO-300K: {len(fomo300k):,} sessions from {fomo300k_path}")
    print(f"Loaded OpenMind: {len(openmind):,} sessions from {openmind_path}")
    
    # FOMO-60K: No preprocessing needed, just count as-is
    
    # FOMO-300K: Process OpenNeuro datasets
    openneuro_mask = fomo300k['dataset'].str.contains('PT030_OpenNeuro/', na=False)
    fomo300k.loc[openneuro_mask, 'participant_id'] = (
        fomo300k.loc[openneuro_mask, 'dataset'].str.extract(r'(ds\d+)')[0] + 
        '_' + fomo300k.loc[openneuro_mask, 'participant_id']
    )
    
    # Extract ds number from unique_id in OpenMind
    openmind['ds_number'] = openmind['unique_id'].str.extract(r'(ds\d+)')[0]
    openmind['participant_id'] = openmind['unique_id'].str.extract(r'(sub-[^_]+)')[0]
    openmind['dataset'] = 'PT030_OpenNeuro/' + openmind['ds_number']
    
    return fomo60k, fomo300k, openmind


def get_merged_groups(df, dataset_name="Dataset"):
    """Get merged group counts from a dataframe"""
    if 'group' not in df.columns or df['group'].isna().all():
        return pd.Series(dtype=int)
    
    group_data = df['group'].dropna()
    print(f"\n{dataset_name} - Total sessions: {len(group_data):,}")
    
    merged_groups, mapping = merge_groups(group_data)
    merged_counts = merged_groups.value_counts()
    
    return merged_counts

def match_openmind_with_fomo300k(openmind, fomo300k):
    """Match OpenMind ds numbers with FOMO300K PT030_OpenNeuro datasets"""
    # Get unique ds numbers from OpenMind
    openmind_ds = set(openmind['ds_number'].dropna().unique())
    
    # Get PT030_OpenNeuro datasets from FOMO300K and extract ds numbers
    fomo300k_openneuro = fomo300k[fomo300k['dataset'].str.contains('PT030_OpenNeuro/', na=False)].copy()
    # Extract ds number from format: PT030_OpenNeuro/ds006395
    fomo300k_openneuro['ds_number'] = fomo300k_openneuro['dataset'].str.extract(r'PT030_OpenNeuro/(ds\d+)')[0]
    fomo300k_ds = set(fomo300k_openneuro['ds_number'].dropna().unique())
    
    # Find overlap
    matched_ds = openmind_ds & fomo300k_ds
    only_openmind = openmind_ds - fomo300k_ds
    only_fomo300k = fomo300k_ds - openmind_ds
    
    print("\n" + "="*70)
    print("DATASET MATCHING SUMMARY")
    print("="*70)
    print(f"OpenMind unique datasets: {len(openmind_ds)}")
    print(f"FOMO-300K PT030_OpenNeuro datasets: {len(fomo300k_ds)}")
    print(f"Matched datasets: {len(matched_ds)}")
    print(f"Only in OpenMind: {len(only_openmind)}")
    print(f"Only in FOMO-300K: {len(only_fomo300k)}")
    
    if only_openmind:
        print(f"\nOpenMind-only datasets: {sorted(only_openmind)}")
    if only_fomo300k:
        print(f"\nFOMO-300K-only datasets: {sorted(only_fomo300k)}")
    
    return matched_ds, fomo300k_openneuro

def analyze_overlap(fomo60k_groups, fomo300k_groups, openmind_groups):
    """Analyze group overlap across datasets, grouping small categories as Others"""
    # Define the top groups to show
    top_group_names = [
        'Controls',
        'Brain Tumor', 
        'Stroke',
        'Mental Disorders',
        'Memory Complaints',
        'Dementia',
        'Neurological Disorders'
    ]
    
    all_groups = set(fomo60k_groups.index) | set(fomo300k_groups.index) | set(openmind_groups.index)
    
    # Calculate totals for percentage calculations
    total_60k = fomo60k_groups.sum()
    total_300k = fomo300k_groups.sum()
    total_openmind = openmind_groups.sum()
    
    # Separate top groups and others
    top_data = []
    others_60k = 0
    others_300k = 0
    others_openmind = 0
    
    for group in all_groups:
        count_60k = fomo60k_groups.get(group, 0)
        count_300k = fomo300k_groups.get(group, 0)
        count_openmind = openmind_groups.get(group, 0)
        
        if group in top_group_names:
            top_data.append({
                'Group': group,
                'FOMO-60K': count_60k,
                'FOMO-300K': count_300k,
                'OpenMind': count_openmind,
                '_sort': count_60k + count_300k + count_openmind
            })
        else:
            others_60k += count_60k
            others_300k += count_300k
            others_openmind += count_openmind
    
    # Create dataframe and sort
    df = pd.DataFrame(top_data)
    df = df.sort_values('_sort', ascending=False)
    
    # Add Others row
    others_row = {
        'Group': 'Others',
        'FOMO-60K': others_60k,
        'FOMO-300K': others_300k,
        'OpenMind': others_openmind,
        '_sort': others_60k + others_300k + others_openmind
    }
    
    result_df = pd.concat([df, pd.DataFrame([others_row])], ignore_index=True)
    
    # Add percentages
    result_df['FOMO-60K %'] = result_df['FOMO-60K'].apply(lambda x: f"{(x/total_60k*100):.1f}%" if x > 0 else "0.0%")
    result_df['FOMO-300K %'] = result_df['FOMO-300K'].apply(lambda x: f"{(x/total_300k*100):.1f}%" if x > 0 else "0.0%")
    result_df['OpenMind %'] = result_df['OpenMind'].apply(lambda x: f"{(x/total_openmind*100):.1f}%" if x > 0 else "0.0%")
    
    # Reorder columns and drop sort column
    result_df = result_df[['Group', 'FOMO-60K', 'FOMO-60K %', 'FOMO-300K', 'FOMO-300K %', 'OpenMind', 'OpenMind %']]
    
    return result_df

def main():
    parser = argparse.ArgumentParser(description='Analyze group overlap between FOMO and OpenMind datasets')
    parser.add_argument('--fomo60k', required=True, help='Path to FOMO-60K participants.tsv')
    parser.add_argument('--fomo300k', required=True, help='Path to FOMO-300K participants.tsv')
    parser.add_argument('--openmind', required=True, help='Path to OpenMind participants.csv')
    
    args = parser.parse_args()
    
    # Load datasets
    print("Loading datasets...")
    fomo60k, fomo300k, openmind = load_datasets(args.fomo60k, args.fomo300k, args.openmind)
    
    # Match OpenMind with FOMO-300K PT030_OpenNeuro
    matched_ds, fomo300k_openneuro = match_openmind_with_fomo300k(openmind, fomo300k)
    
    # Filter FOMO300K OpenNeuro to only matched datasets - this represents "OpenMind" data
    fomo300k_matched = fomo300k_openneuro[fomo300k_openneuro['ds_number'].isin(matched_ds)].copy()
    
    # Get merged groups
    print("\nProcessing groups...")
    fomo60k_groups = get_merged_groups(fomo60k, "FOMO-60K")
    fomo300k_groups = get_merged_groups(fomo300k, "FOMO-300K")  # Use ALL FOMO-300K
    openmind_groups = get_merged_groups(fomo300k_matched, "OpenMind")  # Use FOMO300K data for matched ds
    
    # Analyze overlap
    print("Analyzing overlap...")
    overlap_df = analyze_overlap(fomo60k_groups, fomo300k_groups, openmind_groups)
    
    # Summary statistics
    print("\n" + "="*70)
    print("GROUP OVERLAP SUMMARY")
    print("="*70)
    print(f"\nGroups in all 3 datasets: {len(overlap_df[(overlap_df['FOMO-60K'] > 0) & (overlap_df['FOMO-300K'] > 0) & (overlap_df['OpenMind'] > 0) & (overlap_df['Group'] != 'Others')])}")
    
    print(f"\nGroup distribution:")
    print(overlap_df.to_string(index=False))
   

if __name__ == "__main__":
    main()
