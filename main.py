from flask import Flask, request, jsonify
import easyocr
import os
from werkzeug.utils import secure_filename
import imghdr

app = Flask(__name__)
reader = easyocr.Reader(['id'])

ALLOWED_EXTENSIONS = {'jpg', 'png'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/scan', methods=['POST'])
def scan_image():
    file = request.files['file']
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_ext = filename.rsplit('.', 1)[1].lower()
        file_name = f'image.{file_ext}'
        file.save(file_name)
        result = reader.readtext(file_name, detail=0)
        os.remove(file_name)
        return jsonify({'message': result})
    else:
        return jsonify({'error': 'No file provided or invalid file format'}), 400

if __name__ == '__main__':
    app.run(debug=True)