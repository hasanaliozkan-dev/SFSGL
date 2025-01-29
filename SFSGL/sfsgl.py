#@author: Hasan Ali Özkan


import multiprocessing
from flask import Flask, request, render_template, send_from_directory
import os
import werkzeug.utils

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
        
    def start(self):
        gather_process = multiprocessing.Process(target=self.run_file_gather)
        share_process = multiprocessing.Process(target=self.run_file_share)
        gather_process.start()
        share_process.start()
        gather_process.join()
        share_process.join()
        return self._init_kwargs

    def run_file_gather(self):
        gather_app = FileGather(
            gathered_folder_path=self._gathered_folder_path,
            allowed_extension_to_gather=self._allowed_extension_to_gather,
            allow_multiple_upload=self._allow_multiple_upload,
            add_ip_to_file=self._add_ip_to_file,
            port=self._gathered_port
        )
        gather_app.run()

    def run_file_share(self):
        share_app = FileShare(
            folder_name=self._shared_folder_path,
            allowed_extensions=self._allowed_extension_to_share,
            port=self._shared_port
        )
        share_app.run()


class FileGather():
    def __init__(self, **kwargs):
        self._init_kwargs = kwargs
        self._gathered_folder_path = kwargs.get("gathered_folder_path", "shared")
        self._allowed_extension_to_gather = kwargs.get("allowed_extension_to_gather", ["py","zip"])
        self._allow_multiple_upload = kwargs.get("allow_multiple_upload", "False")
        self._add_ip_to_file = kwargs.get("add_ip_to_file", "True")
        self._port = kwargs.get("port", 5002)
        
        self.app = Flask(__name__, static_folder='static', template_folder='templates')
        self.UPLOAD_FOLDER = self._gathered_folder_path
        self.ALLOWED_EXTENSIONS = set(self._allowed_extension_to_gather)
        self.MULTIPLE_UPLOAD = self._allow_multiple_upload.lower() == 'true'
        self.uploaded_ips = {}

        self.app.config['UPLOAD_FOLDER'] = self.UPLOAD_FOLDER
        os.makedirs(self.UPLOAD_FOLDER, exist_ok=True)

        self.app.add_url_rule('/', 'upload_file', self.upload_file, methods=['GET', 'POST'])

    def allowed_file(self, filename):
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in self.ALLOWED_EXTENSIONS

    def upload_file(self):
        error_message = None
        client_ip = request.remote_addr 
        allowed_file_str = ', '.join(self.ALLOWED_EXTENSIONS) 

        # Check if the client IP has already uploaded a file
        if not self.MULTIPLE_UPLOAD and client_ip in self.uploaded_ips and self.uploaded_ips[client_ip]:
            error_message = "You can only upload one file per IP address."
            return render_template("file_gather.html", error_message=error_message, allowed_file=allowed_file_str)

        if request.method == 'POST':
            if 'file' not in request.files:
                error_message = "No file part"
                return render_template("file_gather.html", error_message=error_message, allowed_file=allowed_file_str)
            file = request.files['file']
            if file.filename == '':
                error_message = "No selected file"
                return render_template("file_gather.html", error_message=error_message, allowed_file=allowed_file_str)
            if file and self.allowed_file(file.filename):
                filename = werkzeug.utils.secure_filename(file.filename)
                file.save(os.path.join(self.app.config['UPLOAD_FOLDER'], filename))
                self.uploaded_ips[client_ip] = True
                return render_template("file_gather.html", success_message="File uploaded successfully.", allowed_file=allowed_file_str)
        return render_template("file_gather.html", allowed_file=allowed_file_str)

    def run(self):
        self.app.run(host='0.0.0.0',port=self._port)


class FileShare():
    def __init__(self,**kwargs):
        self.app = Flask(__name__, static_folder='static', template_folder='templates')
        self._shared_folder_path = kwargs.get("shared_folder_path", "shared")
        self._allowed_extension_to_share = kwargs.get("allowed_extension_to_share", ["py","zip","txt"])
        self._port = kwargs.get("port", 5001)

        self.app.add_url_rule('/', 'index', self.index)
        self.app.add_url_rule('/download/<filename>', 'download_file', self.download_file)

    def allowed_file(self, filename):
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in self._allowed_extension_to_share

    def index(self):
        try:
            files = [f for f in os.listdir(self._shared_folder_path) if self.allowed_file(f)]
            return render_template('file_share.html', files=files)
        except Exception as e:
            self.app.logger.error(f"Error rendering template: {e}")
            return "Internal Server Error", 500

    def download_file(self, filename):
        if self.allowed_file(filename) and os.path.isfile(os.path.join(self._shared_folder_path, filename)):
            return send_from_directory(self._shared_folder_path, filename, as_attachment=True)
        else:
            return "File not found or invalid file type", 404

    def run(self):
        self.app.run(host='0.0.0.0', port=self._port)


if __name__ == '__main__':
    a = SFSGL(shared_folder_path="shared", gathered_folder_path="gathered", allowed_extension_to_gather=["py","zip"], allowed_extension_to_share=["py","zip","txt"], allow_multiple_upload="False", add_ip_to_file="True", shared_port=5001, gathered_port=5002)
    a.start()