from flask import Flask, request, jsonify
from flask_cors import CORS
import uuid
from datetime import datetime
import os

app = Flask(__name__)

# Fixed CORS configuration
CORS(app, 
     resources={r"/*": {"origins": "*"}},
     allow_headers=["Content-Type", "Accept", "Authorization"],
     methods=["GET", "POST", "OPTIONS", "PUT", "DELETE"],
     supports_credentials=False)

@app.before_request
def handle_preflight():
    if request.method == "OPTIONS":
        response = jsonify({'status': 'ok'})
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add('Access-Control-Allow-Headers', "*")
        response.headers.add('Access-Control-Allow-Methods', "*")
        return response, 200

@app.route('/health', methods=['GET', 'OPTIONS'])
def health():
    return jsonify({"status": "healthy", "service": "hospital"})

@app.route('/api/v1/patients/register', methods=['POST', 'OPTIONS'])
def register_patient():
    return jsonify({"id": str(uuid.uuid4()), "status": "registered"})

@app.route('/api/v1/patients', methods=['GET', 'OPTIONS'])
def get_patients():
    return jsonify([])

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8003))
    app.run(host='0.0.0.0', port=port)