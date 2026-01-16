#!/bin/bash
set -e

# Usage function
usage() {
    echo "Usage: $0 -i <input_dir> -o <output_dir> [-t <threads>] [-f <freesurfer_home>]"
    echo ""
    echo "Process NKI dataset with preprocessing pipeline"
    echo ""
    echo "Options:"
    echo "  -i: Input root directory containing NKI subject/session folders"
    echo "  -o: Output root directory for preprocessed NKI data"
    echo "  -t: Number of threads (default: 4)"
    echo "  -f: FreeSurfer home directory (default: \$FREESURFER_HOME)"
    echo "  -h: Show this help message"
    echo ""
    echo "Example:"
    echo "  $0 -i /path/to/nki_tmp -o /path/to/nki_preprocessed -t 4"
    exit 1
}

# Default values
THREADS=4
FREESURFER_HOME="${FREESURFER_HOME:-}"
EXT="nii.gz"

# Parse command line arguments
while getopts "i:o:t:f:h" opt; do
    case $opt in
        i) INPUT_ROOT="$OPTARG" ;;
        o) OUTPUT_ROOT="$OPTARG" ;;
        t) THREADS="$OPTARG" ;;
        f) FREESURFER_HOME="$OPTARG" ;;
        h) usage ;;
        \?) echo "Invalid option: -$OPTARG"; usage ;;
        :) echo "Option -$OPTARG requires an argument"; usage ;;
    esac
done

# Check required arguments
if [ -z "$INPUT_ROOT" ] || [ -z "$OUTPUT_ROOT" ]; then
    echo "Error: Input and output directories are required"
    usage
fi

# Check if input directory exists
if [ ! -d "$INPUT_ROOT" ]; then
    echo "Error: Input directory does not exist: $INPUT_ROOT"
    exit 1
fi

# Check FreeSurfer
if [ -z "$FREESURFER_HOME" ]; then
    echo "Error: FreeSurfer home directory not specified. Use -f flag or set \$FREESURFER_HOME"
    exit 1
fi

if [ ! -d "$FREESURFER_HOME" ]; then
    echo "Error: FreeSurfer directory does not exist: $FREESURFER_HOME"
    exit 1
fi

if [ ! -f "$FREESURFER_HOME/SetUpFreeSurfer.sh" ]; then
    echo "Error: FreeSurfer setup script not found: $FREESURFER_HOME/SetUpFreeSurfer.sh"
    exit 1
fi

# Set up FreeSurfer
echo "=================================================="
echo "NKI Dataset Preprocessing Pipeline"
echo "=================================================="
echo "Setting up FreeSurfer from: $FREESURFER_HOME"
export FREESURFER_HOME
source "$FREESURFER_HOME/SetUpFreeSurfer.sh"

# Set number of threads
export OMP_NUM_THREADS=$THREADS

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PREPROCESS_SCRIPT="${SCRIPT_DIR}/pre_process.sh"

# Check if preprocessing script exists
if [ ! -f "$PREPROCESS_SCRIPT" ]; then
    echo "Error: Preprocessing script not found: $PREPROCESS_SCRIPT"
    echo "Expected location: ${SCRIPT_DIR}/pre_process.sh"
    exit 1
fi

# Create output root directory
mkdir -p "$OUTPUT_ROOT"

# Get all NKI session directories (2 levels deep: subject/session)
echo "Scanning for NKI sessions in: $INPUT_ROOT"
SESSIONS=($(find "$INPUT_ROOT" -mindepth 2 -maxdepth 2 -type d | sort))

# Check if we have sessions
if [ ${#SESSIONS[@]} -eq 0 ]; then
    echo "Error: No NKI sessions found in $INPUT_ROOT"
    echo "Expected structure: $INPUT_ROOT/subject_*/session_*/"
    exit 1
fi

echo "Found ${#SESSIONS[@]} NKI sessions to process"
echo "Using $THREADS threads per session"
echo "=================================================="

# Process each session
PROCESSED=0
SKIPPED=0
FAILED=0

for SESSION_DIR in "${SESSIONS[@]}"; do
    echo "Processing NKI session: $SESSION_DIR"
    
    # Prepare output directory
    REL_PATH="${SESSION_DIR#$INPUT_ROOT/}"
    OUTPUT_DIR="${OUTPUT_ROOT}/${REL_PATH}"
    mkdir -p "$OUTPUT_DIR"
    
    # Count NIFTI files in the session and output directories
    SESSION_NIFTI_COUNT=$(find "$SESSION_DIR" -type f -name "*.$EXT" | wc -l)
    OUTPUT_NIFTI_COUNT=$(find "$OUTPUT_DIR" -maxdepth 1 -type f -name "*.$EXT" 2>/dev/null | wc -l)
    
    # Skip if output has the same number of NIFTI files as session directory
    if [ $OUTPUT_NIFTI_COUNT -gt 0 ] && [ $OUTPUT_NIFTI_COUNT -eq $SESSION_NIFTI_COUNT ]; then
        echo "  → Skipping - already processed ($OUTPUT_NIFTI_COUNT files match)"
        ((SKIPPED++))
        continue
    fi
    
    # Run the preprocessing script
    if bash "$PREPROCESS_SCRIPT" "$SESSION_DIR" "$OUTPUT_DIR" --extension ".$EXT" --no-skull-strip --threads $THREADS; then
        echo "  → Success"
        ((PROCESSED++))
    else
        echo "  → Failed"
        ((FAILED++))
    fi
    
    echo "--------------------------------------------------"
done

# Print summary
echo "=================================================="
echo "NKI Processing Complete!"
echo "=================================================="
echo "Processed: $PROCESSED sessions"
echo "Skipped: $SKIPPED sessions"
echo "Failed: $FAILED sessions"
echo "Total sessions: ${#SESSIONS[@]}"
echo "=================================================="

exit 0
