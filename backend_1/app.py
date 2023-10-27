from flask import Flask, request, jsonify, Response
import os
from random import randint
from flask_cors import CORS  # Импортируйте библиотеку Flask-CORS
import random
from json import loads
from datetime import datetime


app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])





@app.route('/done', methods=['GET'])
def neural_network_done():
    neural_network()
    return jsonify({'message': f'Celery start', 'status': 'done'})





@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'})

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'No selected file'})

    if file:

        current_time = datetime.now()
        filename = current_time.strftime('%Y%m%d%H%M%S%f') + os.path.splitext(file.filename)[1]


        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))


        generated_number = random.randint(1, 100)

        return jsonify({'message': 'File uploaded successfully', 'generated_number': generated_number})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000,debug=True)

