#@author: Hasan Ali Özkan


import argparse
import multiprocessing
import os
import re
import threading
import unicodedata

from flask import Flask, render_template, request, send_from_directory

# Device names Windows refuses as file names, whatever the extension
WINDOWS_RESERVED_NAMES = {"CON", "PRN", "AUX", "NUL", *(f"COM{i}" for i in range(1, 10)), *(f"LPT{i}" for i in range(1, 10))}


def as_bool(value):
    """Accepts real booleans as well as the "True"/"False" strings older versions required."""
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"true", "1", "yes"}


def safe_filename(filename):
    """Strips folders and unsafe characters but keeps non-ASCII letters, so 'çalışma.py' stays 'çalışma.py'."""
    name = unicodedata.normalize("NFC", filename).replace("\\", "/").rsplit("/", 1)[-1]
    name = re.sub(r"[^\w.\-]", "_", name).lstrip(".").rstrip(".")
    if name.split(".")[0].upper() in WINDOWS_RESERVED_NAMES:
        name = f"_{name}"
    return name


def normalize_extensions(extensions):
    return {ext.strip().lower().lstrip(".") for ext in extensions}


class SFSGL():

    def __init__(self, **kwargs):
        self._init_kwargs = kwargs
        self._shared_folder_path = kwargs.get("shared_folder_path", "shared")
        self._gathered_folder_path = kwargs.get("gathered_folder_path", "gathered")
        self._allowed_extension_to_gather = kwargs.get("allowed_extension_to_gather", ["py","zip"])
        self._allowed_extension_to_share = kwargs.get("allowed_extension_to_share", ["py","zip","txt"])
        self._allow_multiple_upload = kwargs.get("allow_multiple_upload", False)
        self._add_ip_to_file = kwargs.get("add_ip_to_file", True)
        self._max_upload_size_mb = kwargs.get("max_upload_size_mb", 50)
        self._shared_port = kwargs.get("shared_port", 5001)
        self._gathered_port = kwargs.get("gathered_port", 5002)

    def start(self):
        print(f"Sharing files from:   {os.path.abspath(self._shared_folder_path)} (port {self._shared_port})")
        print(f"Saving uploads to:    {os.path.abspath(self._gathered_folder_path)} (port {self._gathered_port})")
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
            max_upload_size_mb=self._max_upload_size_mb,
            port=self._gathered_port
        )
        gather_app.run()

    def run_file_share(self):
        share_app = FileShare(
            shared_folder_path=self._shared_folder_path,
            allowed_extension_to_share=self._allowed_extension_to_share,
            port=self._shared_port
        )
        share_app.run()


class FileGather():
    def __init__(self, **kwargs):
        self._init_kwargs = kwargs
        self._gathered_folder_path = kwargs.get("gathered_folder_path", "gathered")
        self._allowed_extension_to_gather = kwargs.get("allowed_extension_to_gather", ["py","zip"])
        self._allow_multiple_upload = kwargs.get("allow_multiple_upload", False)
        self._add_ip_to_file = kwargs.get("add_ip_to_file", True)
        self._max_upload_size_mb = kwargs.get("max_upload_size_mb", 50)
        self._port = kwargs.get("port", 5002)

        self.app = Flask(__name__, static_folder='static', template_folder='templates')
        self.UPLOAD_FOLDER = os.path.abspath(self._gathered_folder_path)
        self.ALLOWED_EXTENSIONS = normalize_extensions(self._allowed_extension_to_gather)
        self.MULTIPLE_UPLOAD = as_bool(self._allow_multiple_upload)
        self.ADD_IP_TO_FILE = as_bool(self._add_ip_to_file)
        self.uploaded_ips = {}
        self._lock = threading.Lock()

        self.app.config['UPLOAD_FOLDER'] = self.UPLOAD_FOLDER
        if self._max_upload_size_mb:
            self.app.config['MAX_CONTENT_LENGTH'] = int(float(self._max_upload_size_mb) * 1024 * 1024)
        os.makedirs(self.UPLOAD_FOLDER, exist_ok=True)

        self.app.add_url_rule('/', 'upload_file', self.upload_file, methods=['GET', 'POST'])
        self.app.register_error_handler(413, self.upload_too_large)

    def allowed_file(self, filename):
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in self.ALLOWED_EXTENSIONS

    def render(self, **context):
        allowed_file_str = ', '.join(sorted(self.ALLOWED_EXTENSIONS))
        return render_template("file_gather.html", allowed_file=allowed_file_str, multiple=self.MULTIPLE_UPLOAD, **context)

    def upload_file(self):
        client_ip = request.remote_addr or "unknown"
        one_per_ip = "You can only upload one file per IP address."

        if not self.MULTIPLE_UPLOAD and self.uploaded_ips.get(client_ip):
            return self.render(error_message=one_per_ip)
        if request.method != 'POST':
            return self.render()

        files = [file for file in request.files.getlist('file') if file.filename]
        if not files:
            return self.render(error_message="No selected file")
        if not self.MULTIPLE_UPLOAD and len(files) > 1:
            return self.render(error_message="Please select only one file.")
        names = [safe_filename(file.filename) for file in files]
        rejected = [file.filename for file, name in zip(files, names) if not self.allowed_file(name)]
        if rejected:
            allowed = ', '.join(sorted(self.ALLOWED_EXTENSIONS))
            return self.render(error_message=f"File type not allowed: {', '.join(rejected)}. Allowed file types: {allowed}")

        with self._lock:
            # Checked again under the lock so two simultaneous uploads from one IP can't both get through
            if not self.MULTIPLE_UPLOAD and self.uploaded_ips.get(client_ip):
                return self.render(error_message=one_per_ip)
            self.uploaded_ips[client_ip] = True
        try:
            saved = [self.save(file, name, client_ip) for file, name in zip(files, names)]
        except Exception:
            self.uploaded_ips[client_ip] = False  # let the student try again
            raise
        return self.render(success_message=f"File uploaded successfully: {', '.join(saved)}")

    def save(self, file, name, client_ip):
        """Saves the upload without ever overwriting: a taken name gets a _1, _2, ... suffix."""
        if self.ADD_IP_TO_FILE:
            name = safe_filename(f"{client_ip}_{name}")
        stem, ext = os.path.splitext(name)
        candidate, counter = name, 1
        while True:
            try:
                # "xb" fails when the file exists, so concurrent uploads can't clobber each other
                with open(os.path.join(self.UPLOAD_FOLDER, candidate), "xb") as out:
                    file.save(out)
                return candidate
            except FileExistsError:
                candidate, counter = f"{stem}_{counter}{ext}", counter + 1

    def upload_too_large(self, error):
        return self.render(error_message=f"File is too large. The limit is {self._max_upload_size_mb} MB."), 413

    def run(self):
        self.app.run(host='0.0.0.0',port=self._port)


class FileShare():
    def __init__(self,**kwargs):
        self.app = Flask(__name__, static_folder='static', template_folder='templates')
        self._shared_folder_path = os.path.abspath(kwargs.get("shared_folder_path", "shared"))
        self._allowed_extension_to_share = normalize_extensions(kwargs.get("allowed_extension_to_share", ["py","zip","txt"]))
        self._port = kwargs.get("port", 5001)
        os.makedirs(self._shared_folder_path, exist_ok=True)

        self.app.add_url_rule('/', 'index', self.index)
        self.app.add_url_rule('/download/<filename>', 'download_file', self.download_file)

    def allowed_file(self, filename):
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in self._allowed_extension_to_share

    def index(self):
        try:
            files = sorted(
                f for f in os.listdir(self._shared_folder_path)
                if self.allowed_file(f) and os.path.isfile(os.path.join(self._shared_folder_path, f))
            )
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


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="sfsgl",
        description="Share files with students and collect their submissions over the local network.",
    )
    parser.add_argument("--shared", default="shared", help="folder whose files students can download (default: ./shared)")
    parser.add_argument("--gathered", default="gathered", help="folder where uploads are saved (default: ./gathered)")
    parser.add_argument("--gather-ext", nargs="+", default=["py", "zip"], metavar="EXT",
                        help="file types students may upload (default: py zip)")
    parser.add_argument("--share-ext", nargs="+", default=["py", "zip", "txt"], metavar="EXT",
                        help="file types listed for download (default: py zip txt)")
    parser.add_argument("--allow-multiple-upload", action="store_true",
                        help="let a student upload more than one file (default: one file per IP address)")
    parser.add_argument("--no-ip-in-filename", action="store_true",
                        help="don't prefix saved files with the uploader's IP address")
    parser.add_argument("--max-upload-mb", type=float, default=50, help="upload size limit in MB, 0 for none (default: 50)")
    parser.add_argument("--share-port", type=int, default=5001, help="port of the download page (default: 5001)")
    parser.add_argument("--gather-port", type=int, default=5002, help="port of the upload page (default: 5002)")
    args = parser.parse_args(argv)

    session = SFSGL(
        shared_folder_path=args.shared,
        gathered_folder_path=args.gathered,
        allowed_extension_to_gather=args.gather_ext,
        allowed_extension_to_share=args.share_ext,
        allow_multiple_upload=args.allow_multiple_upload,
        add_ip_to_file=not args.no_ip_in_filename,
        max_upload_size_mb=args.max_upload_mb,
        shared_port=args.share_port,
        gathered_port=args.gather_port,
    )
    return session.start()

if __name__ == '__main__':
    main()
