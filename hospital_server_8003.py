# Create hospital_server.py
# cat > hospital_server.py << 'EOF'
#!/usr/bin/env python3
"""
Hospital Server - Healthcare Insurance RAG System
"""

import http.server
import socketserver
import json
import uuid
from datetime import datetime
from urllib.parse import urlparse, parse_qs

# In-memory storage
patients = {}
medical_records = {}
claims = {}

class HospitalHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/health':
            self.send_json_response({
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "server": "hospital",
                "version": "1.0.0",
                "patients_count": len(patients),
                "records_count": len(medical_records),
                "claims_count": len(claims)
            })
        
        elif self.path == '/api/v1/patients':
            self.send_json_response({
                "status": "success",
                "data": list(patients.values()),
                "count": len(patients)
            })
        
        elif self.path.startswith('/api/v1/patients/'):
            patient_id = self.path.split('/')[-1]
            if patient_id in patients:
                self.send_json_response({
                    "status": "success",
                    "data": patients[patient_id]
                })
            else:
                self.send_error_response(404, "Patient not found")
        else:
            self.send_error_response(404, "Endpoint not found")

    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        if content_length > 0:
            post_data = self.rfile.read(content_length)
            try:
                data = json.loads(post_data.decode('utf-8'))
            except json.JSONDecodeError:
                self.send_error_response(400, "Invalid JSON")
                return
        else:
            data = {}

        if self.path == '/api/v1/patients/register':
            self.register_patient(data)
        
        elif self.path == '/api/v1/medical-records':
            self.create_medical_record(data)
        
        elif self.path == '/api/v1/insurance-claims':
            self.submit_insurance_claim(data)
        
        else:
            self.send_error_response(404, "Endpoint not found")

    def register_patient(self, data):
        patient_id = f"PAT-{uuid.uuid4().hex[:8].upper()}"
        
        patient_data = {
            "patient_id": patient_id,
            "first_name": data.get("first_name", ""),
            "last_name": data.get("last_name", ""),
            "date_of_birth": data.get("date_of_birth", ""),
            "gender": data.get("gender", ""),
            "phone": data.get("phone", ""),
            "email": data.get("email", ""),
            "address": data.get("address", ""),
            "insurance_policy_number": data.get("insurance_policy_number", ""),
            "registration_date": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat()
        }
        
        patients[patient_id] = patient_data
        
        self.send_json_response({
            "status": "success",
            "message": "Patient registered successfully",
            "patient_id": patient_id,
            "data": patient_data
        })

    def create_medical_record(self, data):
        record_id = f"REC-{uuid.uuid4().hex[:8].upper()}"
        
        # Verify patient exists
        patient_id = data.get("patient_id")
        if patient_id not in patients:
            self.send_error_response(404, "Patient not found")
            return
        
        record_data = {
            "record_id": record_id,
            "patient_id": patient_id,
            "doctor_id": data.get("doctor_id", ""),
            "visit_date": data.get("visit_date", ""),
            "visit_type": data.get("visit_type", ""),
            "diagnosis": data.get("diagnosis", ""),
            "treatments": data.get("treatments", []),
            "total_cost": data.get("total_cost", 0),
            "insurance_claim_amount": data.get("insurance_claim_amount", 0),
            "notes": data.get("notes", ""),
            "created_date": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat()
        }
        
        medical_records[record_id] = record_data
        
        self.send_json_response({
            "status": "success",
            "message": "Medical record created successfully",
            "record_id": record_id,
            "data": record_data
        })

    def submit_insurance_claim(self, data):
        claim_id = f"CLM-{uuid.uuid4().hex[:8].upper()}"
        
        claim_data = {
            "claim_id": claim_id,
            "patient_id": data.get("patient_id", ""),
            "policy_number": data.get("policy_number", ""),
            "medical_record_ids": data.get("medical_record_ids", []),
            "total_amount": data.get("total_amount", 0),
            "claim_type": data.get("claim_type", ""),
            "priority": data.get("priority", "normal"),
            "status": "submitted",
            "submission_date": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat()
        }
        
        claims[claim_id] = claim_data
        
        self.send_json_response({
            "status": "success",
            "message": "Insurance claim submitted successfully",
            "claim_id": claim_id,
            "data": claim_data
        })

    def send_json_response(self, data, status_code=200):
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        self.wfile.write(json.dumps(data, indent=2).encode())

    def send_error_response(self, status_code, message):
        self.send_json_response({
            "status": "error",
            "message": message,
            "timestamp": datetime.now().isoformat()
        }, status_code)

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

if __name__ == "__main__":
    PORT = 8003
    print(f"Starting Hospital Server on http://localhost:{PORT}")
    print("Available endpoints:")
    print("  GET  /health")
    print("  POST /api/v1/patients/register")
    print("  GET  /api/v1/patients")
    print("  POST /api/v1/medical-records")
    print("  POST /api/v1/insurance-claims")
    print("\nPress Ctrl+C to stop")
    
    with socketserver.TCPServer(("", PORT), HospitalHandler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down Hospital Server...")
