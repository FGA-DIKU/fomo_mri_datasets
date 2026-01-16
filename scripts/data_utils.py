import pandas as pd
import numpy as np
from pathlib import Path

# Color palette
COLORS = ['#2E86AB', '#A23B72', '#F18F01', '#C73E1D', '#6A4C93', '#1982C4', '#8AC926', '#FFD60A']

def ensure_figures_folder():
    """Create figures folder if it doesn't exist"""
    figures_dir = Path('figures')
    figures_dir.mkdir(exist_ok=True)
    return figures_dir

def load_data():
    """Load all required data files"""
    subjects_df = pd.read_csv('participants.tsv', sep='\t')
    mapping_df = pd.read_csv('mapping.tsv', sep='\t')
    mri_info_df = pd.read_csv('mri_info.tsv', sep='\t', low_memory=False)
    
    # Process OpenNeuro datasets - make subject IDs unique across subdatasets
    for df in [subjects_df, mapping_df]:
        openneuro_mask = df['dataset'].str.contains('PT030_OpenNeuro/', na=False)
        df.loc[openneuro_mask, 'participant_id'] = (
            df.loc[openneuro_mask, 'dataset'].str.extract(r'(ds\d+)')[0] + 
            '_' + df.loc[openneuro_mask, 'participant_id']
        )
        # Group all OpenNeuro datasets and remove PT prefix
        df['dataset'] = df['dataset'].str.replace(r'PT030_OpenNeuro/ds\d+', 'PT030_OpenNeuro', regex=True)
        df['dataset'] = df['dataset'].str.replace(r'^PT\d{3}_', '', regex=True)
    
    # Clean mapping filenames
    mapping_df['sequence'] = mapping_df['new_filename'].str.replace('.nii.gz', '').str.replace('.nii', '').str.replace('.pt', '')
    
    return subjects_df, mapping_df, mri_info_df

def process_age(age_str):
    """Convert age string to numeric, handling ranges and formats"""
    if pd.isna(age_str):
        return np.nan
    
    age_str = str(age_str).strip().rstrip('Yy')
    
    # Handle age ranges
    if '-' in age_str:
        try:
            parts = [float(p.strip().rstrip('Yy')) for p in age_str.split('-')]
            return sum(parts) / len(parts) if len(parts) == 2 else np.nan
        except ValueError:
            pass
    
    # Convert to numeric
    try:
        age_val = float(age_str)
        return age_val if age_val >= 0 else np.nan
    except ValueError:
        return np.nan

def get_baseline_subjects(subjects_df):
    """Get one record per subject (preferring ses-01 if available)"""
    baseline = subjects_df[subjects_df['session_id'] == 'ses-01'].drop_duplicates(subset=['dataset', 'participant_id'])
    if baseline.empty:
        baseline = subjects_df.groupby(['dataset', 'participant_id']).first().reset_index()
    return baseline

def clean_sequences(mapping_df):
    """Clean and standardize sequence names"""
    sequences = mapping_df['sequence'].copy()
    
    # Remove subject/session prefixes and clean up
    sequences = sequences.str.replace(r'sub-[^_]+_?', '', regex=True)
    sequences = sequences.str.replace(r'ses-[^_]+_?', '', regex=True)
    sequences = sequences.str.replace(r'run-[^_]+_?', '', regex=True)
    sequences = sequences.str.strip('_').str.replace('__', '_', regex=True).str.strip('_')
    
    # Remove trailing numbers and consolidate DWI variants
    sequences = sequences.str.replace(r'_\d+$', '', regex=True)
    sequences = sequences.str.replace(r'^dwi.*', 'dwi', regex=True, case=False)
    
    return sequences

def clean_mri_manufacturers(mri_info_df):
    """Clean and standardize MRI manufacturer names"""
    if 'Manufacturer' not in mri_info_df.columns:
        return mri_info_df
    
    # Create a copy to avoid modifying original
    cleaned_df = mri_info_df.copy()
    
    # Standardize manufacturer names
    manufacturer_mapping = {
        'siemens': 'Siemens',
        'siemens healthcare gmbh': 'Siemens', 
        'siemens healthineers': 'Siemens',
        'siemens : ': 'Siemens',
        'ge': 'GE',
        'ge medical systems': 'GE',
        'ge medical systems': 'GE',
        'general electrics': 'GE',
        'philips': 'Philips',
        'philips medical systems': 'Philips',
        'philips healthcare': 'Philips',
        'toshiba_mec': 'Toshiba',
        'toshiba': 'Toshiba',
        'canon_mec': 'Canon',
        'hitachi medical corporation': 'Hitachi',
        'hitachi': 'Hitachi',
        'brucker': 'Bruker',
        'ningbo xingaoyi': 'Ningbo Xingaoyi'
    }
    
    # Apply mapping (case insensitive)
    cleaned_df['Manufacturer'] = cleaned_df['Manufacturer'].str.lower().str.strip()
    cleaned_df['Manufacturer'] = cleaned_df['Manufacturer'].replace(manufacturer_mapping)
    
    return cleaned_df

def clean_field_strengths(mri_info_df):
    """Clean and standardize magnetic field strengths"""
    if 'MagneticFieldStrength' not in mri_info_df.columns:
        return mri_info_df
    
    # Create a copy to avoid modifying original
    cleaned_df = mri_info_df.copy()
    
    # Convert to numeric and clean
    field_strengths = pd.to_numeric(cleaned_df['MagneticFieldStrength'], errors='coerce')
    
    # Fix obviously wrong values
    # 15000.0 is likely 1.5 (missing decimal)
    field_strengths = field_strengths.replace(15000.0, 1.5)
    
    # Round very close values to standard field strengths
    # 1.494... → 1.5T
    field_strengths = field_strengths.apply(lambda x: 1.5 if pd.notna(x) and abs(x - 1.5) < 0.1 else x)
    # 2.89... → 3.0T  
    field_strengths = field_strengths.apply(lambda x: 3.0 if pd.notna(x) and abs(x - 3.0) < 0.2 else x)
    # 6.98 → 7.0T
    field_strengths = field_strengths.apply(lambda x: 7.0 if pd.notna(x) and abs(x - 7.0) < 0.1 else x)
    # 3.95... → 4.0T
    field_strengths = field_strengths.apply(lambda x: 4.0 if pd.notna(x) and abs(x - 4.0) < 0.1 else x)
    
    cleaned_df['MagneticFieldStrength'] = field_strengths
    
    return cleaned_df

def merge_groups(group_data):
    """Merge similar groups into broader categories with precise matching"""
    if group_data.empty:
        return group_data, {}
    
    # Enhanced category mappings - ORDER MATTERS for priority!
    category_keywords = {
        'Mental Disorders': ['adhd', 'attention deficit', 'hyperactivity', 'add', 'depression', 'depressive', 'mdd', 
                            'major depressive', 'depr', 'depressed', 'schizophrenia', 'schz', 'psychosis', 'psychotic',
                            'schizoaffective', 'bipolar', 'manic', 'mania', 'mood disorder', 'autism', 'autistic', 
                            'asd', 'asperger', 'pervasive developmental', 'psychiatric', 'cocaine', 'Psychiatric Illness'],
        'Brain Tumor': ['brain tumor', 'brain tumour', 'glioma', 'glioblastoma', 'meningioma', 'tumor', 'tumour', 'ependymom',
                        'cancer', 'neoplasm', 'metastases', 'metastasis', 'oncology', 'astrocytom', 'medulloblastoma', 'astrocytom',
                        'lymphoma', 'dnet', 'pituitary adenoma', 'adenoma', 'low-grade diffuse glioma', 'low-grade glioneuronal',
                        'anaplastic', 'metastatic'],
        'Stroke': ['stroke', 'cva', 'cerebrovascular accident', 'infarct', 'ischemic', 'ischaemic', 'ischemia', 'ischaemia',
                   'hemorrhage', 'haemorrhage', 'encephalomalacia', 'gliosis', 'hemorrhagy', 'gliotic foci'],
        'Dementia': ['dementia', 'alzheimer', 'ad', 'demented', 'cognitive impairment', 'mci', 'ftd', 'converted',
                     'mild cognitive', 'alzheimers', 'demenz', 'very_mild_dementia', 'mild_dementia', 'moderate_dementia'],
        'Neurological Disorders': ['multiple sclerosis', 'parkinson', 'epilepsy', 'seizure', 'refractory', 'intractable',
                                   'traumatic brain injury', 'tbi', 'head trauma', 'brain trauma', 'intracranial aneurysms',
                                   'meningitis', 'motor neuron disease', 'hydrocephalus', 'neurological'],
        'Memory Complaints': ['memory complaints'],
        'Controls': ['typically developing', 'normal', 'student', 'expert', 'control', 'neurotypical',
                    'nondemented', 'non-demented', 'hc', 'healthy', 'cn', 'ctrl', 'cont', 'nc',
                    'healthy control', 'typical', 'normal control', 'normalweight', 'health control'],
    }
    
    # Exact match patterns - these must match exactly (case insensitive)
    exact_matches = {
        'Mental Disorders': ['mdd', 'adhd', 'asd', 'add'],
        'Neurological Disorders': ['ms'],  # Only exact 'ms', not as substring
        'Dementia': ['ad', 'mci'],  # Only exact 'ad', not as substring
        'Controls': ['hc', 'cn', 'ctrl', 'cont', 'nc'],
    }
    
    # Define exclusions - groups that contain keywords but should NOT be mapped to certain categories
    exclusions = {
        'Controls': ['encephalocele', 'encephalomalasy', 'encephalopathy', 'dandy-walker', 'adhd', 'depression', 'bipolar',
                     'schizophrenia', 'autism', 'parkinson', 'substance user', 'tumor', 'tumour', 'glioma', 'adenoma',
                     'stroke', 'dementia', 'demented'],
        'Dementia': ['unpersuaded', 'persuaded', 'nondemented', 'adults', 'adolescents', 'adult', 'glioma', 'adenoma', 'tumor', 'tumour'],
        'Neurological Disorders': ['pd-nc', 'pd-mci'],  # These should go to Controls and Dementia respectively
        'Mental Disorders': ['nonpsychiatric', 'non-psychiatric']
    }
    
    # Special overrides - these take absolute priority
    special_overrides = {
        'pd-nc': 'Controls',
        'pd-mci': 'Dementia',
    }
    
    # Apply mappings
    merged_groups = group_data.copy()
    group_mapping = {}
    
    for original_group in merged_groups.unique():
        group_str = str(original_group).lower().strip()
        mapped = False
        
        # 1. Check special overrides first (highest priority)
        if group_str in special_overrides:
            group_mapping[original_group] = special_overrides[group_str]
            mapped = True
        
        if not mapped:
            # 2. Try exact matches (in priority order)
            for category in category_keywords.keys():
                if category in exact_matches:
                    if group_str in exact_matches[category]:
                        # Check exclusions
                        excluded = False
                        if category in exclusions:
                            excluded = any(exclusion.lower() in group_str for exclusion in exclusions[category])
                        
                        if not excluded:
                            group_mapping[original_group] = category
                            mapped = True
                            break
        
        if not mapped:
            # 3. Try keyword matches (in priority order)
            for category, keywords in category_keywords.items():
                # Check if any keyword matches
                keyword_matches = any(keyword.lower() in group_str for keyword in keywords)
                
                if keyword_matches:
                    # Check exclusions
                    excluded = False
                    if category in exclusions:
                        excluded = any(exclusion.lower() in group_str for exclusion in exclusions[category])
                    
                    if not excluded:
                        group_mapping[original_group] = category
                        mapped = True
                        break
        
        # 4. If still not mapped, normalize the original name
        if not mapped:
            normalized_name = ' '.join(word.capitalize() for word in group_str.split())
            group_mapping[original_group] = normalized_name

    return merged_groups.map(group_mapping), group_mapping
