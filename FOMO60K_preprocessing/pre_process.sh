#!/bin/bash
# Author: Stefano Cerri stce@di.ku.dk
# Pre-processing script for MRI data: RAS conversion, co-registration, skull stripping/defacing, label processing

# Check for FreeSurfer
[ -z "$FREESURFER_HOME" ] && { echo "Error: FREESURFER_HOME not set."; exit 1; }
command -v mri_convert &> /dev/null || { echo "Error: mri_convert not found."; exit 1; }

# Default settings
DO_COREGISTER=true
DO_SKULL_STRIP=true
DO_DEFACE=false
DO_CLEAN=true
MERGE_LABELS=false
MERGED_LABEL_NAME="merged_labels"
IMG_EXT=".nii.gz"
THREADS=1
REFERENCE_STRING=""
LABELS_DIR=""
LABELS_OUTPUT_DIR=""

# Function to display script usage
show_usage() {
    echo "Usage: $0 <input_folder> <output_folder> [options]"
    echo "Options:"
    echo "  -e, --extension EXT       Image extension (.nii, .nii.gz, or .mgz), default: .nii.gz"
    echo "  --no-coreg                Skip co-registration step"
    echo "  --no-skull-strip          Skip skull stripping step"
    echo "  --deface                  Use mideface for defacing instead of skull stripping"
    echo "  --no-clean                Keep temporary files (default: clean)"
    echo "  -r, --reference STRING    Use file containing STRING as reference (e.g., FLAIR)"
    echo "  -t, --threads NUM         Number of threads to use (default: 1)"
    echo "  -l, --labels DIR          Directory containing label files (optional)"
    echo "  -lo, --labels-output DIR  Separate output directory for label files (optional)"
    echo "  --merge-labels            Merge all labels into a single binary mask"
    echo "  --merged-name NAME        Name for the merged label file (default: merged_labels)"
    exit 1
}

# Parse command line arguments
[ $# -lt 2 ] && show_usage

INPUT_DIR="$1"
OUTPUT_DIR="$2"
shift 2

# Check if input directory exists
[ ! -d "$INPUT_DIR" ] && { echo "Error: Input directory not found: $INPUT_DIR"; exit 1; }

# Create output directory
mkdir -p "$OUTPUT_DIR"

# Parse additional options
while [ $# -gt 0 ]; do
    case "$1" in
        -e|--extension)
            IMG_EXT="$2"
            [[ ! "$IMG_EXT" =~ ^\.nii(\.gz)?$|^\.mgz$ ]] && { echo "Error: Extension must be .nii, .nii.gz, or .mgz"; exit 1; }
            shift 2
            ;;
        --no-coreg) DO_COREGISTER=false; shift ;;
        --no-skull-strip) DO_SKULL_STRIP=false; shift ;;
        --deface) DO_DEFACE=true; DO_SKULL_STRIP=false; shift ;;
        --no-clean) DO_CLEAN=false; shift ;;
        --merge-labels) MERGE_LABELS=true; shift ;;
        --merged-name) MERGED_LABEL_NAME="$2"; shift 2 ;;
        -r|--reference) REFERENCE_STRING="$2"; shift 2 ;;
        -t|--threads) 
            THREADS="$2"
            ! [[ "$THREADS" =~ ^[0-9]+$ ]] && { echo "Error: Threads must be a positive integer"; exit 1; }
            shift 2
            ;;
        -l|--labels)
            LABELS_DIR="$2"
            [ ! -d "$LABELS_DIR" ] && { echo "Error: Labels directory not found: $LABELS_DIR"; exit 1; }
            shift 2
            ;;
        -lo|--labels-output) LABELS_OUTPUT_DIR="$2"; shift 2 ;;
        *) echo "Unknown option: $1"; show_usage ;;
    esac
done

# Setup directories
TEMP_DIR="${OUTPUT_DIR}/temp"
IMG_RAS_DIR="${TEMP_DIR}/img_ras"
IMG_COREG_DIR="${TEMP_DIR}/img_coreg"
IMG_FINAL_DIR="${OUTPUT_DIR}"

mkdir -p "$TEMP_DIR" "$IMG_RAS_DIR" "$IMG_COREG_DIR"

# Setup label directories if needed
if [ -n "$LABELS_DIR" ]; then
    LAB_RAS_DIR="${TEMP_DIR}/lab_ras"
    LAB_COREG_DIR="${TEMP_DIR}/lab_coreg"
    LABELS_OUTPUT_DIR="${LABELS_OUTPUT_DIR:-${OUTPUT_DIR}/labels}"
    LAB_FINAL_DIR="$LABELS_OUTPUT_DIR"
    mkdir -p "$LAB_RAS_DIR" "$LAB_COREG_DIR" "$LABELS_OUTPUT_DIR"
fi

# Find image files
if [[ "$INPUT_DIR" == *"/"* ]]; then
    INPUT_PATH_FOR_FIND="${INPUT_DIR}"
else
    INPUT_PATH_FOR_FIND="${INPUT_DIR}/"
fi

if [ -n "$LABELS_DIR" ]; then
    ABS_INPUT_DIR=$(realpath "$INPUT_DIR")
    ABS_LABELS_DIR=$(realpath "$LABELS_DIR")
    
    if [[ "$ABS_LABELS_DIR" == "$ABS_INPUT_DIR"* ]]; then
        IMAGE_FIND_CMD="find \"$INPUT_PATH_FOR_FIND\" -type f -name \"*$IMG_EXT\" -not -path \"*${LABELS_DIR}*\""
    else
        IMAGE_FIND_CMD="find \"$INPUT_PATH_FOR_FIND\" -type f -name \"*$IMG_EXT\""
    fi
else
    IMAGE_FIND_CMD="find \"$INPUT_PATH_FOR_FIND\" -type f -name \"*$IMG_EXT\""
fi

IMAGE_FILES=$(eval $IMAGE_FIND_CMD)
[ -z "$IMAGE_FILES" ] && { echo "Error: No *$IMG_EXT files found in $INPUT_DIR"; exit 1; }

# Step 1: Image RAS conversion
for img_file in $IMAGE_FILES; do
    base_name=$(basename "$img_file")
    mri_convert "$img_file" "${IMG_RAS_DIR}/${base_name}" --out_orientation RAS
    [ $? -ne 0 ] && { echo "Error: RAS conversion failed for $img_file"; exit 1; }
done

# Step 1B: Label RAS conversion (if enabled)
if [ -n "$LABELS_DIR" ]; then
    LABEL_FILES=$(find "$LABELS_DIR" -type f -name "*$IMG_EXT")
    for lab_file in $LABEL_FILES; do
        lab_base_name=$(basename "$lab_file")
        mri_convert "$lab_file" "${LAB_RAS_DIR}/${lab_base_name}" --out_orientation RAS --resample_type nearest
        [ $? -ne 0 ] && { echo "Error: RAS conversion failed for label $lab_file"; exit 1; }
    done
fi

# Step 2: Image co-registration (if enabled)
if $DO_COREGISTER; then
    # Find reference scan
    if [ -n "$REFERENCE_STRING" ]; then
        for file in "${IMG_RAS_DIR}"/*"$IMG_EXT"; do
            base_name=$(basename "$file")
            if [[ "$base_name" == *"$REFERENCE_STRING"* ]]; then
                REFERENCE_SCAN="$file"
                break
            fi
        done
    fi
    
    # If not found, use highest resolution
    if [ -z "$REFERENCE_SCAN" ]; then
        SMALLEST_VOXEL_VOLUME=999999
        for file in "${IMG_RAS_DIR}"/*"$IMG_EXT"; do
            voxel_info=$(mri_info "$file" | grep "voxel sizes")
            x_dim=$(echo "$voxel_info" | sed -E 's/.*voxel sizes: ([0-9.]+).*/\1/')
            y_dim=$(echo "$voxel_info" | sed -E 's/.*voxel sizes: [0-9.]+, ([0-9.]+).*/\1/')
            z_dim=$(echo "$voxel_info" | sed -E 's/.*voxel sizes: [0-9.]+, [0-9.]+, ([0-9.]+).*/\1/')
            voxel_volume=$(echo "$x_dim * $y_dim * $z_dim" | bc -l)
            
            if (( $(echo "$voxel_volume < $SMALLEST_VOXEL_VOLUME" | bc -l) )); then
                SMALLEST_VOXEL_VOLUME=$voxel_volume
                REFERENCE_SCAN="$file"
            fi
        done
    fi
    
    REFERENCE_BASE=$(basename "$REFERENCE_SCAN")
    
    # Co-register all scans
    for file in "${IMG_RAS_DIR}"/*"$IMG_EXT"; do
        if [ "$file" != "$REFERENCE_SCAN" ]; then
            base_name=$(basename "$file")
            reg_file="${TEMP_DIR}/$(basename "$file" "$IMG_EXT")_to_$(basename "$REFERENCE_SCAN" "$IMG_EXT").lta"
            
            # Generate registration matrix
            mri_coreg --mov "$file" --ref "$REFERENCE_SCAN" --reg "$reg_file" --threads $THREADS
            [ $? -ne 0 ] && { echo "Error: Registration failed for $file"; exit 1; }
            
            # Apply registration
            mri_vol2vol --mov "$file" --reg "$reg_file" --o "${IMG_COREG_DIR}/${base_name}" --targ "$REFERENCE_SCAN"
            [ $? -ne 0 ] && { echo "Error: Volume transformation failed for $file"; exit 1; }
        else
            # Copy reference scan
            cp "$REFERENCE_SCAN" "${IMG_COREG_DIR}/$(basename "$REFERENCE_SCAN")"
        fi
    done
    
    IMG_FOR_NEXT_STEP="$IMG_COREG_DIR"
    
    # Co-register labels if needed
    if [ -n "$LABELS_DIR" ]; then
        for lab_file in "${LAB_RAS_DIR}"/*"$IMG_EXT"; do
            lab_base_name=$(basename "$lab_file")
            
            # Find corresponding reg file
            reg_file=""
            for img_file in "${IMG_RAS_DIR}"/*"$IMG_EXT"; do
                img_base_name=$(basename "$img_file")
                if [ "$img_base_name" = "$lab_base_name" ] && [ "$img_file" != "$REFERENCE_SCAN" ]; then
                    reg_file="${TEMP_DIR}/${img_base_name%.${IMG_EXT#.}}_to_$(basename "$REFERENCE_SCAN" "$IMG_EXT").lta"
                    break
                fi
            done
            
            if [ -f "$reg_file" ]; then
                # Apply registration
                mri_vol2vol --mov "$lab_file" --reg "$reg_file" --o "${LAB_COREG_DIR}/${lab_base_name}" --targ "$REFERENCE_SCAN" --interp nearest
                [ $? -ne 0 ] && { echo "Error: Label transformation failed for $lab_file"; exit 1; }
            else
                # Just copy
                cp "$lab_file" "${LAB_COREG_DIR}/$(basename "$lab_file")"
            fi
        done
        
        LAB_FOR_NEXT_STEP="$LAB_COREG_DIR"
    fi
else
    # Skip co-registration
    IMG_FOR_NEXT_STEP="$IMG_RAS_DIR"
    [ -n "$LABELS_DIR" ] && LAB_FOR_NEXT_STEP="$LAB_RAS_DIR"
fi

# Step 3: Skull stripping or defacing
if $DO_SKULL_STRIP; then
    if $DO_COREGISTER; then
        # Use reference image for segmentation
        reference_file="${IMG_COREG_DIR}/${REFERENCE_BASE}"
        reference_prefix="${REFERENCE_BASE%.${IMG_EXT#.}}"
        temp_seg="${TEMP_DIR}/${reference_prefix}_seg${IMG_EXT}"
        
        # Create segmentation
        mri_synthseg --i "$reference_file" --o "$temp_seg" --robust --threads $THREADS
        [ $? -ne 0 ] && { echo "Error: Segmentation failed for reference image"; exit 1; }
        [ ! -f "$temp_seg" ] && { echo "Error: Segmentation file not created"; exit 1; }
        
        # Apply to reference
        mri_mask "$reference_file" "$temp_seg" "${IMG_FINAL_DIR}/${REFERENCE_BASE}"
        [ $? -ne 0 ] && { echo "Error: Skull stripping failed for reference image"; exit 1; }
        
        # Copy reference label if exists
        if [ -n "$LABELS_DIR" ]; then
            ref_label="${LAB_FOR_NEXT_STEP}/${REFERENCE_BASE}"
            [ -f "$ref_label" ] && cp "$ref_label" "${LAB_FINAL_DIR}/$(basename "$ref_label")"
        fi
        
        # Apply to other images
        for file in "${IMG_FOR_NEXT_STEP}"/*"$IMG_EXT"; do
            base_name=$(basename "$file")
            if [ "$base_name" != "$REFERENCE_BASE" ]; then
                mri_mask "$file" "$temp_seg" "${IMG_FINAL_DIR}/${base_name}"
                [ $? -ne 0 ] && { echo "Error: Skull stripping failed for $file"; exit 1; }
            fi
        done
        
        # Copy all labels
        if [ -n "$LABELS_DIR" ]; then
            for lab_file in "${LAB_FOR_NEXT_STEP}"/*"$IMG_EXT"; do
                cp "$lab_file" "${LAB_FINAL_DIR}/$(basename "$lab_file")"
            done
        fi
    else
        # Process each independently
        for file in "${IMG_FOR_NEXT_STEP}"/*"$IMG_EXT"; do
            base_name=$(basename "$file")
            file_prefix="${base_name%.${IMG_EXT#.}}"
            temp_seg="${TEMP_DIR}/${file_prefix}_seg${IMG_EXT}"
            
            # Create segmentation
            mri_synthseg --i "$file" --o "$temp_seg" --robust --threads $THREADS
            [ $? -ne 0 ] && { echo "Error: Segmentation failed for $file"; exit 1; }
            
            # Apply mask
            mri_mask "$file" "$temp_seg" "${IMG_FINAL_DIR}/${base_name}"
            [ $? -ne 0 ] && { echo "Error: Skull stripping failed for $file"; exit 1; }
            
            # Copy label if exists
            if [ -n "$LABELS_DIR" ]; then
                lab_file="${LAB_FOR_NEXT_STEP}/${base_name}"
                [ -f "$lab_file" ] && cp "$lab_file" "${LAB_FINAL_DIR}/${base_name}"
            fi
        done
    fi
elif $DO_DEFACE; then
    # Create facemask dir
    FACEMASK_DIR="${TEMP_DIR}/facemask"
    mkdir -p "$FACEMASK_DIR"
    
    if $DO_COREGISTER; then
        # Use reference to create facemask
        reference_file="${IMG_COREG_DIR}/${REFERENCE_BASE}"
        facemask_file="${FACEMASK_DIR}/reference_facemask${IMG_EXT}"
        
        # Generate facemask
        mideface --i "$reference_file" --o "${IMG_FINAL_DIR}/${REFERENCE_BASE}" --facemask "$facemask_file" --threads $THREADS
        [ $? -ne 0 ] && { echo "Error: Facemask generation failed for reference"; exit 1; }
        [ ! -f "$facemask_file" ] && { echo "Error: Facemask file not created"; exit 1; }
        
        # Copy reference label if exists
        if [ -n "$LABELS_DIR" ]; then
            ref_label="${LAB_FOR_NEXT_STEP}/${REFERENCE_BASE}"
            [ -f "$ref_label" ] && cp "$ref_label" "${LAB_FINAL_DIR}/$(basename "$ref_label")"
        fi
        
        # Apply to other images
        for file in "${IMG_FOR_NEXT_STEP}"/*"$IMG_EXT"; do
            base_name=$(basename "$file")
            if [ "$base_name" != "$REFERENCE_BASE" ]; then
                # Get registration matrix
                reg_file="${TEMP_DIR}/$(basename "$file" "$IMG_EXT")_to_$(basename "$REFERENCE_SCAN" "$IMG_EXT").lta"
                original_file="${IMG_RAS_DIR}/${base_name}"
                
                # Create temporary directory for defaced images if it doesn't exist
                mkdir -p "${TEMP_DIR}/defaced"
                
                # Apply facemask to a temporary file with proper naming
                defaced_temp="${TEMP_DIR}/defaced/temp_${base_name}"
                mideface --apply "$original_file" "$facemask_file" "$reg_file" "$defaced_temp"
                [ $? -ne 0 ] && { echo "Error: Facemask application failed for $file"; exit 1; }
                
                # Apply registration to align the defaced image with reference
                mri_vol2vol --mov "$defaced_temp" --reg "$reg_file" --o "${IMG_FINAL_DIR}/${base_name}" --targ "$reference_file"
                [ $? -ne 0 ] && { echo "Error: Volume transformation after defacing failed for $file"; exit 1; }
            fi
        done
        
        # Copy all labels
        if [ -n "$LABELS_DIR" ]; then
            for lab_file in "${LAB_FOR_NEXT_STEP}"/*"$IMG_EXT"; do
                cp "$lab_file" "${LAB_FINAL_DIR}/$(basename "$lab_file")"
            done
        fi
    else
        # Process each independently
        for file in "${IMG_FOR_NEXT_STEP}"/*"$IMG_EXT"; do
            base_name=$(basename "$file")
            file_prefix="${base_name%.${IMG_EXT#.}}"
            facemask_file="${FACEMASK_DIR}/${file_prefix}_facemask${IMG_EXT}"
            
            # Generate facemask and deface
            mideface --i "$file" --o "${IMG_FINAL_DIR}/${base_name}" --facemask "$facemask_file" --threads $THREADS
            [ $? -ne 0 ] && { echo "Error: Defacing failed for $file"; exit 1; }
            
            # Copy label if exists
            if [ -n "$LABELS_DIR" ]; then
                lab_file="${LAB_FOR_NEXT_STEP}/${base_name}"
                [ -f "$lab_file" ] && cp "$lab_file" "${LAB_FINAL_DIR}/${base_name}"
            fi
        done
    fi
else
    # Skip both, just copy files
    for file in "${IMG_FOR_NEXT_STEP}"/*"$IMG_EXT"; do
        cp "$file" "${IMG_FINAL_DIR}/$(basename "$file")"
    done
fi

# Merge labels if requested
if [ -n "$LABELS_DIR" ] && $MERGE_LABELS; then
    MERGED_LABEL="${LAB_FINAL_DIR}/${MERGED_LABEL_NAME}${IMG_EXT}"
    BINARY_LABELS_DIR="${TEMP_DIR}/binary_labels"
    mkdir -p "$BINARY_LABELS_DIR"
    TEMP_MERGED="${TEMP_DIR}/temp_merged${IMG_EXT}"
    
    # Initialize with first label
    FIRST_LABEL=$(ls "${LAB_FINAL_DIR}"/*"$IMG_EXT" | head -n 1)
    cp "$FIRST_LABEL" "$MERGED_LABEL"
    mri_binarize --i "$MERGED_LABEL" --o "$MERGED_LABEL" --min 1 --binval 0
    cp "$MERGED_LABEL" "$TEMP_MERGED"
    
    # Merge all labels
    for lab_file in "${LAB_FINAL_DIR}"/*"$IMG_EXT"; do
        if [ "$lab_file" = "$MERGED_LABEL" ]; then continue; fi
        
        TEMP_BINARY="${BINARY_LABELS_DIR}/$(basename "$lab_file")"
        mri_binarize --i "$lab_file" --o "$TEMP_BINARY" --min 0.5 --binval 1 --binvalnot 0
        mri_binarize --i "$TEMP_BINARY" --o "$MERGED_LABEL" --min 0.5 --merge "$TEMP_MERGED" --binval 1
        cp "$MERGED_LABEL" "$TEMP_MERGED"
    done
    
    # Clean original labels if needed
    if $DO_CLEAN; then
        for lab_file in "${LAB_FINAL_DIR}"/*"$IMG_EXT"; do
            [ "$lab_file" != "$MERGED_LABEL" ] && rm "$lab_file"
        done
    fi
fi

# Clean mideface log files if DO_DEFACE is enabled and DO_CLEAN is true
if $DO_DEFACE && $DO_CLEAN; then
    echo "Cleaning mideface log files..."
    find "$IMG_FINAL_DIR" -name "*.mideface.log" -type f -delete
fi

# Clean up
$DO_CLEAN && rm -rf "$TEMP_DIR"

exit 0
