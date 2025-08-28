from flask import Flask, request, jsonify
from flask_cors import CORS
import uuid
from datetime import datetime
import os

app = Flask(__name__)
CORS(app, origins="*")

PORT = int(os.environ.get('PORT', 8003))

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy", "service": "hospital"})

@app.route('/api/v1/patients/register', methods=['POST'])
def register_patient():
    return jsonify({"id": str(uuid.uuid4()), "status": "registered"})

@app.route('/api/v1/patients', methods=['GET'])
def get_patients():
    return jsonify([])

@app.route('/', methods=['GET'])
def index():
    return jsonify({"service": "Hospital Server", "port": PORT})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=PORT)