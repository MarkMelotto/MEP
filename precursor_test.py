import os
import shutil

# Directory containing the profile files
directory = 'X:/ANSYS results/triple_jet/MIXED LBE/precursor/inlets/test'
left = True  # if false it is right

# Adjustment factor
h = 0.015
adjustment_factor = 3.5 * h
counter = 1

# Iterate over files in the directory
for filename in os.listdir(directory):
    if filename.startswith("Profile_cold_left_0"):
        filepath = os.path.join(directory, filename)
        # Make a copy of the original file
        original_filepath = filepath + ".original"
        shutil.copyfile(filepath, original_filepath)

        with open(filepath, 'r') as file:
            lines = file.readlines()

        # Create a temporary file to store modified content
        temp_filepath = filepath + ".tmp"
        with open(temp_filepath, 'w') as temp_file:
            for line in lines:
                if counter >= 5405 and counter <= 10804:
                    value = float(line.strip())
                    if value < h:
                        new_value = value + adjustment_factor
                        temp_file.write(f"{new_value}\n")  # Write the adjusted value to the temporary file
                    else:
                        temp_file.write(line)  # Write the original line to the temporary file
                else:
                    temp_file.write(line)  # Write the original line to the temporary file
                counter += 1

        # Replace the original file with the temporary file
        shutil.move(temp_filepath, filepath)

print("Adjustment complete.")
