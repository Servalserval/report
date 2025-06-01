import os

def check_os_list(filedir, filename):
    nested_dir = filedir.split("/")
    current_dir = "./"
    for i in nested_dir:
        if i == "":
            continue
        files_in_dir = os.listdir(path = current_dir)
        if i not in files_in_dir and i != ".":
            print(i)
            os.mkdir(f"{current_dir}/{i}")
        current_dir += f"{i}/"
        
    
    files_in_dir = os.listdir(path = current_dir)
    return filename in files_in_dir
    
    