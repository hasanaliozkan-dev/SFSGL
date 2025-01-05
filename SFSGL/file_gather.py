"""
@author : hasanaliozkan-dev
"""

from flask import Flask, request, render_template
import os
import werkzeug.utils
import sys

app = Flask(__name__)

UPLOAD_FOLDER = sys.argv[1]
ALLOWED_EXTENSIONS = sys.argv[2].split(',')
MULTIPLE_UPLOAD = sys.argv[3] == "True" 
ADD_IP_TO_FILENAME = sys.argv[4] == "True"


app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

uploaded_ips = {}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    error_message = None
    client_ip = request.remote_addr 
    allowed_file_str = ', '.join(ALLOWED_EXTENSIONS) 

    
    # Check if the client IP has already uploaded a file
    if not MULTIPLE_UPLOAD and client_ip in uploaded_ips and uploaded_ips[client_ip]:
        error_message = "You can only upload one file per IP address."
        return render_template("file_gather.html", error_message=error_message,allowed_file=allowed_file_str)

    if request.method == 'POST':
        # Check if the 'files' part is in the request
        if 'files' not in request.files:
            error_message = "No file part"
            return render_template("file_gather.html", error_message=error_message,allowed_file=allowed_file_str)

        files = request.files.getlist('files')  # Get the list of files
        
        if not files:
            error_message = "No selected file"
            return render_template("file_gather.html", error_message=error_message,allowed_file=allowed_file_str)


        for file in files:
            if file and allowed_file(file.filename):
                filename = werkzeug.utils.secure_filename(file.filename)
                name, extension = os.path.splitext(filename)
                if ADD_IP_TO_FILENAME:

                    new_filename = f"{name}_{client_ip}{extension}"
                else:
                    new_filename = filename
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], new_filename))
            else:
                error_message = f"File type not allowed. Please upload only {', '.join(ALLOWED_EXTENSIONS)} files."
                return render_template("file_gather.html", error_message=error_message,allowed_file=allowed_file_str)

        if not MULTIPLE_UPLOAD:
            uploaded_ips[client_ip] = True
        error_message = f"File(s) uploaded successfully."
        return render_template("file_gather.html", error_message=error_message,allowed_file=allowed_file_str)

    
    return render_template("file_gather.html", error_message=error_message,allowed_file=allowed_file_str)



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002)
