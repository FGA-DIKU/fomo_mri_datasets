import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from scipy import stats
from data_utils import (COLORS, ensure_figures_folder, process_age, 
                        get_baseline_subjects, clean_sequences, merge_groups,
                        clean_mri_manufacturers, clean_field_strengths)


sns.set_style("whitegrid", {'grid.linestyle': '--', 'grid.alpha': 0.3})
plt.rcParams['font.family'] = 'sans-serif'

def plot_demographics(subjects_df):
    """Plot demographic distributions"""
    figures_dir = ensure_figures_folder()
    baseline = get_baseline_subjects(subjects_df)
    
    fig, axes = plt.subplots(2, 2, figsize=(18, 12))
    
    # Age distribution
    baseline['age_numeric'] = baseline['age'].apply(process_age)
    age_data = baseline['age_numeric'].dropna()
    
    if not age_data.empty:
        # KDE plot with histogram
        axes[0,0].hist(age_data, bins=25, alpha=0.6, color=COLORS[0], edgecolor='black', 
                      linewidth=0.5, density=True, label='Distribution')
        
        # Add KDE overlay
        kde = stats.gaussian_kde(age_data)
        x_range = np.linspace(age_data.min(), age_data.max(), 200)
        axes[0,0].plot(x_range, kde(x_range), linewidth=2.5, color=COLORS[1], label='KDE')
        
        axes[0,0].axvline(age_data.mean(), color=COLORS[2], linestyle='--', linewidth=2,
                         label=f'Mean: {age_data.mean():.1f} years')
        axes[0,0].legend(fontsize=11, frameon=True, fancybox=True, shadow=True)
    
    axes[0,0].set_title(f'Age Distribution (n={len(age_data)} subjects)', 
                       fontsize=14, fontweight='bold', pad=15)
    axes[0,0].set_xlabel('Age (years)', fontsize=12, fontweight='bold')
    axes[0,0].set_ylabel('Density', fontsize=12, fontweight='bold')
    axes[0,0].spines['top'].set_visible(False)
    axes[0,0].spines['right'].set_visible(False)
    axes[0,0].spines['left'].set_linewidth(1.2)
    axes[0,0].spines['bottom'].set_linewidth(1.2)
    
    # Sex distribution - horizontal bar chart
    sex_data = baseline['sex'].dropna()
    if not sex_data.empty:
        sex_counts = sex_data.value_counts()
        total_sex = len(sex_data)
        
        bars = axes[0,1].barh(range(len(sex_counts)), sex_counts.values,
                             color=COLORS[:len(sex_counts)], alpha=0.8,
                             edgecolor='black', linewidth=0.5)
        axes[0,1].set_yticks(range(len(sex_counts)))
        axes[0,1].set_yticklabels(sex_counts.index, fontsize=12)
        axes[0,1].set_title(f'Sex Distribution (n={len(sex_data)} subjects)', 
                           fontsize=14, fontweight='bold', pad=15)
        axes[0,1].set_xlabel('Number of Subjects', fontsize=12, fontweight='bold')
        axes[0,1].invert_yaxis()
        axes[0,1].spines['top'].set_visible(False)
        axes[0,1].spines['right'].set_visible(False)
        axes[0,1].spines['left'].set_linewidth(1.2)
        axes[0,1].spines['bottom'].set_linewidth(1.2)
        
        # Add value labels with percentages
        for i, bar in enumerate(bars):
            width = bar.get_width()
            percentage = (width / total_sex) * 100
            axes[0,1].text(width + max(sex_counts.values)*0.01, bar.get_y() + bar.get_height()/2,
                          f'{int(width):,} ({percentage:.1f}%)', ha='left', va='center', 
                          fontweight='bold', fontsize=11)
    
    # Handedness distribution - horizontal bar chart
    hand_data = baseline['handedness'].dropna()
    if not hand_data.empty:
        hand_counts = hand_data.value_counts()
        total_hand = len(hand_data)
        
        bars = axes[1,0].barh(range(len(hand_counts)), hand_counts.values,
                             color=COLORS[:len(hand_counts)], alpha=0.8,
                             edgecolor='black', linewidth=0.5)
        axes[1,0].set_yticks(range(len(hand_counts)))
        axes[1,0].set_yticklabels(hand_counts.index, fontsize=12)
        axes[1,0].set_title(f'Handedness Distribution (n={len(hand_data)} subjects)', 
                           fontsize=14, fontweight='bold', pad=15)
        axes[1,0].set_xlabel('Number of Subjects', fontsize=12, fontweight='bold')
        axes[1,0].invert_yaxis()
        axes[1,0].spines['top'].set_visible(False)
        axes[1,0].spines['right'].set_visible(False)
        axes[1,0].spines['left'].set_linewidth(1.2)
        axes[1,0].spines['bottom'].set_linewidth(1.2)
        
        # Add value labels with percentages
        for i, bar in enumerate(bars):
            width = bar.get_width()
            percentage = (width / total_hand) * 100
            axes[1,0].text(width + max(hand_counts.values)*0.01, bar.get_y() + bar.get_height()/2,
                          f'{int(width):,} ({percentage:.1f}%)', ha='left', va='center', 
                          fontweight='bold', fontsize=11)
    
    # Sessions per subject
    sessions_per_subject = subjects_df.groupby(['dataset', 'participant_id']).size()
    sessions_plot = sessions_per_subject.copy()
    sessions_plot.loc[sessions_plot >= 6] = 6
    
    bin_counts = sessions_plot.value_counts().sort_index()
    x_labels = [str(int(x)) if x < 6 else '6+' for x in bin_counts.index]
    x_positions = range(len(bin_counts))
    
    bars = axes[1,1].bar(x_positions, bin_counts.values, color=COLORS[0], alpha=0.8,
                        edgecolor='black', linewidth=0.5)
    axes[1,1].set_xticks(x_positions)
    axes[1,1].set_xticklabels(x_labels, fontsize=11)
    axes[1,1].set_title(f'Sessions per Subject (n={len(sessions_per_subject)} subjects)', 
                       fontsize=14, fontweight='bold', pad=15)
    axes[1,1].set_xlabel('Number of Sessions', fontsize=12, fontweight='bold')
    axes[1,1].set_ylabel('Number of Subjects', fontsize=12, fontweight='bold')
    axes[1,1].spines['top'].set_visible(False)
    axes[1,1].spines['right'].set_visible(False)
    axes[1,1].spines['left'].set_linewidth(1.2)
    axes[1,1].spines['bottom'].set_linewidth(1.2)
    
    # Add value labels on bars with percentages
    total_subjects_sessions = len(sessions_per_subject)
    for bar in bars:
        height = bar.get_height()
        percentage = (height / total_subjects_sessions) * 100
        axes[1,1].text(bar.get_x() + bar.get_width()/2., height + max(bin_counts.values)*0.01,
                      f'{int(height):,}\n({percentage:.1f}%)', ha='center', va='bottom', 
                      fontweight='bold', fontsize=10)
    
    plt.tight_layout()
    plt.subplots_adjust(top=0.92, hspace=0.3, wspace=0.3)
    plt.savefig(figures_dir / 'demographic_distributions.png', dpi=300, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    plt.show()

def plot_group_distribution(subjects_df):
    """Plot merged group distribution"""
    figures_dir = ensure_figures_folder()
    baseline = get_baseline_subjects(subjects_df)
    
    if 'group' not in baseline.columns or baseline['group'].isna().all():
        print("No group data available for plotting")
        return
    
    group_data = baseline['group'].dropna()
    original_group_counts = group_data.value_counts()
    merged_groups, group_mapping = merge_groups(group_data)
    
    # Apply 1% threshold for "Others"
    group_counts = merged_groups.value_counts()
    total_subjects = len(merged_groups)
    threshold = 0.01 * total_subjects
    
    major_groups = group_counts[group_counts >= threshold]
    minor_groups = group_counts[group_counts < threshold]
    
    if len(minor_groups) > 0:
        final_counts = major_groups.copy()
        final_counts['Others'] = minor_groups.sum()
        minor_group_names = minor_groups.index.tolist()
    else:
        final_counts = major_groups
        minor_group_names = []
    
    # Single bar plot
    fig, ax = plt.subplots(1, 1, figsize=(16, 10))
    
    bars = ax.bar(range(len(final_counts)), final_counts.values, 
                  color=COLORS[:len(final_counts)], alpha=0.8, 
                  edgecolor='black', linewidth=0.5)
    ax.set_xticks(range(len(final_counts)))
    ax.set_xticklabels(final_counts.index, rotation=45, ha='right', fontsize=12)
    ax.set_title(f'Merged Group Distribution (n={len(merged_groups):,} subjects, <1% → Others)', 
                 fontsize=14, fontweight='bold', pad=15)
    ax.set_xlabel('Group', fontsize=12, fontweight='bold')
    ax.set_ylabel('Number of Subjects', fontsize=12, fontweight='bold')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_linewidth(1.2)
    ax.spines['bottom'].set_linewidth(1.2)
    
    # Add value labels on bars with percentages
    for bar in bars:
        height = bar.get_height()
        percentage = (height / total_subjects) * 100
        ax.text(bar.get_x() + bar.get_width()/2., height + max(final_counts.values)*0.01,
                f'{int(height):,}\n({percentage:.1f}%)', ha='center', va='bottom', 
                fontweight='bold', fontsize=10)
    
    plt.tight_layout()
    plt.savefig(figures_dir / 'group_distribution.png', dpi=300, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    plt.show()
    
    # Print comprehensive mapping changes
    print("\n" + "=" * 60)
    print("GROUP MERGING CHANGES")
    print("=" * 60)
    print("Mapping applied:")
    
    # Group the mappings by category for better readability
    category_mappings = {}
    for original, merged in group_mapping.items():
        if merged not in category_mappings:
            category_mappings[merged] = []
        category_mappings[merged].append(original)
        
    print(f"\nOriginal vs Merged Group Counts:")
    print("ORIGINAL GROUPS (top 20):")
    for group, count in original_group_counts.head(20).items():
        print(f"  {group}: {count}")
    
    if len(original_group_counts) > 20:
        print(f"  ... and {len(original_group_counts) - 20} more groups")
    
    print("\nMERGED GROUPS:")
    for group, count in final_counts.items():
        percentage = (count / total_subjects) * 100
        print(f"  {group}: {count:,} ({percentage:.1f}%)")
    
    if minor_group_names:
        print(f"\nGroups merged into 'Others' (< 1%):")
        for group_name in minor_group_names:
            original_count = group_counts[group_name]
            percentage = (original_count / total_subjects) * 100
            print(f"  {group_name}: {original_count} ({percentage:.1f}%)")
    
    print(f"\nDetailed Category Mappings:")
    for category, originals in category_mappings.items():
        if len(originals) > 1:  # Only show categories that actually merged groups
            print(f"\n{category}:")
            for orig in sorted(originals):
                orig_count = original_group_counts.get(orig, 0)
                print(f"    {orig} ({orig_count} subjects)")
    
    print(f"\nSummary:")
    print(f"  Original groups: {len(original_group_counts)}")
    print(f"  Merged groups (before Others): {len(group_counts)}")
    print(f"  Final groups (with Others): {len(final_counts)}")
    print(f"  Groups moved to Others: {len(minor_group_names)}")
    print(f"  Reduction: {len(original_group_counts) - len(final_counts)} groups")

def plot_slice_thickness_analysis(mri_info_df):
    """Plot slice thickness distribution with histogram and KDE overlay"""
    figures_dir = ensure_figures_folder()
    
    # Load data
    fomo300k = pd.read_csv('FOMO300K_slice_thickness.csv')
    fomo60k = pd.read_csv('FOMO60K_slice_thickness.csv')
    openmind = pd.read_csv('OpenMind_slice_thickness.csv')

    # Bin values > 7mm into 7
    fomo300k['thickness_binned'] = fomo300k['slice_thickness'].apply(lambda x: 7 if x > 7 else x)
    fomo60k['thickness_binned'] = fomo60k['slice_thickness'].apply(lambda x: 7 if x > 7 else x)
    openmind['thickness_binned'] = openmind['slice_thickness'].apply(lambda x: 7 if x > 7 else x)

    colors = ['#2E86AB', '#A23B72', '#F18F01']

    fig, ax = plt.subplots(figsize=(12, 6))

    # Define bins
    bin_edges = [0, 0.5, 1.5, 2.5, 3.5, 4.5, 5.5, 6.5, 100]

    # Count values in each bin
    fomo300k_counts, _ = np.histogram(fomo300k['thickness_binned'], bins=bin_edges)
    fomo60k_counts, _ = np.histogram(fomo60k['thickness_binned'], bins=bin_edges)
    openmind_counts, _ = np.histogram(openmind['thickness_binned'], bins=bin_edges)

    # Bin centers for positioning bars
    bin_centers = [(bin_edges[i] + bin_edges[i+1])/2 for i in range(len(bin_edges)-1)]
    bin_centers[-1] = 7.0

    width = 0.25

    # Plot bars with transparency at bin centers
    bars1 = ax.bar(np.array(bin_centers) - width, fomo300k_counts, width, label='FOMO-300K', 
                   color=colors[0], alpha=0.5, edgecolor='black', linewidth=0.5)
    bars2 = ax.bar(bin_centers, fomo60k_counts, width, label='FOMO-60K', 
                   color=colors[1], alpha=0.5, edgecolor='black', linewidth=0.5)
    bars3 = ax.bar(np.array(bin_centers) + width, openmind_counts, width, label='OpenMind', 
                   color=colors[2], alpha=0.5, edgecolor='black', linewidth=0.5)

    # Create secondary axis for KDE
    ax2 = ax.twinx()

    # Compute KDE for the range 0-7.5
    x_range = np.linspace(0, 7.5, 500)

    # Compute KDE for each dataset
    kde_fomo300k = stats.gaussian_kde(fomo300k['thickness_binned'])
    kde_fomo60k = stats.gaussian_kde(fomo60k['thickness_binned'])
    kde_openmind = stats.gaussian_kde(openmind['thickness_binned'])

    # Plot KDE curves
    ax2.plot(x_range, kde_fomo300k(x_range), linewidth=2.5, color=colors[0])
    ax2.plot(x_range, kde_fomo60k(x_range), linewidth=2.5, color=colors[1])
    ax2.plot(x_range, kde_openmind(x_range), linewidth=2.5, color=colors[2])

    # Create x-axis labels
    bin_labels = ['<0.5', '0.5-1.5', '1.5-2.5', '2.5-3.5', '3.5-4.5', '4.5-5.5', '5.5-6.5', '≥6.5']

    # Set x-axis with labels at bin centers
    ax.set_xticks(bin_centers)
    ax.set_xticklabels(bin_labels, fontsize=11)
    ax.set_xlabel('Slice Thickness (mm)', fontsize=14, fontweight='bold')
    ax.set_ylabel('Count', fontsize=14, fontweight='bold')
    ax2.set_ylabel('Density', fontsize=14, fontweight='bold')
    ax.tick_params(axis='y', labelsize=11)
    ax2.tick_params(axis='y', labelsize=11)

    # Make both y-axes start from 0
    ax.set_ylim(bottom=0)
    ax2.set_ylim(bottom=0)

    # Set x-axis limits
    ax.set_xlim(-0.5, 7.5)

    # Legend on the right
    ax.legend(fontsize=12, frameon=True, fancybox=True, shadow=True, loc='upper right')

    ax.spines['top'].set_visible(False)
    ax2.spines['top'].set_visible(False)
    ax.spines['left'].set_linewidth(1.2)
    ax.spines['bottom'].set_linewidth(1.2)
    ax2.spines['right'].set_linewidth(1.2)

    plt.tight_layout()
    plt.savefig(figures_dir / 'slice_thickness_histogram_kde.png', dpi=300, bbox_inches='tight')
    plt.show()

def plot_mri_acquisition_info(mri_info_df):
    """Plot MRI acquisition parameters"""
    if mri_info_df.empty:
        print("No MRI acquisition data available")
        return
    
    # Clean the data first
    cleaned_mri_df = clean_mri_manufacturers(mri_info_df)
    cleaned_mri_df = clean_field_strengths(cleaned_mri_df)
    
    figures_dir = ensure_figures_folder()
    fig, axes = plt.subplots(2, 2, figsize=(20, 14))
    
    # Manufacturer distribution - horizontal bar chart
    if 'Manufacturer' in cleaned_mri_df.columns:
        manufacturer_counts = cleaned_mri_df['Manufacturer'].value_counts()
        
        # Group small manufacturers into "Others" if < 0.5%
        # FIXED: Use sum of manufacturer_counts instead of len(cleaned_mri_df)
        total_scans_with_mfg = manufacturer_counts.sum()  # Only scans with valid manufacturer data
        threshold = 0.005 * total_scans_with_mfg
        major_mfgs = manufacturer_counts[manufacturer_counts >= threshold]
        minor_mfgs = manufacturer_counts[manufacturer_counts < threshold]
        
        if len(minor_mfgs) > 0:
            final_mfg_counts = major_mfgs.copy()
            final_mfg_counts['Others'] = minor_mfgs.sum()
        else:
            final_mfg_counts = major_mfgs
        
        bars = axes[0,0].barh(range(len(final_mfg_counts)), final_mfg_counts.values, 
                             color=COLORS[:len(final_mfg_counts)], alpha=0.8, 
                             edgecolor='black', linewidth=0.5)
        axes[0,0].set_yticks(range(len(final_mfg_counts)))
        axes[0,0].set_yticklabels(final_mfg_counts.index, fontsize=11)
        axes[0,0].set_title(f'Scanner Manufacturers (n={total_scans_with_mfg:,} scans)', 
                           fontsize=14, fontweight='bold', pad=15)
        axes[0,0].set_xlabel('Number of Scans', fontsize=12, fontweight='bold')
        axes[0,0].invert_yaxis()
        axes[0,0].spines['top'].set_visible(False)
        axes[0,0].spines['right'].set_visible(False)
        axes[0,0].spines['left'].set_linewidth(1.2)
        axes[0,0].spines['bottom'].set_linewidth(1.2)
        
        # Add value labels with percentages - FIXED denominator
        for i, bar in enumerate(bars):
            width = bar.get_width()
            percentage = (width / total_scans_with_mfg) * 100
            axes[0,0].text(width + max(final_mfg_counts.values)*0.01, bar.get_y() + bar.get_height()/2,
                          f'{int(width):,} ({percentage:.1f}%)', ha='left', va='center', 
                          fontweight='bold', fontsize=10)
    
    # Scanner model distribution (top 20) - colored by manufacturer
    if 'ManufacturersModelName' in cleaned_mri_df.columns and 'Manufacturer' in cleaned_mri_df.columns:
        model_counts = cleaned_mri_df['ManufacturersModelName'].value_counts().head(20)
        
        # Create manufacturer color mapping
        manufacturer_color_map = {}
        for i, manufacturer in enumerate(final_mfg_counts.index):
            manufacturer_color_map[manufacturer] = COLORS[i % len(COLORS)]
        
        # Map each scanner model to its manufacturer and get corresponding color
        model_colors = []
        for model in model_counts.index:
            model_manufacturer = cleaned_mri_df[cleaned_mri_df['ManufacturersModelName'] == model]['Manufacturer'].iloc[0]
            model_colors.append(manufacturer_color_map.get(model_manufacturer, COLORS[0]))
        
        bars = axes[0,1].barh(range(len(model_counts)), model_counts.values, 
                             color=model_colors, alpha=0.8, edgecolor='black', linewidth=0.5)
        axes[0,1].set_yticks(range(len(model_counts)))
        axes[0,1].set_yticklabels([name[:25] + '...' if len(name) > 25 else name 
                                  for name in model_counts.index], fontsize=10)
        axes[0,1].set_title('Top 20 Scanner Models (colored by manufacturer)', fontsize=14, fontweight='bold', pad=15)
        axes[0,1].set_xlabel('Number of Scans', fontsize=12, fontweight='bold')
        axes[0,1].invert_yaxis()
        axes[0,1].spines['top'].set_visible(False)
        axes[0,1].spines['right'].set_visible(False)
        axes[0,1].spines['left'].set_linewidth(1.2)
        axes[0,1].spines['bottom'].set_linewidth(1.2)
        
        # Add value labels with percentages - FIXED denominator
        for i, bar in enumerate(bars):
            width = bar.get_width()
            percentage = (width / total_scans_with_mfg) * 100
            axes[0,1].text(width + max(model_counts.values)*0.01, bar.get_y() + bar.get_height()/2,
                          f'{int(width):,} ({percentage:.1f}%)', ha='left', va='center', 
                          fontweight='bold', fontsize=9)
        
        # Add a legend for manufacturer colors
        legend_elements = [plt.Rectangle((0,0),1,1, facecolor=manufacturer_color_map[mfg], alpha=0.8, 
                                        edgecolor='black', linewidth=0.5) 
                          for mfg in final_mfg_counts.index]
        axes[0,1].legend(legend_elements, final_mfg_counts.index, title='Manufacturer Colors', 
                  loc='lower right', fontsize=9, title_fontsize=10)
    
    # Field strength distribution - vertical bar chart
    if 'MagneticFieldStrength' in cleaned_mri_df.columns:
        field_strength = cleaned_mri_df['MagneticFieldStrength'].dropna()
        if not field_strength.empty:
            field_counts = field_strength.value_counts().sort_index()
            
            # Filter out extremely rare or obviously wrong values for display
            field_counts = field_counts[field_counts >= 5]  # At least 5 scans
            
            bars = axes[1,0].bar(range(len(field_counts)), field_counts.values, 
                                color=COLORS[2], alpha=0.8, edgecolor='black', linewidth=0.5)
            axes[1,0].set_xticks(range(len(field_counts)))
            axes[1,0].set_xticklabels([f'{x}T' for x in field_counts.index], fontsize=11, rotation=45)
            axes[1,0].set_title('Magnetic Field Strength Distribution', 
                               fontsize=14, fontweight='bold', pad=15)
            axes[1,0].set_xlabel('Field Strength (Tesla)', fontsize=12, fontweight='bold')
            axes[1,0].set_ylabel('Number of Scans', fontsize=12, fontweight='bold')
            axes[1,0].spines['top'].set_visible(False)
            axes[1,0].spines['right'].set_visible(False)
            axes[1,0].spines['left'].set_linewidth(1.2)
            axes[1,0].spines['bottom'].set_linewidth(1.2)
            
            # Add value labels with percentages on bars
            for i, bar in enumerate(bars):
                height = bar.get_height()
                percentage = (height / len(field_strength)) * 100
                axes[1,0].text(bar.get_x() + bar.get_width()/2., height + max(field_counts.values)*0.01,
                              f'{int(height):,}\n({percentage:.1f}%)', ha='center', va='bottom', 
                              fontweight='bold', fontsize=9)
    
    # Acquisition type distribution - horizontal bar chart
    if 'MRAcquisitionType' in cleaned_mri_df.columns:
        # Clean acquisition types (merge 3D and 3d)
        acq_types = cleaned_mri_df['MRAcquisitionType'].str.upper()
        acq_counts = acq_types.value_counts()
        total_acq_scans = acq_counts.sum()
        
        bars = axes[1,1].barh(range(len(acq_counts)), acq_counts.values, 
                             color=COLORS[:len(acq_counts)], alpha=0.8, 
                             edgecolor='black', linewidth=0.5)
        axes[1,1].set_yticks(range(len(acq_counts)))
        axes[1,1].set_yticklabels(acq_counts.index, fontsize=11)
        axes[1,1].set_title(f'MR Acquisition Types (n={total_acq_scans:,} scans)', 
                           fontsize=14, fontweight='bold', pad=15)
        axes[1,1].set_xlabel('Number of Scans', fontsize=12, fontweight='bold')
        axes[1,1].invert_yaxis()
        axes[1,1].spines['top'].set_visible(False)
        axes[1,1].spines['right'].set_visible(False)
        axes[1,1].spines['left'].set_linewidth(1.2)
        axes[1,1].spines['bottom'].set_linewidth(1.2)
        
        # Add value labels with percentages - FIXED denominator
        for i, bar in enumerate(bars):
            width = bar.get_width()
            percentage = (width / total_acq_scans) * 100
            axes[1,1].text(width + max(acq_counts.values)*0.01, bar.get_y() + bar.get_height()/2,
                          f'{int(width):,} ({percentage:.1f}%)', ha='left', va='center', 
                          fontweight='bold', fontsize=10)
    
    plt.tight_layout()
    plt.savefig(figures_dir / 'mri_acquisition_info.png', dpi=300, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    plt.show()
    
    # Print enhanced summary statistics with cleaned data
    print("\n" + "=" * 70)
    print("MRI ACQUISITION ANALYSIS (CLEANED)")
    print("=" * 70)
    
    if 'Manufacturer' in cleaned_mri_df.columns:
        print(f"Scanner Manufacturers (n={total_scans_with_mfg:,} scans):")
        for i, (mfg, count) in enumerate(final_mfg_counts.items()):
            percentage = (count / total_scans_with_mfg) * 100
            connector = "├──" if i < len(final_mfg_counts) - 1 else "└──"
            print(f"{connector} {mfg}: {count:,} ({percentage:.1f}%)")
    
    if 'MagneticFieldStrength' in cleaned_mri_df.columns:
        field_data = cleaned_mri_df['MagneticFieldStrength'].dropna()
        if not field_data.empty:
            print(f"\nField Strength Distribution (cleaned):")
            for i, (strength, count) in enumerate(field_data.value_counts().sort_index().items()):
                percentage = (count / len(field_data)) * 100
                connector = "├──" if i < len(field_data.value_counts()) - 1 else "└──"
                print(f"{connector} {strength}T: {count:,} ({percentage:.1f}%)")
                
    if 'MRAcquisitionType' in cleaned_mri_df.columns:
        acq_data = cleaned_mri_df['MRAcquisitionType'].str.upper().value_counts()
        total_acq = acq_data.sum()
        print(f"\nAcquisition Types:")
        for i, (acq_type, count) in enumerate(acq_data.items()):
            percentage = (count / total_acq) * 100
            connector = "├──" if i < len(acq_data) - 1 else "└──"
            print(f"{connector} {acq_type}: {count:,} ({percentage:.1f}%)")

def plot_modality_and_sequence_distributions(mapping_df):
    """Plot modality and sequence distributions"""
    figures_dir = ensure_figures_folder()
    
    # Prepare sequence data
    sequences_clean = clean_sequences(mapping_df)
    sequence_counts = sequences_clean.value_counts().head(15)
    
    # Prepare modality data
    modality_counts = mapping_df['modality'].value_counts()
    
    # Create modality color mapping
    modality_color_map = {}
    for i, modality in enumerate(modality_counts.index):
        modality_color_map[modality] = COLORS[i % len(COLORS)]
    
    # Map each sequence to its modality and get corresponding color
    sequence_colors = []
    for seq in sequence_counts.index:
        seq_modalities = mapping_df[clean_sequences(mapping_df) == seq]['modality'].value_counts()
        if not seq_modalities.empty:
            primary_modality = seq_modalities.index[0]
            sequence_colors.append(modality_color_map.get(primary_modality, COLORS[0]))
        else:
            sequence_colors.append(COLORS[0])
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(24, 10))
    
    # Modality distribution
    bars1 = ax1.bar(modality_counts.index, modality_counts.values, 
                    color=[modality_color_map[mod] for mod in modality_counts.index], alpha=0.8,
                    edgecolor='black', linewidth=0.5)
    ax1.set_title('Modality Distribution', fontsize=14, fontweight='bold', pad=15)
    ax1.set_xlabel('Modality', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Number of Scans', fontsize=12, fontweight='bold')
    ax1.tick_params(axis='x', rotation=45, labelsize=11)
    ax1.tick_params(axis='y', labelsize=11)
    ax1.spines['top'].set_visible(False)
    ax1.spines['right'].set_visible(False)
    ax1.spines['left'].set_linewidth(1.2)
    ax1.spines['bottom'].set_linewidth(1.2)
    
    total_scans_modality = len(mapping_df)
    for bar in bars1:
        height = bar.get_height()
        percentage = (height / total_scans_modality) * 100
        ax1.text(bar.get_x() + bar.get_width()/2., height + max(modality_counts.values)*0.01,
                f'{int(height):,}\n({percentage:.1f}%)', ha='center', va='bottom', 
                fontweight='bold', fontsize=10)
    
    # Sequence distribution
    bars2 = ax2.barh(range(len(sequence_counts)), sequence_counts.values, 
                     color=sequence_colors, alpha=0.8,
                     edgecolor='black', linewidth=0.5)
    ax2.set_yticks(range(len(sequence_counts)))
    ax2.set_yticklabels([seq[:25] + '...' if len(seq) > 25 else seq 
                        for seq in sequence_counts.index], fontsize=11)
    ax2.set_title('Top 15 Sequences by Scan Count (colored by modality)', fontsize=14, fontweight='bold', pad=15)
    ax2.set_xlabel('Number of Scans', fontsize=12, fontweight='bold')
    ax2.invert_yaxis()
    ax2.spines['top'].set_visible(False)
    ax2.spines['right'].set_visible(False)
    ax2.spines['left'].set_linewidth(1.2)
    ax2.spines['bottom'].set_linewidth(1.2)
    
    max_count = max(sequence_counts.values)
    total_scans = len(sequences_clean)
    for i, (seq, count) in enumerate(sequence_counts.items()):
        percentage = (count / total_scans) * 100
        ax2.text(count + max_count * 0.01, i, f'{count:,} ({percentage:.1f}%)', 
                va='center', ha='left', fontsize=10, fontweight='bold')
    
    # Add legend for modality colors
    legend_elements = [plt.Rectangle((0,0),1,1, facecolor=modality_color_map[mod], alpha=0.8, 
                                    edgecolor='black', linewidth=0.5) 
                      for mod in modality_counts.index]
    ax2.legend(legend_elements, modality_counts.index, title='Modality Colors', 
              loc='lower right', fontsize=10, title_fontsize=11)
    
    plt.tight_layout()
    plt.savefig(figures_dir / 'modality_and_sequence_distributions.png', dpi=300, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    plt.show()

def plot_sequences_per_session_matrix(mapping_df):
    """Create co-occurrence matrices"""
    figures_dir = ensure_figures_folder()
    
    mapping_df_clean = mapping_df.copy()
    mapping_df_clean['sequence_clean'] = clean_sequences(mapping_df)
    mapping_df_clean['sequence_clean'] = mapping_df_clean['sequence_clean'].str.replace(r'^dwi.*', 'dwi', regex=True, case=False)
    
    sequence_presence = mapping_df_clean.groupby(['dataset', 'participant_id', 'session_id'])['sequence_clean'].apply(list).reset_index()
    top_sequences = mapping_df_clean['sequence_clean'].value_counts().head(25).index.tolist()
    
    session_sequence_matrix = []
    for _, session_row in sequence_presence.iterrows():
        session_sequences = session_row['sequence_clean']
        binary_vector = [1 if seq in session_sequences else 0 for seq in top_sequences]
        session_sequence_matrix.append(binary_vector)
    
    session_df = pd.DataFrame(session_sequence_matrix, columns=top_sequences)
    sequence_correlation = session_df.corr()
    
    modality_presence = mapping_df_clean.groupby(['dataset', 'participant_id', 'session_id'])['modality'].apply(list).reset_index()
    all_modalities = mapping_df_clean['modality'].unique()
    
    modality_session_matrix = []
    for _, session_row in modality_presence.iterrows():
        session_modalities = session_row['modality']
        binary_vector = [1 if mod in session_modalities else 0 for mod in all_modalities]
        modality_session_matrix.append(binary_vector)
    
    modality_df = pd.DataFrame(modality_session_matrix, columns=all_modalities)
    modality_correlation = modality_df.corr()
    
    fig, axes = plt.subplots(1, 2, figsize=(24, 10))
    
    sns.heatmap(modality_correlation, annot=True, cmap='RdBu_r', center=0, 
                square=True, ax=axes[0], fmt='.2f', cbar_kws={'shrink': 0.8},
                linewidths=0.5, linecolor='white')
    axes[0].set_title('Modality Co-occurrence Matrix\n(Per-session correlation between modalities)', 
                     fontsize=14, fontweight='bold', pad=15)
    axes[0].tick_params(axis='x', rotation=45, labelsize=11)
    axes[0].tick_params(axis='y', rotation=0, labelsize=11)
    axes[0].set_xlabel('Modality', fontsize=12, fontweight='bold')
    axes[0].set_ylabel('Modality', fontsize=12, fontweight='bold')
    
    sns.heatmap(sequence_correlation, annot=False, cmap='RdBu_r', center=0, 
                square=True, ax=axes[1], fmt='.2f', cbar_kws={'shrink': 0.8},
                linewidths=0.1, linecolor='white',
                xticklabels=[seq[:15] + '...' if len(seq) > 15 else seq for seq in sequence_correlation.columns],
                yticklabels=[seq[:15] + '...' if len(seq) > 15 else seq for seq in sequence_correlation.index])
    axes[1].set_title(f'Sequence Co-occurrence Matrix (Top {len(top_sequences)} sequences)\n(Per-session correlation between sequences)', 
                     fontsize=14, fontweight='bold', pad=15)
    axes[1].tick_params(axis='x', rotation=45, labelsize=9)
    axes[1].tick_params(axis='y', rotation=45, labelsize=9)
    axes[1].set_xlabel('Sequence', fontsize=12, fontweight='bold')
    axes[1].set_ylabel('Sequence', fontsize=12, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(figures_dir / 'sequences_per_session_matrix.png', dpi=300, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    plt.show()

def plot_dataset_comparison(subjects_df, mapping_df):
    """Plot dataset comparison metrics"""
    figures_dir = ensure_figures_folder()
    
    fig, axes = plt.subplots(2, 2, figsize=(20, 14))
    
    dataset_subjects = subjects_df.groupby('dataset')['participant_id'].nunique().sort_values(ascending=False).head(12)
    total_subjects_all = subjects_df.groupby(['dataset', 'participant_id']).ngroups
    bars1 = axes[0,0].barh(range(len(dataset_subjects)), dataset_subjects.values, 
                          color=COLORS[0], alpha=0.8, edgecolor='black', linewidth=0.5)
    axes[0,0].set_yticks(range(len(dataset_subjects)))
    axes[0,0].set_yticklabels([name[:35] + '...' if len(name) > 35 else name 
                              for name in dataset_subjects.index], fontsize=10)
    axes[0,0].set_title('Top 12 Datasets by Subject Count', fontsize=14, fontweight='bold', pad=15)
    axes[0,0].set_xlabel('Number of Subjects', fontsize=12, fontweight='bold')
    axes[0,0].invert_yaxis()
    axes[0,0].spines['top'].set_visible(False)
    axes[0,0].spines['right'].set_visible(False)
    axes[0,0].spines['left'].set_linewidth(1.2)
    axes[0,0].spines['bottom'].set_linewidth(1.2)
    
    for i, bar in enumerate(bars1):
        width = bar.get_width()
        percentage = (width / total_subjects_all) * 100
        axes[0,0].text(width + max(dataset_subjects.values)*0.01, bar.get_y() + bar.get_height()/2,
                      f'{int(width):,} ({percentage:.1f}%)', ha='left', va='center', 
                      fontweight='bold', fontsize=9)
    
    dataset_scans = mapping_df['dataset'].value_counts().head(12)
    total_scans_all = len(mapping_df)
    bars2 = axes[0,1].barh(range(len(dataset_scans)), dataset_scans.values, 
                          color=COLORS[1], alpha=0.8, edgecolor='black', linewidth=0.5)
    axes[0,1].set_yticks(range(len(dataset_scans)))
    axes[0,1].set_yticklabels([name[:35] + '...' if len(name) > 35 else name 
                              for name in dataset_scans.index], fontsize=10)
    axes[0,1].set_title('Top 12 Datasets by Scan Count', fontsize=14, fontweight='bold', pad=15)
    axes[0,1].set_xlabel('Number of Scans', fontsize=12, fontweight='bold')
    axes[0,1].invert_yaxis()
    axes[0,1].spines['top'].set_visible(False)
    axes[0,1].spines['right'].set_visible(False)
    axes[0,1].spines['left'].set_linewidth(1.2)
    axes[0,1].spines['bottom'].set_linewidth(1.2)
    
    for i, bar in enumerate(bars2):
        width = bar.get_width()
        percentage = (width / total_scans_all) * 100
        axes[0,1].text(width + max(dataset_scans.values)*0.01, bar.get_y() + bar.get_height()/2,
                      f'{int(width):,} ({percentage:.1f}%)', ha='left', va='center', 
                      fontweight='bold', fontsize=9)
    
    dataset_sessions = subjects_df['dataset'].value_counts().head(12)
    total_sessions_all = len(subjects_df)
    bars3 = axes[1,0].barh(range(len(dataset_sessions)), dataset_sessions.values, 
                          color=COLORS[2], alpha=0.8, edgecolor='black', linewidth=0.5)
    axes[1,0].set_yticks(range(len(dataset_sessions)))
    axes[1,0].set_yticklabels([name[:35] + '...' if len(name) > 35 else name 
                              for name in dataset_sessions.index], fontsize=10)
    axes[1,0].set_title('Top 12 Datasets by Session Count', fontsize=14, fontweight='bold', pad=15)
    axes[1,0].set_xlabel('Number of Sessions', fontsize=12, fontweight='bold')
    axes[1,0].invert_yaxis()
    axes[1,0].spines['top'].set_visible(False)
    axes[1,0].spines['right'].set_visible(False)
    axes[1,0].spines['left'].set_linewidth(1.2)
    axes[1,0].spines['bottom'].set_linewidth(1.2)
    
    for i, bar in enumerate(bars3):
        width = bar.get_width()
        percentage = (width / total_sessions_all) * 100
        axes[1,0].text(width + max(dataset_sessions.values)*0.01, bar.get_y() + bar.get_height()/2,
                      f'{int(width):,} ({percentage:.1f}%)', ha='left', va='center', 
                      fontweight='bold', fontsize=9)
    
    modality_diversity = mapping_df.groupby('dataset')['modality'].nunique().sort_values(ascending=False).head(12)
    max_modalities = mapping_df['modality'].nunique()
    bars4 = axes[1,1].barh(range(len(modality_diversity)), modality_diversity.values, 
                          color=COLORS[3], alpha=0.8, edgecolor='black', linewidth=0.5)
    axes[1,1].set_yticks(range(len(modality_diversity)))
    axes[1,1].set_yticklabels([name[:35] + '...' if len(name) > 35 else name 
                              for name in modality_diversity.index], fontsize=10)
    axes[1,1].set_title('Top 12 Datasets by Modality Diversity', fontsize=14, fontweight='bold', pad=15)
    axes[1,1].set_xlabel('Number of Different Modalities', fontsize=12, fontweight='bold')
    axes[1,1].invert_yaxis()
    axes[1,1].spines['top'].set_visible(False)
    axes[1,1].spines['right'].set_visible(False)
    axes[1,1].spines['left'].set_linewidth(1.2)
    axes[1,1].spines['bottom'].set_linewidth(1.2)
    
    for i, bar in enumerate(bars4):
        width = bar.get_width()
        percentage = (width / max_modalities) * 100
        axes[1,1].text(width + max(modality_diversity.values)*0.1, bar.get_y() + bar.get_height()/2,
                      f'{int(width)} ({percentage:.1f}%)', ha='left', va='center', 
                      fontweight='bold', fontsize=9)
    
    plt.tight_layout()
    plt.savefig(figures_dir / 'dataset_comparisons.png', dpi=300, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    plt.show()
