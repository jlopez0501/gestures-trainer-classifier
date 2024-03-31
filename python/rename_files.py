import os

def rename_files(directory):
    # Iterate over each file in the directory
    for filename in os.listdir(directory):
        if filename.startswith("shoulder_press") and filename.endswith(".csv"):
            # Split the filename to get the number
            num = filename.split("shoulder_press")[1].split(".csv")[0]
            new_filename = f"shoulder_press_3_10_shoulder_press{num}.csv"
            # Rename the file
            os.rename(os.path.join(directory, filename), os.path.join(directory, new_filename))
            print(f"Renamed {filename} to {new_filename}")

# Specify the directory containing the files
directory = "../DMP_9D_ACCEL_Logs/shoulder_press_3_10/"  # Change this to the directory containing your files if they are not in the current directory

rename_files(directory)

