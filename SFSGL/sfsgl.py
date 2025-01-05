import multiprocessing
import subprocess
class SFSGL():

    def __init__(self, **kwargs):
        self._init_kwargs = kwargs
        self._shared_folder_path = kwargs.get("shared_folder_path", "shared")
        self._gathered_folder_path = kwargs.get("gathered_folder_path", "gathered")
        self._allowed_extension_to_gather = kwargs.get("allowed_extension_to_gather", ["py","zip"])
        self._allowed_extension_to_share = kwargs.get("allowed_extension_to_share", ["py","zip","txt"])
        self._allow_multiple_upload = kwargs.get("allow_multiple_upload", "False")
        self._add_ip_to_file = kwargs.get("add_ip_to_file", "True")
        self._shared_port = kwargs.get("shared_port", 5001)
        self._gathered_port = kwargs.get("gathered_port", 5002)
        
    
    def run_file_gather(self):
        subprocess.run(["python3", "file_gather.py", self._gathered_folder_path, ",".join(self._allowed_extension_to_gather),self._allow_multiple_upload,self._add_ip_to_file])

    def run_file_share(self):
        subprocess.run(["python3", "file_share.py", self._shared_folder_path, ",".join(self._allowed_extension_to_share)])


 
        
    
    def start(self):
        gather_process = multiprocessing.Process(target=self.run_file_gather)
        share_process = multiprocessing.Process(target=self.run_file_share)
        gather_process.start()
        share_process.start()
        gather_process.join()
        share_process.join()
        return self._init_kwargs