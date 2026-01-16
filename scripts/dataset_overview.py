import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from scipy import stats
from pathlib import Path
import argparse
from data_utils import (COLORS, ensure_figures_folder, process_age, 
                        get_baseline_subjects, clean_sequences, merge_groups,
                        clean_mri_manufacturers, clean_field_strengths, load_data)
from matplotlib.patches import Patch

sns.set_style("whitegrid", {'grid.linestyle': '--', 'grid.alpha': 0.3})
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.size'] = 16  # Base font size
plt.rcParams['axes.labelsize'] = 14  # Axis labels
plt.rcParams['axes.titlesize'] = 16  # Subplot titles
PANEL_SIZE=22


def plot_unified_overview(subjects_df, mapping_df, mri_info_df, slice_thickness_dir='.', output_folder='.'):
    """Create a comprehensive unified visualization with all key information
    
    Args:
        subjects_df: DataFrame with subject information
        mapping_df: DataFrame with mapping information
        mri_info_df: DataFrame with MRI information
        slice_thickness_dir: Path to folder containing slice thickness CSV files (default: current directory)
        output_folder: Path to folder where figures will be saved (default: current directory)
    """
    slice_thickness_path = Path(slice_thickness_dir)
    output_path = Path(output_folder)
    figures_dir = output_path / 'figures'
    figures_dir.mkdir(parents=True, exist_ok=True)
    
    # Prepare data
    baseline = get_baseline_subjects(subjects_df)
    baseline['age_numeric'] = baseline['age'].apply(process_age)
    all_sessions = subjects_df.copy()
    all_sessions['age_numeric'] = all_sessions['age'].apply(process_age)
    cleaned_mri_df = clean_mri_manufacturers(mri_info_df)
    cleaned_mri_df = clean_field_strengths(cleaned_mri_df)
    sequences_clean = clean_sequences(mapping_df)
    
    # Create figure with custom gridspec for the specified layout
    fig = plt.figure(figsize=(30, 22))
    gs = fig.add_gridspec(3, 12, hspace=0.2, wspace=5.5, 
                          left=0.08, right=0.96, top=0.98, bottom=0.04)
    
    # ============================================================
    # FIRST LINE: Age (40%), Merged Groups (40%), Sex+Handedness stacked (20%)
    # ============================================================
    
    # 1. Age Distribution (40% = 4.8 columns)
    ax_age = fig.add_subplot(gs[0, 0:5])
    pos = ax_age.get_position()

    # Add panel label
    ax_age.text(-0.08, 1.05, 'A', transform=ax_age.transAxes, 
               fontsize=PANEL_SIZE, fontweight='bold', va='top', ha='right')

    age_data = all_sessions['age_numeric'].dropna()

    if not age_data.empty:
        # Histogram with counts (not density)
        ax_age.hist(age_data, bins=25, alpha=0.6, color=COLORS[0], edgecolor='black', 
                   linewidth=0.5, density=False, label='Histogram')
    
        # Create twin axis for KDE
        ax_age2 = ax_age.twinx()
    
        # KDE on the twin axis
        kde = stats.gaussian_kde(age_data)
        x_range = np.linspace(age_data.min(), age_data.max(), 200)
        ax_age2.plot(x_range, kde(x_range), linewidth=2.5, color=COLORS[1], label='KDE')
    
        # Format y-axis to show only 2 decimal places
        from matplotlib.ticker import FormatStrFormatter
        ax_age2.yaxis.set_major_formatter(FormatStrFormatter('%.3f'))
    
        # Mean line on primary axis
        ax_age.axvline(age_data.mean(), color=COLORS[2], linestyle='--', linewidth=2,
                      label=f'Mean: {age_data.mean():.1f}y')
    
        # Combine legends from both axes
        lines1, labels1 = ax_age.get_legend_handles_labels()
        lines2, labels2 = ax_age2.get_legend_handles_labels()
        ax_age.legend(lines1 + lines2, labels1 + labels2, fontsize=16, frameon=True, loc='upper right')


    ax_age.set_title(f'Age Distribution (n={len(age_data):,})', fontsize=20, fontweight='bold')
    ax_age.set_xlabel('Age (years)', fontsize=16, fontweight='bold')
    ax_age.set_ylabel('Sessions', fontsize=16, fontweight='bold')  
    ax_age2.set_ylabel('Density', fontsize=16, fontweight='bold')  
    ax_age.set_ylim(bottom=0)
    ax_age2.set_ylim(bottom=0)
    ax_age.spines['top'].set_visible(False)
    ax_age.spines['right'].set_visible(False)
    ax_age2.spines['top'].set_visible(False)
    ax_age2.set_position([pos.x0, pos.y0, pos.width * 0.85, pos.height]) 
   
    # 2. Merged Groups (40% = 4.8 columns)
    ax_groups = fig.add_subplot(gs[0, 5:10])
    
    # Add panel label - 
    ax_groups.text(-0.08, 1.05, 'B', transform=ax_groups.transAxes, 
                  fontsize=PANEL_SIZE, fontweight='bold', va='top', ha='right')
    
    if 'group' in all_sessions.columns and not all_sessions['group'].isna().all():
        group_data = all_sessions['group'].dropna()
        merged_groups, _ = merge_groups(group_data)
        group_counts = merged_groups.value_counts()
        total_sessions = len(merged_groups)  
        threshold = 0.01 * total_sessions
        
        major_groups = group_counts[group_counts >= threshold]
        minor_groups = group_counts[group_counts < threshold]
        
        if len(minor_groups) > 0:
            final_counts = major_groups.copy()
            final_counts['Others'] = minor_groups.sum()
        else:
            final_counts = major_groups
        
        # Take top 8 for space
        plot_counts = final_counts.head(8)
        
        bars = ax_groups.barh(range(len(plot_counts)), plot_counts.values,
                             color=COLORS[:len(plot_counts)], alpha=0.6,
                             edgecolor='black', linewidth=0.5)
        ax_groups.set_yticks(range(len(plot_counts)))
        ax_groups.set_yticklabels([name[:25] + '...' if len(name) > 25 else name 
                                   for name in plot_counts.index], fontsize=16)
        ax_groups.set_title(f'Subject Groups (n={total_sessions:,})',
                           fontsize=20, fontweight='bold')
        ax_groups.set_xlabel('Sessions', fontsize=16, fontweight='bold')
        ax_groups.invert_yaxis()
        ax_groups.spines['top'].set_visible(False)
        ax_groups.spines['right'].set_visible(False)
        
        for bar in bars:
            width = bar.get_width()
            percentage = (width / total_sessions) * 100
            ax_groups.text(width + max(plot_counts.values)*0.01, 
                          bar.get_y() + bar.get_height()/2,
                          f'{int(width):,}\n({percentage:.0f}%)', 
                          ha='left', va='center', fontweight='bold', fontsize=16)
    
    # Create nested gridspec for Sex and Handedness stacking (20% = 2.4 columns)
    gs_demo = gs[0, 10:12].subgridspec(2, 1, hspace=0.4)
    
    # 3a. Sex (top of stack)
    ax_sex = fig.add_subplot(gs_demo[0])
    
    # Add panel label - 
    ax_sex.text(-0.30, 1.12, 'C', transform=ax_sex.transAxes, 
               fontsize=PANEL_SIZE, fontweight='bold', va='top', ha='right')
    
    sex_data = all_sessions['sex'].dropna()
    
    if not sex_data.empty:
        sex_counts = sex_data.value_counts()
        total_sex = len(sex_data)
        
        bars = ax_sex.barh(range(len(sex_counts)), sex_counts.values,
                          color=COLORS[:len(sex_counts)], alpha=0.6,
                          edgecolor='black', linewidth=0.5)
        ax_sex.set_yticks(range(len(sex_counts)))
        ax_sex.set_yticklabels(sex_counts.index, fontsize=16)
        ax_sex.set_title(f'Sex (n={len(sex_data):,})', fontsize=20, fontweight='bold')
        ax_sex.set_xlabel('Sessions', fontsize=16, fontweight='bold')
        ax_sex.invert_yaxis()
        ax_sex.spines['top'].set_visible(False)
        ax_sex.spines['right'].set_visible(False)
        
        for bar in bars:
            width = bar.get_width()
            percentage = (width / total_sex) * 100
            ax_sex.text(width + max(sex_counts.values)*0.01, 
                       bar.get_y() + bar.get_height()/2,
                       f'{int(width):,}\n({percentage:.0f}%)', 
                       ha='left', va='center', fontweight='bold', fontsize=16)
    
    # 3b. Handedness (bottom of stack)
    ax_hand = fig.add_subplot(gs_demo[1])
    
    # Add panel label - 
    ax_hand.text(-0.30, 1.12, 'D', transform=ax_hand.transAxes, 
                fontsize=PANEL_SIZE, fontweight='bold', va='top', ha='right')
    
    hand_data = all_sessions['handedness'].dropna()
    
    if not hand_data.empty:
        hand_counts = hand_data.value_counts()
        total_hand = len(hand_data)
        
        bars = ax_hand.barh(range(len(hand_counts)), hand_counts.values,
                           color=COLORS[:len(hand_counts)], alpha=0.6,
                           edgecolor='black', linewidth=0.5)
        ax_hand.set_yticks(range(len(hand_counts)))
        ax_hand.set_yticklabels(hand_counts.index, fontsize=16)
        ax_hand.set_title(f'Handedness (n={len(hand_data):,})', fontsize=20, fontweight='bold')
        ax_hand.set_xlabel('Sessions', fontsize=16, fontweight='bold')
        ax_hand.invert_yaxis()
        ax_hand.spines['top'].set_visible(False)
        ax_hand.spines['right'].set_visible(False)
        
        for bar in bars:
            width = bar.get_width()
            percentage = (width / total_hand) * 100
            ax_hand.text(width + max(hand_counts.values)*0.01,
                        bar.get_y() + bar.get_height()/2,
                        f'{int(width):,}\n({percentage:.0f}%)',
                        ha='left', va='center', fontweight='bold', fontsize=16)
    
    # ============================================================
    # SECOND LINE: Vendor+Acquisition stacked (20%), Scanner (30%), Tesla (20%), Thickness (30%)
    # ============================================================
    
    # Create a nested gridspec for Vendor and Acquisition stacking (20% = 2.4 columns)
    gs_vendor_acq = gs[1, 0:3].subgridspec(2, 1, hspace=0.4)
    
    # 1a. MRI Vendor (top of stack)
    ax_vendor = fig.add_subplot(gs_vendor_acq[0])
    
    # Add panel label - 
    ax_vendor.text(-0.12, 1.12, 'E', transform=ax_vendor.transAxes, 
                  fontsize=PANEL_SIZE, fontweight='bold', va='top', ha='right')
    
    if 'Manufacturer' in cleaned_mri_df.columns:
        manufacturer_counts = cleaned_mri_df['Manufacturer'].value_counts()
        # Calculate total based on scans with non-null manufacturer data
        total_scans_with_mfg = manufacturer_counts.sum()
        threshold = 0.005 * total_scans_with_mfg
        major_mfgs = manufacturer_counts[manufacturer_counts >= threshold]
        minor_mfgs = manufacturer_counts[manufacturer_counts < threshold]
        
        if len(minor_mfgs) > 0:
            final_mfg_counts = major_mfgs.copy()
            final_mfg_counts['Others'] = minor_mfgs.sum()
        else:
            final_mfg_counts = major_mfgs
        
        bars = ax_vendor.barh(range(len(final_mfg_counts)), final_mfg_counts.values,
                             color=COLORS[:len(final_mfg_counts)], alpha=0.6,
                             edgecolor='black', linewidth=0.5)
        ax_vendor.set_yticks(range(len(final_mfg_counts)))
        ax_vendor.set_yticklabels(final_mfg_counts.index, fontsize=16)
        ax_vendor.set_title(f'Manufacturers (n={total_scans_with_mfg:,})', 
                           fontsize=20, fontweight='bold')
        ax_vendor.set_xlabel('Scans', fontsize=16, fontweight='bold')
        ax_vendor.invert_yaxis()
        ax_vendor.spines['top'].set_visible(False)
        ax_vendor.spines['right'].set_visible(False)
        
        for bar in bars:
            width = bar.get_width()
            percentage = (width / total_scans_with_mfg) * 100
            ax_vendor.text(width + max(final_mfg_counts.values)*0.01,
                          bar.get_y() + bar.get_height()/2,
                          f'{int(width):,}\n({percentage:.0f}%)',
                          ha='left', va='center', fontweight='bold', fontsize=16)
    
    # 1b. Acquisition Type (bottom of stack)
    ax_acq = fig.add_subplot(gs_vendor_acq[1])
    
    # Add panel label - 
    ax_acq.text(-0.12, 1.12, 'F', transform=ax_acq.transAxes, 
               fontsize=PANEL_SIZE, fontweight='bold', va='top', ha='right')
    
    if 'MRAcquisitionType' in cleaned_mri_df.columns:
        acq_types = cleaned_mri_df['MRAcquisitionType'].str.upper()
        acq_counts = acq_types.value_counts()
        total_acq_scans = acq_counts.sum()
        
        bars = ax_acq.barh(range(len(acq_counts)), acq_counts.values,
                          color=COLORS[:len(acq_counts)], alpha=0.6,
                          edgecolor='black', linewidth=0.5)
        ax_acq.xaxis.set_major_locator(plt.MaxNLocator(nbins=6, integer=True))
        ax_acq.set_yticks(range(len(acq_counts)))
        ax_acq.set_yticklabels(acq_counts.index, fontsize=16)
        ax_acq.set_title(f'Acquisition Type (n={total_acq_scans:,})', 
                        fontsize=20, fontweight='bold')
        ax_acq.set_xlabel('Scans', fontsize=16, fontweight='bold')
        ax_acq.invert_yaxis()
        ax_acq.spines['top'].set_visible(False)
        ax_acq.spines['right'].set_visible(False)
        
        for bar in bars:
            width = bar.get_width()
            percentage = (width / total_acq_scans) * 100
            ax_acq.text(width + max(acq_counts.values)*0.01,
                       bar.get_y() + bar.get_height()/2,
                       f'{int(width):,}\n({percentage:.0f}%)',
                       ha='left', va='center', fontweight='bold', fontsize=16)
    
    # 2. Field Strength (30% = 3.6 columns) - LARGER, extends to end of row
    ax_tesla = fig.add_subplot(gs[1, 3:7])
    
    # Add panel label - 
    ax_tesla.text(-0.08, 1.10, 'G', transform=ax_tesla.transAxes, 
                 fontsize=PANEL_SIZE, fontweight='bold', va='top', ha='right')
    
    if 'MagneticFieldStrength' in cleaned_mri_df.columns:
        field_strength = cleaned_mri_df['MagneticFieldStrength'].dropna()
        if not field_strength.empty:
            field_counts = field_strength.value_counts().sort_index()
            field_counts = field_counts[field_counts >= 5]  # At least 5 scans
            
            bars = ax_tesla.bar(range(len(field_counts)), field_counts.values,
                               color=COLORS[2], alpha=0.6,
                               edgecolor='black', linewidth=0.5)
            ax_tesla.set_xticks(range(len(field_counts)))
            ax_tesla.set_xticklabels([f'{x}T' for x in field_counts.index], 
                                    fontsize=16, rotation=45)
            ax_tesla.set_title(f'Field Strength (n={len(field_strength):,})', fontsize=20, fontweight='bold', pad=30)
            ax_tesla.set_xlabel('Tesla', fontsize=16, fontweight='bold')
            ax_tesla.set_ylabel('Scans', fontsize=16, fontweight='bold')
            ax_tesla.spines['top'].set_visible(False)
            ax_tesla.spines['right'].set_visible(False)
            
            for bar in bars:
                height = bar.get_height()
                percentage = (height / len(field_strength)) * 100
                ax_tesla.text(bar.get_x() + bar.get_width()/2., 
                             height + max(field_counts.values)*0.01,
                             f'{int(height):,}\n({percentage:.0f}%)',
                             ha='center', va='bottom', fontweight='bold', fontsize=16)
    
    # 3. Scanner Models (30% = 3.6 columns, TOP 15)
    ax_scanner = fig.add_subplot(gs[1, 7:12])
    
    # Add panel label - 
    ax_scanner.text(-0.08, 1.05, 'H', transform=ax_scanner.transAxes, 
                   fontsize=PANEL_SIZE, fontweight='bold', va='top', ha='right')
    
    if 'ManufacturersModelName' in cleaned_mri_df.columns and 'Manufacturer' in cleaned_mri_df.columns:
        model_counts = cleaned_mri_df['ManufacturersModelName'].value_counts().head(15)
        
        # Create manufacturer color mapping
        manufacturer_color_map = {}
        for i, manufacturer in enumerate(final_mfg_counts.index):
            manufacturer_color_map[manufacturer] = COLORS[i % len(COLORS)]
        
        model_colors = []
        for model in model_counts.index:
            model_manufacturer = cleaned_mri_df[cleaned_mri_df['ManufacturersModelName'] == model]['Manufacturer'].iloc[0]
            model_colors.append(manufacturer_color_map.get(model_manufacturer, COLORS[0]))
        
        bars = ax_scanner.barh(range(len(model_counts)), model_counts.values,
                              color=model_colors, alpha=0.6,
                              edgecolor='black', linewidth=0.5)
        ax_scanner.set_yticks(range(len(model_counts)))
        ax_scanner.set_yticklabels([name[:22] + '...' if len(name) > 22 else name 
                                   for name in model_counts.index], fontsize=16)
        ax_scanner.set_title('Top 15 Scanner Models', fontsize=20, fontweight='bold')
        ax_scanner.set_xlabel('Scans', fontsize=16, fontweight='bold')
        ax_scanner.invert_yaxis()
        ax_scanner.spines['top'].set_visible(False)
        ax_scanner.spines['right'].set_visible(False)
        
        # Add manufacturer legend - only for manufacturers present in plotted models
        from matplotlib.patches import Patch
        plotted_manufacturers = []
        for model in model_counts.index:
            mfg = cleaned_mri_df[cleaned_mri_df['ManufacturersModelName'] == model]['Manufacturer'].iloc[0]
            if mfg not in plotted_manufacturers:
                plotted_manufacturers.append(mfg)
        
        legend_elements = [Patch(facecolor=manufacturer_color_map[mfg], 
                                edgecolor='black', alpha=0.6, label=mfg)
                          for mfg in plotted_manufacturers]
        ax_scanner.legend(handles=legend_elements, loc='lower right', 
                         fontsize=16, frameon=True, title='Manufacturer')
        
        for bar in bars:
            width = bar.get_width()
            percentage = (width / total_scans_with_mfg) * 100  
            ax_scanner.text(width + max(model_counts.values)*0.01,
                           bar.get_y() + bar.get_height()/2,
                           f'{int(width):,}({percentage:.0f}%)',
                           ha='left', va='center', fontweight='bold', fontsize=16)
    
    # ============================================================
    # THIRD LINE: Slice Thickness (50%), Sequences (50%)
    # ============================================================
    
    # 1. Slice Thickness (50% = 6 columns)
    ax_slice = fig.add_subplot(gs[2, 0:6])
    
    # Add panel label - 
    ax_slice.text(-0.08, 1.05, 'I', transform=ax_slice.transAxes, 
                 fontsize=PANEL_SIZE, fontweight='bold', va='top', ha='right')
    
    # Load slice thickness data from specified directory
    fomo300k_path = slice_thickness_path / 'FOMO300K_slice_thickness.csv'
    fomo60k_path = slice_thickness_path / 'FOMO60K_slice_thickness.csv'
    openmind_path = slice_thickness_path / 'OpenMind_slice_thickness.csv'
    
    # Check if files exist before loading
    if not fomo300k_path.exists():
        print(f"Warning: {fomo300k_path} not found, skipping slice thickness plot")
    elif not fomo60k_path.exists():
        print(f"Warning: {fomo60k_path} not found, skipping slice thickness plot")
    elif not openmind_path.exists():
        print(f"Warning: {openmind_path} not found, skipping slice thickness plot")
    else:
        fomo300k = pd.read_csv(fomo300k_path)
        fomo60k = pd.read_csv(fomo60k_path)
        openmind = pd.read_csv(openmind_path)
        
        # Bin values > 7mm into 7
        fomo300k['thickness_binned'] = fomo300k['slice_thickness'].apply(lambda x: 7 if x > 7 else x)
        fomo60k['thickness_binned'] = fomo60k['slice_thickness'].apply(lambda x: 7 if x > 7 else x)
        openmind['thickness_binned'] = openmind['slice_thickness'].apply(lambda x: 7 if x > 7 else x)
        
        slice_colors = ['#2E86AB', '#A23B72', '#F18F01']
        bin_edges = [0, 0.5, 1.5, 2.5, 3.5, 4.5, 5.5, 6.5, 100]
        
        fomo300k_counts, _ = np.histogram(fomo300k['thickness_binned'], bins=bin_edges)
        fomo60k_counts, _ = np.histogram(fomo60k['thickness_binned'], bins=bin_edges)
        openmind_counts, _ = np.histogram(openmind['thickness_binned'], bins=bin_edges)
        
        bin_centers = [(bin_edges[i] + bin_edges[i+1])/2 for i in range(len(bin_edges)-1)]
        bin_centers[-1] = 7.0
        
        width = 0.25
        ax_slice.bar(np.array(bin_centers) - width, fomo300k_counts, width, 
                     label='FOMO-300K', color=slice_colors[0], alpha=0.6, 
                     edgecolor='black', linewidth=0.5)
        ax_slice.bar(bin_centers, fomo60k_counts, width, 
                     label='FOMO-60K', color=slice_colors[1], alpha=0.6, 
                     edgecolor='black', linewidth=0.5)
        ax_slice.bar(np.array(bin_centers) + width, openmind_counts, width, 
                     label='OpenMind', color=slice_colors[2], alpha=0.6, 
                     edgecolor='black', linewidth=0.5)
        
        # KDE overlay
        ax_slice2 = ax_slice.twinx()
        x_range = np.linspace(0, 7.5, 500)
        
        kde_fomo300k = stats.gaussian_kde(fomo300k['thickness_binned'])
        kde_fomo60k = stats.gaussian_kde(fomo60k['thickness_binned'])
        kde_openmind = stats.gaussian_kde(openmind['thickness_binned'])
        
        ax_slice2.plot(x_range, kde_fomo300k(x_range), linewidth=2.5, color=slice_colors[0])
        ax_slice2.plot(x_range, kde_fomo60k(x_range), linewidth=2.5, color=slice_colors[1])
        ax_slice2.plot(x_range, kde_openmind(x_range), linewidth=2.5, color=slice_colors[2])
        
        bin_labels = ['<0.5', '0.5-1.5', '1.5-2.5', '2.5-3.5', '3.5-4.5', '4.5-5.5', '5.5-6.5', '≥6.5']
        ax_slice.set_xticks(bin_centers)
        ax_slice.set_xticklabels(bin_labels, fontsize=16)
        ax_slice.set_xlabel('Slice Thickness (mm)', fontsize=16, fontweight='bold')
        ax_slice.set_ylabel('Scans', fontsize=16, fontweight='bold')
        ax_slice2.set_ylabel('Density', fontsize=16, fontweight='bold')
        ax_slice.set_ylim(bottom=0)
        ax_slice2.set_ylim(bottom=0)
        ax_slice.set_xlim(-0.5, 7.5)
        ax_slice.legend(fontsize=16, frameon=True, loc='upper right', title='Dataset')
        ax_slice.set_title('Slice Thickness Distribution', fontsize=20, fontweight='bold')
        ax_slice.spines['top'].set_visible(False)
        ax_slice2.spines['top'].set_visible(False)
        
    # 2. Top Sequences (50% = 6 columns)
    ax_seq = fig.add_subplot(gs[2, 6:12])
    
    # Add panel label - 
    ax_seq.text(-0.08, 1.05, 'J', transform=ax_seq.transAxes, 
               fontsize=PANEL_SIZE, fontweight='bold', va='top', ha='right')
    
    sequence_counts = sequences_clean.value_counts().head(15)
    modality_counts = mapping_df['modality'].value_counts()
    
    # Create modality color mapping
    modality_color_map = {}
    for i, modality in enumerate(modality_counts.index):
        modality_color_map[modality] = COLORS[i % len(COLORS)]
    
    sequence_colors = []
    for seq in sequence_counts.index:
        seq_modalities = mapping_df[clean_sequences(mapping_df) == seq]['modality'].value_counts()
        if not seq_modalities.empty:
            primary_modality = seq_modalities.index[0]
            sequence_colors.append(modality_color_map.get(primary_modality, COLORS[0]))
        else:
            sequence_colors.append(COLORS[0])
    
    bars = ax_seq.barh(range(len(sequence_counts)), sequence_counts.values,
                       color=sequence_colors, alpha=0.6,
                       edgecolor='black', linewidth=0.5)
    ax_seq.set_yticks(range(len(sequence_counts)))
    ax_seq.set_yticklabels([seq[:22] + '...' if len(seq) > 22 else seq 
                           for seq in sequence_counts.index], fontsize=16)
    ax_seq.set_title('Top 15 Sequences', fontsize=20, fontweight='bold')
    ax_seq.set_xlabel('Scans', fontsize=16, fontweight='bold')
    ax_seq.invert_yaxis()
    ax_seq.spines['top'].set_visible(False)
    ax_seq.spines['right'].set_visible(False)
    
    # Add modality legend - only for modalities present in plotted sequences
    plotted_modalities = []
    for seq in sequence_counts.index:
        seq_modalities = mapping_df[clean_sequences(mapping_df) == seq]['modality'].value_counts()
        if not seq_modalities.empty:
            primary_modality = seq_modalities.index[0]
            if primary_modality not in plotted_modalities:
                plotted_modalities.append(primary_modality)
    
    legend_elements = [Patch(facecolor=modality_color_map[mod], 
                            edgecolor='black', alpha=0.6, label=mod)
                      for mod in plotted_modalities]
    ax_seq.legend(handles=legend_elements, loc='lower right', 
                 fontsize=16, frameon=True, title='Modality')
    
    max_count = max(sequence_counts.values)
    total_seq_scans = len(sequences_clean)
    for i, (seq, count) in enumerate(sequence_counts.items()):
        percentage = (count / total_seq_scans) * 100
        ax_seq.text(count + max_count * 0.01, i, 
                   f'{count:,} ({percentage:.0f}%)',
                   va='center', ha='left', fontsize=16, fontweight='bold')
    
    plt.savefig(figures_dir / 'dataset_overview.png', 
                dpi=400, bbox_inches='tight', facecolor='white', edgecolor='none')
    plt.show()
    
    print("\n" + "=" * 70)
    print("UNIFIED OVERVIEW VISUALIZATION CREATED")
    print("=" * 70)
    print(f"Saved to: {figures_dir / 'dataset_overview.png'}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Create unified overview visualization from dataset files'
    )
    parser.add_argument(
        '-s', '--slice-thickness-dir',
        default='.',
        help='Directory containing slice thickness CSV files (default: current directory)'
    )
    parser.add_argument(
        '-o', '--output',
        default='.',
        help='Output folder for figures (default: current directory)'
    )
    
    args = parser.parse_args()
    
    # Load data using the existing load_data function
    from data_utils import load_data
    subjects_df, mapping_df, mri_info_df = load_data()
    
    # Create unified plot
    plot_unified_overview(subjects_df, mapping_df, mri_info_df, args.slice_thickness_dir, args.output)
