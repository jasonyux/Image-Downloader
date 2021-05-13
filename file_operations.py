import os, shutil, json, logging

def remove_dir(dir_path):
    try:
        shutil.rmtree(dir_path)
    except FileNotFoundError:
        pass
    return

def remove_file(file_path):
    if os.path.exists(file_path):
        os.remove(file_path)
    return

def flush_json_to_file(openfile, json_object):
    try:
        openfile.seek(0)
        openfile.write(json.dumps(json_object, indent=4))
        openfile.truncate()
    except Exception:
        logging.warn("Failed to flush json data to file at flush_json_to_file()")
        return -1
    return 1