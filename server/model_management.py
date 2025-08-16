import os

def deleteOldModel():
    # Path to your folder
    indexTypes = ["ndvi", "ndmi"]
    for indexType in indexTypes:
        folder_path = f"models/{indexType}"

        # File to delete
        file_name = "my_model.h5"

        # Full path
        file_path = os.path.join(folder_path, file_name)

        # Check if file exists before deleting
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"{file_name} deleted successfully.")
        else:
            print(f"{file_name} does not exist in {folder_path}.")