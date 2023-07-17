
def list_all_files(files_directory:str, allowed_extension:(str|None) = None, import_os_required:bool = False):
    if import_os_required:
        import os
    files = os.listdir(files_directory)
    if allowed_extension is not None and allowed_extension.strip() != "":
        allowed_extension = allowed_extension.strip()
        full_extension = allowed_extension if allowed_extension.startswith('.') else f'.{allowed_extension}'
        files = [f for f in filter(lambda fn: fn.endswith(full_extension ), files)]
    return files

if __name__ == "__main__":
    jsons = list_all_files("./resources/excluded/FCAB-BE", '.json', True)
    for file in jsons:
        print(file)
    print("done")
