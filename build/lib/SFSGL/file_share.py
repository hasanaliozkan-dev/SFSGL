"""
@author : hasanaliozkan-dev
"""
from flask import Flask, send_from_directory,render_template #3.1.0
import os
import sys 


app = Flask(__name__)

folder_name = sys.argv[1]


EXAMPLE_FOLDER = folder_name  
ALLOWED_EXTENSIONS = {'py' , 'zip'}  



def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    try:
        files = [f for f in os.listdir(EXAMPLE_FOLDER) if allowed_file(f)]
        return render_template('file_share.html', files=files)
    except Exception as e:
        app.logger.error(f"Error rendering template: {e}")
        return "Internal Server Error", 500


@app.route('/download/<filename>')
def download_file(filename):

    if allowed_file(filename) and os.path.isfile(os.path.join(EXAMPLE_FOLDER, filename)):
        return send_from_directory(EXAMPLE_FOLDER, filename, as_attachment=True)
    else:
        return "File not found or invalid file type", 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
