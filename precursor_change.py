import os

# Directory containing the profile files
directory = 'X:/ANSYS results/triple_jet/MIXED LBE/precursor/inlets/test'
left = True  # if false it is right

# Adjustment factor
h = 0.015
adjustment_factor = 3.5 * h
counter = 1

# Iterate over files in the directory
for filename in os.listdir(directory):
    if filename.startswith("Profile_cold_left_000001.prof"):
        filepath = os.path.join(directory, filename)
        with open(filepath, 'r+') as file:
            lines = file.readlines()
            for line in lines:
                if counter >= 5405 and counter <= 10804:
                    value = float(line.strip())
                    if value < h:
                        # file.seek(0)
                        new_value = value + adjustment_factor
                        file.write(f"{new_value}\n")  # Write the adjusted value back to the file
                        # file.truncate()
                    else:
                        # file.seek(0)
                        file.write(line)
                        # file.truncate()

                else:
                    # file.seek(0)
                    file.write(line)  # Write the original line back to the file
                    # file.truncate()
                counter += 1

                # if line.strip() == "(y":
                #     adjusting = True
                #     modified_lines.append(line)
                # elif adjusting and not line.strip().startswith("("):
                #     # Adjust Y data
                #     modified_lines.append(str(float(line.strip()) + adjustment_factor) + "\n")
                # elif adjusting and line.strip().startswith("("):
                #     adjusting = False
                #     modified_lines.append(line)
                # else:
                #     modified_lines.append(line)

        # Write the modified content back to the file
        # with open(filepath, 'w') as file:
        #     file.writelines(modified_lines)

print("Adjustment complete.")
