import os


def create_recursive_folders(folder_path, create_path):
    "got to folder_path and create create_path folders"
    current_path = os.getcwd()
    os.chdir(folder_path)
    _path_array = create_path.split("/")

    for i in range(1, len(_path_array)):
        _sub_path = "/".join(_path_array[:i])
        if not os.path.exists(_sub_path):
            os.mkdir(_sub_path)
            print(f"Creating folder: {_sub_path}")
        else:
            print(f"Folder already exists: {_sub_path}")
    os.chdir(current_path)
    return
    
if __name__ == "__main__":
    create_recursive_folders("../src", "common/python/lib/python3.11/site-packages/hii")
