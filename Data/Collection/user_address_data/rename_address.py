import os

# Path to the folder for address json files
folder_path = r"...\address_data"  # Replace with the actual folder path

# Loop through all files in the folder
for filename in os.listdir(folder_path):
    # Only rename files that start with "buyer_" and end with ".json"
    if filename.startswith("buyer_") and filename.endswith(".json"):
        # New filename with "buyer_" removed
        new_filename = filename.replace("buyer_", "", 1)
        # Full paths for renaming
        src = os.path.join(folder_path, filename)
        dst = os.path.join(folder_path, new_filename)
        # Rename the file
        os.rename(src, dst)
        print(f"Renamed: {filename} -> {new_filename}")
