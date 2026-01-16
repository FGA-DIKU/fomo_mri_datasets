import os
import argparse
import shutil
from os.path import join
from tqdm import tqdm
from batchgenerators.utilities.file_and_folder_operations import maybe_mkdir_p as ensure_dir_exists

# Excluded subjects list
EXCLUDED_SUBJECTS = { # USED in task3 of FOMO25
    "subject_0108", "subject_0182", "subject_0097", "subject_0805", "subject_0406",
    "subject_1216", "subject_0028", "subject_0085", "subject_0972", "subject_0511",
    "subject_0310", "subject_0538", "subject_1080", "subject_0166", "subject_0333",
    "subject_0850", "subject_0490", "subject_0319", "subject_0860", "subject_1073",
    "subject_1177", "subject_0703", "subject_0854", "subject_0819", "subject_0652",
    "subject_0920", "subject_1209", "subject_0596", "subject_0110", "subject_0200",
    "subject_1301", "subject_0552", "subject_0160", "subject_0981", "subject_0023",
    "subject_0517", "subject_0757", "subject_0105", "subject_0994", "subject_1315",
    "subject_0006", "subject_0322", "subject_0262", "subject_0207", "subject_0210",
    "subject_1233", "subject_1235", "subject_0358", "subject_1179", "subject_0493",
    "subject_0764", "subject_0193", "subject_0875", "subject_0036", "subject_0111",
    "subject_0329", "subject_1127", "subject_1157", "subject_0895", "subject_1034",
    "subject_0126", "subject_0870", "subject_0885", "subject_1040", "subject_1048",
    "subject_1244", "subject_1084", "subject_1108", "subject_1155", "subject_0771",
    "subject_0962", "subject_0301", "subject_0766", "subject_1069", "subject_0012",
    "subject_0276", "subject_0121", "subject_0323", "subject_0665", "subject_0205",
    "subject_1276", "subject_1263", "subject_0199", "subject_0198", "subject_0817",
    "subject_1032", "subject_0815", "subject_0654", "subject_1261", "subject_1063",
    "subject_1249", "subject_0021", "subject_1078", "subject_0408", "subject_0731",
    "subject_1236", "subject_0907", "subject_0435", "subject_1258", "subject_0599",
    "subject_0556", "subject_0202", "subject_0755", "subject_0169", "subject_0123",
    "subject_0752", "subject_1367", "subject_0861", "subject_0229", "subject_1214",
    "subject_1143", "subject_0500", "subject_0099", "subject_0073", "subject_0371",
    "subject_0796", "subject_0008", "subject_1298", "subject_0501", "subject_0781",
    "subject_1175", "subject_1292", "subject_0184", "subject_1189", "subject_0896",
    "subject_0456", "subject_1299", "subject_0245", "subject_1272", "subject_1374",
    "subject_1141", "subject_0212", "subject_0770", "subject_1378", "subject_0046",
    "subject_1190", "subject_1008", "subject_1234", "subject_0221", "subject_0491",
    "subject_0965", "subject_0884", "subject_1201", "subject_0899", "subject_0448",
    "subject_0220", "subject_0324", "subject_0722", "subject_0970", "subject_0561",
    "subject_1355", "subject_1135", "subject_1182", "subject_0010", "subject_0742",
    "subject_1238", "subject_1256", "subject_0589", "subject_0777", "subject_0506",
    "subject_0832", "subject_0911", "subject_0648", "subject_0793", "subject_0086",
    "subject_1134", "subject_1377", "subject_0275", "subject_1133", "subject_0508",
    "subject_0394", "subject_0146", "subject_0057", "subject_0681", "subject_0725",
    "subject_0859", "subject_0626", "subject_0247", "subject_1259", "subject_0320",
    "subject_0886", "subject_0384", "subject_0835", "subject_1165", "subject_0024",
    "subject_0482", "subject_1254", "subject_0916", "subject_1172", "subject_1199",
    "subject_0660", "subject_1120", "subject_1278", "subject_0084", "subject_0441",
    "subject_0402", "subject_0607", "subject_0285", "subject_0636", "subject_0868"
}


def main(source_path, dest_path, num_workers=12):
    subjects_dir = source_path
    if os.path.exists(dest_path):
        shutil.rmtree(dest_path)
    ensure_dir_exists(dest_path)
    
    # Get all subject directories
    all_subjects = sorted([d for d in os.listdir(subjects_dir) 
                          if os.path.isdir(join(subjects_dir, d))])
    
    total_subjects = 0
    total_vols = 0
    
    for subject_id in tqdm(all_subjects, desc="Subjects"):
        # Skip excluded subjects
        if subject_id in EXCLUDED_SUBJECTS:
            continue
            
        total_subjects += 1
        subject_path = join(subjects_dir, subject_id)
        
        # Find session directories
        sessions = sorted([s for s in os.listdir(subject_path) 
                          if os.path.isdir(join(subject_path, s))])
        
        for session in sessions:
            session_path = join(subject_path, session)
            
            # Get all .nii files in session
            nii_files = [f for f in os.listdir(session_path) 
                        if f.endswith(".nii.gz")]
            
            if nii_files:
                # Create output directory
                output_dir = join(dest_path, subject_id, "session_1")
                ensure_dir_exists(output_dir)
                
                # Copy all nii files
                for nii_file in nii_files:
                    src = join(session_path, nii_file)
                    dst = join(output_dir, nii_file)
                    shutil.copy2(src, dst)
                    total_vols += 1
    
    print(f"Moved {total_vols} volumes from {total_subjects} subjects to {dest_path}")
    
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process data from MGH_WILD dataset")
    parser.add_argument(
        "--input",
        type=str,
        required=True,
        help="Path to MGH_WILD data directory"
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
