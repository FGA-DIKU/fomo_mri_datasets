#!/bin/bash

# ===========================================
# Dataset Reshuffling and Anonymization Script
# ===========================================

# Customizable naming prefixes
SUBJECT_PREFIX="sub_"  # Prefix for subject folders
SESSION_PREFIX="ses_"  # Prefix for session folders
SCAN_PREFIX="scan_"    # Prefix for default scan naming
SEED=12345  # Fixed seed for deterministic selection
MAX_SCANS=-1  # Default: no limit (-1)

# ===========================================
# Scan type name mapping dictionary
# ===========================================
declare -A scan_type_map
# T1 group
scan_type_map["T1w"]="t1"
scan_type_map["T1W"]="t1"
scan_type_map["t1w"]="t1"
scan_type_map["t1W"]="t1"
scan_type_map["T1"]="t1"
scan_type_map["t1"]="t1"
scan_type_map["MPR"]="t1"
scan_type_map["mpr"]="t1"
scan_type_map["MPRAGE"]="t1"
scan_type_map["mprage"]="t1"
scan_type_map["MP2RAGE"]="t1"
scan_type_map["mp2rage"]="t1"
scan_type_map["T1_MPR"]="t1"
scan_type_map["3D_T1"]="t1"
scan_type_map["3DT1"]="t1"
scan_type_map["BRAVO"]="t1"
scan_type_map["FSPGR"]="t1"
scan_type_map["T1W_3D"]="t1"
scan_type_map["3D_MPRAGE"]="t1"
scan_type_map["IR_FSPGR"]="t1"
scan_type_map["SPGR"]="t1"
scan_type_map["T1_SPGR"]="t1"
scan_type_map["T1_FLAIR"]="t1"
scan_type_map["3D_BRAVO"]="t1"
scan_type_map["T1_IR"]="t1"
# T1 contrast group
scan_type_map["t1ce"]="t1c"
scan_type_map["T1ce"]="t1c"
scan_type_map["t1c"]="t1c"
scan_type_map["gad"]="t1c"
scan_type_map["GAD"]="t1c"
scan_type_map["Gad"]="t1c"
scan_type_map["t1gd"]="t1c"
scan_type_map["T1gd"]="t1c"
scan_type_map["t1GD"]="t1c"
scan_type_map["T1GD"]="t1c"
scan_type_map["t1+gad"]="t1c"
scan_type_map["T1+gad"]="t1c"
scan_type_map["t1+GAD"]="t1c"
scan_type_map["T1+GAD"]="t1c"
scan_type_map["T1+C"]="t1c"
scan_type_map["t1+c"]="t1c"
scan_type_map["T1C"]="t1c"
scan_type_map["POST"]="t1c"
scan_type_map["post"]="t1c"
scan_type_map["T1W_POST"]="t1c"
scan_type_map["T1_POST"]="t1c"
scan_type_map["T1W+C"]="t1c"
scan_type_map["3D_T1_POST"]="t1c"
scan_type_map["MPRAGE+C"]="t1c"
scan_type_map["MPRAGE_POST"]="t1c"
scan_type_map["T1_3D_POST"]="t1c"
scan_type_map["CONTRAST"]="t1c"
# FLAIR group
scan_type_map["flair"]="flair"
scan_type_map["FLAIR"]="flair"
scan_type_map["t2f"]="flair"
scan_type_map["T2_FLAIR"]="flair"
scan_type_map["t2_flair"]="flair"
scan_type_map["T2FLAIR"]="flair"
scan_type_map["t2flair"]="flair"
scan_type_map["T2-FLAIR"]="flair"
scan_type_map["t2-flair"]="flair"
scan_type_map["DARK_FLUID"]="flair"
scan_type_map["dark_fluid"]="flair"
scan_type_map["3D_FLAIR"]="flair"
scan_type_map["FLUID"]="flair"
# T2 group
scan_type_map["T2"]="t2"
scan_type_map["T2W"]="t2"
scan_type_map["T2w"]="t2"
scan_type_map["t2"]="t2"
scan_type_map["t2w"]="t2"
scan_type_map["T2-weighted"]="t2"
scan_type_map["t2-weighted"]="t2"
scan_type_map["T2_TSE"]="t2"
scan_type_map["T2_FSE"]="t2"
scan_type_map["FSE_T2"]="t2"
scan_type_map["TSE_T2"]="t2"
# PD group
scan_type_map["PD"]="pd"
scan_type_map["pd"]="pd"
scan_type_map["Pd"]="pd"
scan_type_map["PDW"]="pd"
scan_type_map["pdw"]="pd"
scan_type_map["PD_W"]="pd"
scan_type_map["pd_w"]="pd"
scan_type_map["PROTON"]="pd"
scan_type_map["proton"]="pd"
scan_type_map["PROTON_DENSITY"]="pd"
scan_type_map["proton_density"]="pd"
scan_type_map["PD/T2"]="pd"
scan_type_map["pd/t2"]="pd"
# T2 star group
scan_type_map["T2*"]="t2s"
scan_type_map["t2*"]="t2s"
scan_type_map["T2S"]="t2s"
scan_type_map["T2s"]="t2s"
scan_type_map["t2s"]="t2s"
scan_type_map["T2star"]="t2s"
scan_type_map["T2Star"]="t2s"
scan_type_map["t2star"]="t2s"
scan_type_map["T2STAR"]="t2s"
scan_type_map["t2STAR"]="t2s"
scan_type_map["GRE"]="t2s"
scan_type_map["gre"]="t2s"
scan_type_map["T2*_GRE"]="t2s"
scan_type_map["T2STAR_GRE"]="t2s"
scan_type_map["GRE_T2*"]="t2s"
scan_type_map["FFE"]="t2s"
scan_type_map["T2_FFE"]="t2s"
# DWI group
scan_type_map["DWI"]="dwi"
scan_type_map["dwi"]="dwi"
scan_type_map["dw"]="dwi"
scan_type_map["DW"]="dwi"
scan_type_map["diffusion"]="dwi"
scan_type_map["Diffusion"]="dwi"
scan_type_map["DIFFUSION"]="dwi"
scan_type_map["DTI"]="dwi"
scan_type_map["dti"]="dwi"
scan_type_map["B1000"]="dwi"
scan_type_map["b1000"]="dwi"
scan_type_map["B2000"]="dwi"
scan_type_map["b2000"]="dwi"
scan_type_map["B0"]="dwi"
scan_type_map["b0"]="dwi"
scan_type_map["TRACE"]="dwi"
scan_type_map["trace"]="dwi"
scan_type_map["EPI"]="dwi"
scan_type_map["DIFF_EPI"]="dwi"
scan_type_map["EP_DWI"]="dwi"
scan_type_map["DWI_TRACE"]="dwi"
# ADC group
scan_type_map["ADC"]="adc"
scan_type_map["adc"]="adc"
scan_type_map["APPARENT"]="adc"
scan_type_map["apparent"]="adc"
scan_type_map["ADC_MAP"]="adc"
scan_type_map["adc_map"]="adc"
scan_type_map["DIFFUSION_ADC"]="adc"
scan_type_map["DWI_ADC"]="adc"
# SWI group
scan_type_map["SWI"]="swi"
scan_type_map["swi"]="swi"
scan_type_map["susceptibility"]="swi"
scan_type_map["Susceptibility"]="swi"
scan_type_map["SUSCEPTIBILITY"]="swi"
scan_type_map["SW"]="swi"
scan_type_map["sw"]="swi"
scan_type_map["SWI_PHASE"]="swi"
scan_type_map["SWAN"]="swi"
scan_type_map["VENOUS_BOLD"]="swi"
scan_type_map["HEMO"]="swi"
scan_type_map["PHASE"]="swi"

# ===========================================
# Functions
# ===========================================

# Function to print usage instructions
usage() {
    echo "Usage: $0 -i <input_datasets_list> -o <output_folder> [-s <subject_prefix>] [-e <session_prefix>] [-c <scan_prefix>] [-m <max_scans>] [-map <mapping_file>]"
    echo "  -i: Text file containing dataset paths and names (tab or space separated)"
    echo "      Format: /path/to/dataset  PT001_DatasetName"
    echo "      Example: /data/OASIS  PT001_OASIS"
    echo "  -o: Output folder where anonymized datasets will be created"
    echo "  -s: Subject folder prefix (default: 'sub_')"
    echo "  -e: Session folder prefix (default: 'ses_')"
    echo "  -c: Default scan prefix (default: 'scan_')"
    echo "  -m: Maximum number of scans to include (default: no limit)"
    echo "  -map: Output file to save the mapping information (default: mapping.csv)"
    exit 1
}

# Function to get scan name based on original filename
# Returns: scan_type to be used for further processing
get_scan_type() {
    local original_name=$1

    # Extract scan type from filename (without extension)
    local base_name=$(basename "$original_name" | sed 's/\.[^.]*$//' | sed 's/\.[^.]*$//')

    # Check if the scan type is in our dictionary
    for key in "${!scan_type_map[@]}"; do
        if [[ "$base_name" == *"$key"* ]]; then
            echo "${scan_type_map[$key]}"
            return 0
        fi
    done

    # If not found in dictionary, return empty
    echo ""
    return 1
}

# Function to ensure .nii.gz extension
ensure_nifti_gz() {
    local input_file=$1
    local output_file=$2

    # Check if the file is already .nii.gz
    if [[ "$input_file" == *.nii.gz ]]; then
        cp "$input_file" "$output_file"
    # Check if the file is .nii and needs compression
    elif [[ "$input_file" == *.nii ]]; then
        echo "Compressing $input_file to $output_file"
        gzip -c "$input_file" > "$output_file"
    else
        echo "Warning: Unsupported file format for $input_file, attempting to copy as-is"
        cp "$input_file" "$output_file"
    fi
}

# Function to count scans in a subject directory
count_subject_scans() {
    local subject_dir=$1
    local scan_count=0

    # Count all nifti files in the subject directory (recursive)
    while IFS= read -r nifti_file; do
        if [ -f "$nifti_file" ]; then
            ((scan_count++))
        fi
    done < <(find "$subject_dir" -type f \( -name "*.nii" -o -name "*.nii.gz" \))

    echo "$scan_count"
}

# ===========================================
# Main script
# ===========================================

# Parse command line arguments
mapping_file="mapping.csv"
while getopts ":i:o:s:e:c:m:map:" opt; do
    case $opt in
        i) input_list="$OPTARG" ;;
        o) output_folder="$OPTARG" ;;
        s) SUBJECT_PREFIX="$OPTARG" ;;
        e) SESSION_PREFIX="$OPTARG" ;;
        c) SCAN_PREFIX="$OPTARG" ;;
        m) MAX_SCANS="$OPTARG" ;;
        map) mapping_file="$OPTARG" ;;
        \?) echo "Invalid option: -$OPTARG"; usage ;;
        :) echo "Option -$OPTARG requires an argument"; usage ;;
    esac
done

# Check if required arguments are provided
if [ -z "$input_list" ] || [ -z "$output_folder" ]; then
    usage
fi

# Check if input list exists
if [ ! -f "$input_list" ]; then
    echo "Error: Input list file '$input_list' does not exist."
    exit 1
fi

# Create output folder
mkdir -p "$output_folder"

# Create mapping file with header
echo "original_path,new_path,type" > "$mapping_file"

# Read all dataset paths into an array
declare -a datasets
declare -a dataset_names

while IFS= read -r line || [ -n "$line" ]; do
    # Skip empty lines and comments
    if [ -z "$line" ] || [[ "$line" =~ ^[[:space:]]*# ]]; then
        continue
    fi

    # Split by whitespace (tabs or spaces)
    read -r dataset_path dataset_name <<< "$line"

    # Trim whitespace
    dataset_path=$(echo "$dataset_path" | xargs)
    dataset_name=$(echo "$dataset_name" | xargs)

    # If no dataset name provided, extract from path
    if [ -z "$dataset_name" ]; then
        dataset_name=$(basename "$dataset_path")
    fi

    datasets+=("$dataset_path")
    dataset_names+=("$dataset_name")
done < "$input_list"

echo "Loaded ${#datasets[@]} datasets from $input_list"

# Initialize arrays to track dataset statistics
declare -a dataset_total_subjects
declare -a dataset_total_sessions
declare -a dataset_total_scans
declare -a dataset_used_subjects
declare -a dataset_used_sessions
declare -a dataset_used_scans
declare -a dataset_included # To ensure at least one subject per dataset

# Initialize with zeroes
for ((i=0; i<${#datasets[@]}; i++)); do
    dataset_total_subjects[i]=0
    dataset_total_sessions[i]=0
    dataset_total_scans[i]=0
    dataset_used_subjects[i]=0
    dataset_used_sessions[i]=0
    dataset_used_scans[i]=0
    dataset_included[i]=0
done

# Count total number of subjects across all datasets
total_subjects=0
declare -a all_subjects
declare -a subject_dataset_index # To track which dataset each subject belongs to
declare -a subject_scan_counts   # To track how many scans each subject has

# First pass: collect all subjects and their metadata
for dataset_idx in "${!datasets[@]}"; do
    dataset_path="${datasets[$dataset_idx]}"
    if [ ! -d "$dataset_path" ]; then
        echo "Warning: Dataset path '$dataset_path' does not exist or is not a directory. Skipping."
        continue
    fi

    subject_count=0  # Initialize counter for this dataset
    session_count=0  # Initialize session counter
    scan_count=0     # Initialize scan counter

    # Find all subject directories in this dataset - no specific naming pattern assumption
    for subject_dir in "$dataset_path"/*; do
        if [ -d "$subject_dir" ]; then
            all_subjects+=("$subject_dir")
            subject_dataset_index+=("$dataset_idx")

            # Count sessions in this subject
            local_session_count=0
            for session_dir in "$subject_dir"/*; do
                if [ -d "$session_dir" ]; then
                    ((local_session_count++))
                fi
            done

            # If no session directories found, count as 1 default session
            if [ "$local_session_count" -eq 0 ]; then
                local_session_count=1
            fi

            # Count scans
            local_scan_count=$(count_subject_scans "$subject_dir")
            subject_scan_counts+=("$local_scan_count")

            # Update dataset counters
            ((subject_count++))
            ((session_count+=local_session_count))
            ((scan_count+=local_scan_count))
        fi
    done

    # Store dataset statistics
    dataset_total_subjects[$dataset_idx]=$subject_count
    dataset_total_sessions[$dataset_idx]=$session_count
    dataset_total_scans[$dataset_idx]=$scan_count

    ((total_subjects+=$subject_count))

    echo "Dataset $((dataset_idx+1)) (${dataset_names[$dataset_idx]}): $subject_count subjects, $session_count sessions, $scan_count scans"
done

echo "Found $total_subjects subjects across all datasets."

# Deterministically shuffle the order of subjects using a fixed seed
echo "Setting up deterministic selection with seed: $SEED"

# Create a temporary file with indices and deterministic "random" values
tmp_file=$(mktemp)
for ((i=0; i<total_subjects; i++)); do
    # Generate a reproducible "random" value based on the seed and index
    random_val=$(( (i * 1103515245 + 12345) % 2147483647 ))
    random_val=$(( (random_val + SEED) % 2147483647 ))
    echo "$i $random_val" >> "$tmp_file"
done

# Sort based on the deterministic values and extract just the indices
shuffled_indices=($(sort -k2 -n "$tmp_file" | cut -d' ' -f1))

# Clean up
rm "$tmp_file"

echo "Deterministically selected ${#shuffled_indices[@]} subjects using seed $SEED"

# If max scans is specified, we need to determine how many subjects to include
total_included_scans=0
subjects_to_process=()

if [ "$MAX_SCANS" -gt 0 ]; then
    echo "Limiting dataset to at least $MAX_SCANS scans, including complete subjects..."

    # Process subjects in the deterministic shuffled order until reaching the scan limit
    # Display progress every 100 subjects
    for idx in "${shuffled_indices[@]}"; do
        # Only add subjects until we reach the minimum required scans
        if [ "$total_included_scans" -lt "$MAX_SCANS" ]; then
            subjects_to_process+=("$idx")
            scan_count="${subject_scan_counts[$idx]}"
            total_included_scans=$((total_included_scans + scan_count))
            dataset_idx=${subject_dataset_index[$idx]}
            dataset_used_subjects[$dataset_idx]=$((dataset_used_subjects[$dataset_idx] + 1))
            dataset_included[$dataset_idx]=1  # Mark this dataset as included

            # Print progress every 100 subjects
            if [ "$((${#subjects_to_process[@]} % 100))" -eq 0 ]; then
                echo "Added ${#subjects_to_process[@]} subjects, current scan count: $total_included_scans / $MAX_SCANS"
            fi
        fi
    done

    echo "Selected ${#subjects_to_process[@]} subjects with $total_included_scans scans (target: $MAX_SCANS)"
else
    # If no max scans specified, process all subjects in deterministic order
    subjects_to_process=("${shuffled_indices[@]}")

    # Count used subjects per dataset
    for idx in "${shuffled_indices[@]}"; do
        dataset_idx=${subject_dataset_index[$idx]}
        dataset_used_subjects[$dataset_idx]=$((dataset_used_subjects[$dataset_idx] + 1))
        dataset_included[$dataset_idx]=1
    done
fi

# Add arrays to track sessions per subject more accurately
declare -a subject_session_counts

# First collect session counts for each subject
for i in "${!all_subjects[@]}"; do
    subject_dir="${all_subjects[$i]}"
    session_count=0

    # Count actual session directories
    for session_dir in "$subject_dir"/*; do
        if [ -d "$session_dir" ]; then
            ((session_count++))
        fi
    done

    # If no session directories found, count as 1 default session
    if [ "$session_count" -eq 0 ]; then
        session_count=1
    fi

    subject_session_counts[$i]=$session_count
done

# Print summary before starting the copy operations
echo "=============================================="
echo "PRE-PROCESSING SUMMARY"
echo "=============================================="
echo "Original subjects: $total_subjects"
echo "Selected subjects: ${#subjects_to_process[@]}"
echo "Target directory: $output_folder"
echo "Mapping file: $mapping_file"

# Calculate and display dataset statistics
total_original_scans=0
total_original_sessions=0
total_original_subjects=0
total_selected_scans=0
total_selected_sessions=0

for dataset_idx in "${!datasets[@]}"; do
    dataset_path="${datasets[$dataset_idx]}"
    original_subjects=${dataset_total_subjects[$dataset_idx]}
    original_sessions=${dataset_total_sessions[$dataset_idx]}
    original_scans=${dataset_total_scans[$dataset_idx]}
    selected_subjects=${dataset_used_subjects[$dataset_idx]}

    # Calculate exact selected scans and sessions for this dataset
    selected_scans=0
    selected_sessions=0

    # Count sessions and scans for selected subjects in this dataset
    for j in "${!subjects_to_process[@]}"; do
        i=${subjects_to_process[$j]}
        if [ "${subject_dataset_index[$i]}" -eq "$dataset_idx" ]; then
            # Add scan count for this subject
            selected_scans=$((selected_scans + subject_scan_counts[$i]))

            # Add session count for this subject
            selected_sessions=$((selected_sessions + subject_session_counts[$i]))
        fi
    done

    # Calculate percentages (avoid division by zero)
    if [ "$original_subjects" -gt 0 ]; then
        subject_pct=$(awk "BEGIN {printf \"%.1f\", ($selected_subjects / $original_subjects) * 100}")
    else
        subject_pct="0.0"
    fi

    if [ "$original_sessions" -gt 0 ]; then
        session_pct=$(awk "BEGIN {printf \"%.1f\", ($selected_sessions / $original_sessions) * 100}")
    else
        session_pct="0.0"
    fi

    if [ "$original_scans" -gt 0 ]; then
        scan_pct=$(awk "BEGIN {printf \"%.1f\", ($selected_scans / $original_scans) * 100}")
    else
        scan_pct="0.0"
    fi

    echo "Dataset $((dataset_idx+1)) (${dataset_names[$dataset_idx]}):"
    echo "  Subjects: $selected_subjects / $original_subjects ($subject_pct%)"
    echo "  Sessions: $selected_sessions / $original_sessions ($session_pct%)"
    echo "  Scans: $selected_scans / $original_scans ($scan_pct%)"

    # Add to totals
    ((total_original_subjects+=original_subjects))
    ((total_original_sessions+=original_sessions))
    ((total_original_scans+=original_scans))
    ((total_selected_sessions+=selected_sessions))
    ((total_selected_scans+=selected_scans))
done

# Calculate overall percentages
total_selected_subjects=${#subjects_to_process[@]}

# Avoid division by zero
if [ "$total_original_subjects" -gt 0 ]; then
    total_subject_pct=$(awk "BEGIN {printf \"%.1f\", ($total_selected_subjects / $total_original_subjects) * 100}")
else
    total_subject_pct="0.0"
fi

if [ "$total_original_sessions" -gt 0 ]; then
    total_session_pct=$(awk "BEGIN {printf \"%.1f\", ($total_selected_sessions / $total_original_sessions) * 100}")
else
    total_session_pct="0.0"
fi

if [ "$total_original_scans" -gt 0 ]; then
    total_scan_pct=$(awk "BEGIN {printf \"%.1f\", ($total_selected_scans / $total_original_scans) * 100}")
else
    total_scan_pct="0.0"
fi

echo "--------------------------------------------"
echo "Overall planned utilization:"
echo "  Subjects: $total_selected_subjects / $total_original_subjects ($total_subject_pct%)"
echo "  Sessions: $total_selected_sessions / $total_original_sessions ($total_session_pct%)"
echo "  Scans: $total_selected_scans / $total_original_scans ($total_scan_pct%)"
echo "=============================================="
echo "Starting file copy operations..."

# Process subjects in deterministic order
new_subject_index=1

for i in "${subjects_to_process[@]}"; do
    original_subject_dir="${all_subjects[$i]}"
    dataset_idx=${subject_dataset_index[$i]}
    dataset_name="${dataset_names[$dataset_idx]}"

    # Create path to dataset folder
    dataset_output_dir="$output_folder/${dataset_name}"
    mkdir -p "$dataset_output_dir"

    # Create subject folder inside dataset folder with sequential numbering (no zero-padding)
    new_subject_dir="$dataset_output_dir/${SUBJECT_PREFIX}${new_subject_index}"

    echo "Processing: $original_subject_dir -> $new_subject_dir"
    mkdir -p "$new_subject_dir"

    # Record subject mapping
    echo "$original_subject_dir,$new_subject_dir,subject" >> "$mapping_file"

    # Process sessions for this subject
    session_index=1

    # Find all subdirectories as potential sessions
    session_found=false
    for original_session_dir in "$original_subject_dir"/*; do
        if [ -d "$original_session_dir" ]; then
            new_session_dir="$new_subject_dir/${SESSION_PREFIX}$session_index"
            mkdir -p "$new_session_dir"

            echo "  Session: $original_session_dir -> $new_session_dir"

            # Record session mapping
            echo "$original_session_dir,$new_session_dir,session" >> "$mapping_file"

            # Process all nifti files in this session
            scan_index=1

            # Create associative array to track scan type counts for this session
            declare -A type_counts

            # First, collect all files and their types
            declare -a session_files
            declare -a session_types

            while IFS= read -r original_nifti; do
                if [ -f "$original_nifti" ]; then
                    session_files+=("$original_nifti")

                    # Get scan type
                    scan_type=$(get_scan_type "$(basename "$original_nifti")")

                    # If no mapping found, use default naming
                    if [ -z "$scan_type" ]; then
                        scan_type="${SCAN_PREFIX}${scan_index}"
                        ((scan_index++))
                    fi

                    session_types+=("$scan_type")
                fi
            done < <(find "$original_session_dir" -type f \( -name "*.nii" -o -name "*.nii.gz" \))

            # Process files with counted types
            local_scan_count=0
            for idx in "${!session_files[@]}"; do
                original_nifti="${session_files[$idx]}"
                scan_type="${session_types[$idx]}"

                # Increment counter for this type
                if [ -z "${type_counts[$scan_type]}" ]; then
                    type_counts[$scan_type]=1
                else
                    ((type_counts[$scan_type]++))
                fi

                # Create name with counter
                if [ "${type_counts[$scan_type]}" -gt 1 ]; then
                    scan_name="${scan_type}_${type_counts[$scan_type]}"
                else
                    scan_name="${scan_type}"
                fi

                new_nifti="$new_session_dir/${scan_name}.nii.gz"

                echo "    Scan: $original_nifti -> $new_nifti"

                # Record scan mapping
                echo "$original_nifti,$new_nifti,scan" >> "$mapping_file"

                # Copy and ensure .nii.gz format
                ensure_nifti_gz "$original_nifti" "$new_nifti"
                ((local_scan_count++))
                ((dataset_used_scans[dataset_idx]++))
            done

            # Clean up
            unset type_counts
            unset session_files
            unset session_types

            # Update session counters
            if [ "$local_scan_count" -gt 0 ]; then
                ((dataset_used_sessions[dataset_idx]++))
            fi

            ((session_index++))
            session_found=true
        fi
    done

    # If no sessions were found, look for nifti files directly in the subject dir
    if [ "$session_found" = false ]; then
        new_session_dir="$new_subject_dir/${SESSION_PREFIX}1"
        mkdir -p "$new_session_dir"

        echo "  No sessions found, creating default session: $new_session_dir"

        # Record session mapping
        echo "$original_subject_dir,$new_session_dir,session" >> "$mapping_file"

        # Process all nifti files in the subject directory
        scan_index=1

        # Create associative array to track scan type counts
        declare -A type_counts

        # First, collect all files and their types
        declare -a subject_files
        declare -a subject_types

        while IFS= read -r original_nifti; do
            if [ -f "$original_nifti" ]; then
                subject_files+=("$original_nifti")

                # Get scan type
                scan_type=$(get_scan_type "$(basename "$original_nifti")")

                # If no mapping found, use default naming
                if [ -z "$scan_type" ]; then
                    scan_type="${SCAN_PREFIX}${scan_index}"
                    ((scan_index++))
                fi

                subject_types+=("$scan_type")
            fi
        done < <(find "$original_subject_dir" -maxdepth 3 -type f \( -name "*.nii" -o -name "*.nii.gz" \))

        # Process files with counted types
        local_scan_count=0
        for idx in "${!subject_files[@]}"; do
            original_nifti="${subject_files[$idx]}"
            scan_type="${subject_types[$idx]}"

            # Increment counter for this type
            if [ -z "${type_counts[$scan_type]}" ]; then
                type_counts[$scan_type]=1
            else
                ((type_counts[$scan_type]++))
            fi

            # Create name with counter
            if [ "${type_counts[$scan_type]}" -gt 1 ]; then
                scan_name="${scan_type}_${type_counts[$scan_type]}"
            else
                scan_name="${scan_type}"
            fi

            new_nifti="$new_session_dir/${scan_name}.nii.gz"

            echo "    Scan: $original_nifti -> $new_nifti"

            # Record scan mapping
            echo "$original_nifti,$new_nifti,scan" >> "$mapping_file"

            # Copy and ensure .nii.gz format
            ensure_nifti_gz "$original_nifti" "$new_nifti"
            ((local_scan_count++))
            ((dataset_used_scans[dataset_idx]++))
        done

        # Update session counters
        if [ "$local_scan_count" -gt 0 ]; then
            ((dataset_used_sessions[dataset_idx]++))
        fi

        # Clean up
        unset type_counts
        unset subject_files
        unset subject_types
    fi

    ((new_subject_index++))
done

# Print detailed statistics at the end of the script
echo "=============================================="
echo "Dataset reshuffling and anonymization complete."
echo "=============================================="
echo "Original subjects: $total_subjects"
echo "Processed subjects: $((new_subject_index-1))"
echo "Number of datasets: ${#datasets[@]}"
echo "Output directory: $output_folder"
echo "Mapping file: $mapping_file"
echo "Structure:"
echo "  Dataset folders: Names from input file (e.g., PT001_DATASET_NAME)"
echo "  Subject folders: ${SUBJECT_PREFIX}### (numbered sequentially across all datasets)"
echo "  Session prefix: $SESSION_PREFIX"
echo "  Default scan prefix: $SCAN_PREFIX"

# If max scans limit was applied, print detailed statistics
if [ "$MAX_SCANS" -gt 0 ]; then
    echo "=============================================="
    echo "Dataset Utilization Summary:"
    echo "=============================================="
    echo "Total scans in final dataset: $total_included_scans / $MAX_SCANS (target limit)"
    echo "--------------------------------------------"

    total_original_scans=0
    total_original_sessions=0
    total_original_subjects=0
    total_used_sessions=0
    total_used_scans=0

    for dataset_idx in "${!datasets[@]}"; do
        dataset_path="${datasets[$dataset_idx]}"
        original_subjects=${dataset_total_subjects[$dataset_idx]}
        original_sessions=${dataset_total_sessions[$dataset_idx]}
        original_scans=${dataset_total_scans[$dataset_idx]}
        used_subjects=${dataset_used_subjects[$dataset_idx]}
        used_sessions=${dataset_used_sessions[$dataset_idx]}
        used_scans=${dataset_used_scans[$dataset_idx]}

        # Calculate percentages (avoid division by zero)
        if [ "$original_subjects" -gt 0 ]; then
            subject_pct=$(awk "BEGIN {printf \"%.1f\", ($used_subjects / $original_subjects) * 100}")
        else
            subject_pct="0.0"
        fi

        if [ "$original_sessions" -gt 0 ]; then
            session_pct=$(awk "BEGIN {printf \"%.1f\", ($used_sessions / $original_sessions) * 100}")
        else
            session_pct="0.0"
        fi

        if [ "$original_scans" -gt 0 ]; then
            scan_pct=$(awk "BEGIN {printf \"%.1f\", ($used_scans / $original_scans) * 100}")
        else
            scan_pct="0.0"
        fi

        echo "Dataset $((dataset_idx+1)) (${dataset_names[$dataset_idx]}):"
        echo "  Subjects: $used_subjects / $original_subjects ($subject_pct%)"
        echo "  Sessions: $used_sessions / $original_sessions ($session_pct%)"
        echo "  Scans: $used_scans / $original_scans ($scan_pct%)"

        # Add to totals
        ((total_original_subjects+=original_subjects))
        ((total_original_sessions+=original_sessions))
        ((total_original_scans+=original_scans))
        ((total_used_sessions+=used_sessions))
        ((total_used_scans+=used_scans))
    done

    # Calculate overall percentages
    total_used_subjects=$((new_subject_index-1))

    # Avoid division by zero
    if [ "$total_original_subjects" -gt 0 ]; then
        total_subject_pct=$(awk "BEGIN {printf \"%.1f\", ($total_used_subjects / $total_original_subjects) * 100}")
    else
        total_subject_pct="0.0"
    fi

    if [ "$total_original_sessions" -gt 0 ]; then
        total_session_pct=$(awk "BEGIN {printf \"%.1f\", ($total_used_sessions / $total_original_sessions) * 100}")
    else
        total_session_pct="0.0"
    fi

    if [ "$total_original_scans" -gt 0 ]; then
        total_scan_pct=$(awk "BEGIN {printf \"%.1f\", ($total_used_scans / $total_original_scans) * 100}")
    else
        total_scan_pct="0.0"
    fi

    echo "--------------------------------------------"
    echo "Overall utilization:"
    echo "  Subjects: $total_used_subjects / $total_original_subjects ($total_subject_pct%)"
    echo "  Sessions: $total_used_sessions / $total_original_sessions ($total_session_pct%)"
    echo "  Scans: $total_used_scans / $total_original_scans ($total_scan_pct%)"
    echo "=============================================="
fi

# Always print a basic summary even when MAX_SCANS is not set
if [ "$MAX_SCANS" -le 0 ]; then
    echo "=============================================="
    echo "Dataset Utilization Summary:"
    echo "=============================================="

    total_original_scans=0
    total_original_sessions=0
    total_original_subjects=0
    total_used_subjects=0
    total_used_sessions=0
    total_used_scans=0

    for dataset_idx in "${!datasets[@]}"; do
        dataset_path="${datasets[$dataset_idx]}"
        original_subjects=${dataset_total_subjects[$dataset_idx]}
        original_sessions=${dataset_total_sessions[$dataset_idx]}
        original_scans=${dataset_total_scans[$dataset_idx]}
        used_subjects=${dataset_used_subjects[$dataset_idx]}
        used_sessions=${dataset_used_sessions[$dataset_idx]}
        used_scans=${dataset_used_scans[$dataset_idx]}

        # Calculate percentages (avoid division by zero)
        if [ "$original_subjects" -gt 0 ]; then
            subject_pct=$(awk "BEGIN {printf \"%.1f\", ($used_subjects / $original_subjects) * 100}")
        else
            subject_pct="0.0"
        fi

        if [ "$original_sessions" -gt 0 ]; then
            session_pct=$(awk "BEGIN {printf \"%.1f\", ($used_sessions / $original_sessions) * 100}")
        else
            session_pct="0.0"
        fi

        if [ "$original_scans" -gt 0 ]; then
            scan_pct=$(awk "BEGIN {printf \"%.1f\", ($used_scans / $original_scans) * 100}")
        else
            scan_pct="0.0"
        fi

        echo "Dataset $((dataset_idx+1)) (${dataset_names[$dataset_idx]}):"
        echo "  Subjects: $used_subjects / $original_subjects ($subject_pct%)"
        echo "  Sessions: $used_sessions / $original_sessions ($session_pct%)"
        echo "  Scans: $used_scans / $original_scans ($scan_pct%)"

        # Add to totals
        ((total_original_subjects+=original_subjects))
        ((total_original_sessions+=original_sessions))
        ((total_original_scans+=original_scans))
        ((total_used_subjects+=used_subjects))
        ((total_used_sessions+=used_sessions))
        ((total_used_scans+=used_scans))
    done

    # Calculate overall percentages
    # Avoid division by zero
    if [ "$total_original_subjects" -gt 0 ]; then
        total_subject_pct=$(awk "BEGIN {printf \"%.1f\", ($total_used_subjects / $total_original_subjects) * 100}")
    else
        total_subject_pct="0.0"
    fi

    if [ "$total_original_sessions" -gt 0 ]; then
        total_session_pct=$(awk "BEGIN {printf \"%.1f\", ($total_used_sessions / $total_original_sessions) * 100}")
    else
        total_session_pct="0.0"
    fi

    if [ "$total_original_scans" -gt 0 ]; then
        total_scan_pct=$(awk "BEGIN {printf \"%.1f\", ($total_used_scans / $total_original_scans) * 100}")
    else
        total_scan_pct="0.0"
    fi

    echo "--------------------------------------------"
    echo "Overall utilization:"
    echo "  Subjects: $total_used_subjects / $total_original_subjects ($total_subject_pct%)"
    echo "  Sessions: $total_used_sessions / $total_original_sessions ($total_session_pct%)"
    echo "  Scans: $total_used_scans / $total_original_scans ($total_scan_pct%)"
    echo "=============================================="
fi

echo "Mapping information saved to: $mapping_file"