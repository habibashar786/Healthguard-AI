from flask import Flask, request, jsonify
from flask_cors import CORS
import uuid
from datetime import datetime
import os

app = Flask(__name__)
CORS(app)

@app.route('/health')
def health():
    return jsonify({"status": "healthy"})

@app.route('/api/v1/patients/register', methods=['POST'])
def register_patient():
    return jsonify({"id": str(uuid.uuid4()), "status": "registered"})

@app.route('/api/v1/patients', methods=['GET'])
def get_patients():
    return jsonify([])

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8003))
    app.run(host='0.0.0.0', port=port)
