import multiprocessing
import subprocess

def run_file_gather():
    subprocess.run(["python3", "file_gather.py", "uploads", "py,zip"])

def run_file_share():
    subprocess.run(["python3", "file_share.py", "shared"])

if __name__ == "__main__":
    gather_process = multiprocessing.Process(target=run_file_gather)
    share_process = multiprocessing.Process(target=run_file_share)

    gather_process.start()
    share_process.start()

    gather_process.join()
    share_process.join()

 
