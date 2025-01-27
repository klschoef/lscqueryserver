from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
import os
import argparse
from flask_cors import CORS

# Setup argparse to handle command-line arguments
parser = argparse.ArgumentParser(description='Simple File Upload Server')
parser.add_argument('--upload_folder', type=str, required=True, help='Folder to store uploads')
parser.add_argument('--max_content_length', type=int, default=50 * 1024 * 1024, help='Max upload size in bytes')
parser.add_argument('--port', type=int, default=5000, help='Port to run the Flask server on')
args = parser.parse_args()

app = Flask(__name__)
CORS(app)


# Apply the argparse arguments to app configuration
app.config['UPLOAD_FOLDER'] = args.upload_folder
app.config['MAX_CONTENT_LENGTH'] = args.max_content_length

# Allowed file extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/ping', methods=['GET'])
def ping():
    return jsonify({'message': 'Pong!'})

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part in the request'}), 400

    files = request.files.getlist('file')

    uploaded_files = []
    errors = []

    for file in files:
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            uploaded_files.append(filename)
        else:
            errors.append(f"{file.filename}: Invalid file type or filename.")

    if errors:
        return jsonify({'error': 'Some files were not uploaded', 'messages': errors}), 400

    return jsonify({'message': 'Files successfully uploaded', 'files': uploaded_files}), 200


if __name__ == '__main__':
    app.run(debug=True, port=args.port)
