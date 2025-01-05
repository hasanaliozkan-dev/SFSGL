"""
@author : hasanaliozkan-dev
"""




import multiprocessing
import subprocess
import json 


config = json.load(open("configuration.json"))


def run_file_gather():
    subprocess.run(["python3", "file_gather.py", config["gathered_folder_path"], ",".join(config["allowed_extension_to_gather"]),config["allow_multiple_upload"],config["add_ip_to_file"]])

def run_file_share():
    subprocess.run(["python3", "file_share.py", config["shared_folder_path"], ",".join(config["allowed_extension_to_share"])])

if __name__ == "__main__":
    gather_process = multiprocessing.Process(target=run_file_gather)
    share_process = multiprocessing.Process(target=run_file_share)

    gather_process.start()
    share_process.start()

    gather_process.join()
    share_process.join()

 
