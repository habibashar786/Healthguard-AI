#!/usr/bin/env python3
"""
Insurance Server - Actual Server (Port 8004)
Handles insurance policies, claims, and assessments
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
import json
import random
import os

app = Flask(__name__)

# Fixed CORS configuration to handle preflight requests properly
CORS(app, 
     resources={r"/*": {"origins": "*"}},
     allow_headers=["Content-Type", "Accept", "Authorization"],
     methods=["GET", "POST", "OPTIONS", "PUT", "DELETE"],
     supports_credentials=False,
     max_age=3600)

PORT = int(os.environ.get('PORT', 8004))
HOST = '0.0.0.0'

# In-memory storage
policies = {}
claims = {}
assessments = {}

# Add OPTIONS handler for all routes
@app.before_request
def handle_preflight():
    if request.method == "OPTIONS":
        response = jsonify({'status': 'ok'})
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add('Access-Control-Allow-Headers', "*")
        response.headers.add('Access-Control-Allow-Methods', "*")
        return response, 200

@app.after_request
def after_request(response):
    # Ensure CORS headers are always present
    origin = request.headers.get('Origin', '*')
    response.headers.add('Access-Control-Allow-Origin', origin if origin else '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Accept,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,POST,OPTIONS,PUT,DELETE')
    return response

@app.route('/health', methods=['GET', 'OPTIONS'])
def health_check():
    """Health check endpoint"""
    if request.method == 'OPTIONS':
        return '', 200
    
    return jsonify({
        "status": "healthy",
        "server": "insurance",
        "version": "1.0.0",
        "port": PORT,
        "timestamp": datetime.now().isoformat(),
        "policies_count": len(policies),
        "claims_count": len(claims),
        "assessments_count": len(assessments)
    })

@app.route('/api/v1/policies', methods=['GET', 'OPTIONS'])
def get_policies():
    """Get all policies"""
    if request.method == 'OPTIONS':
        return '', 200
    
    return jsonify({
        "status": "success",
        "count": len(policies),
        "data": list(policies.values())
    })

@app.route('/api/v1/policies', methods=['POST', 'OPTIONS'])
def create_policy():
    """Create new policy"""
    if request.method == 'OPTIONS':
        return '', 200
    
    data = request.json
    policy_id = f"POL-{random.randint(100000, 999999)}"
    
    policy = {
        "policy_id": policy_id,
        "patient_id": data.get("patient_id"),
        "policy_number": data.get("policy_number", policy_id),
        "plan_type": data.get("plan_type", "PPO"),
        "premium": data.get("premium", 450.00),
        "deductible": data.get("deductible", 1500),
        "coverage_details": data.get("coverage_details", {
            "preventive_care": 100,
            "emergency": 80,
            "specialist": 80,
            "prescription": 80
        }),
        "status": "active",
        "created_at": datetime.now().isoformat()
    }
    
    policies[policy_id] = policy
    
    return jsonify({
        "status": "success",
        "message": "Policy created",
        "policy_id": policy_id,
        "data": policy
    })

@app.route('/api/v1/claims/assess', methods=['POST', 'OPTIONS'])
def assess_claim():
    """Assess insurance claim"""
    if request.method == 'OPTIONS':
        return '', 200
    
    data = request.json
    assessment_id = f"ASS-{random.randint(100000, 999999)}"
    
    # Simple assessment logic
    total_amount = data.get("total_amount", 0)
    covered_amount = total_amount * 0.8  # 80% coverage
    
    assessment = {
        "assessment_id": assessment_id,
        "claim_id": data.get("claim_id"),
        "policy_number": data.get("policy_number"),
        "total_amount": total_amount,
        "covered_amount": covered_amount,
        "patient_responsibility": total_amount - covered_amount,
        "status": "approved" if covered_amount > 0 else "denied",
        "assessed_at": datetime.now().isoformat()
    }
    
    assessments[assessment_id] = assessment
    
    return jsonify({
        "status": "success",
        "message": "Claim assessed",
        "assessment_id": assessment_id,
        "data": assessment
    })

@app.route('/api/v1/coverage', methods=['POST', 'OPTIONS'])
def check_coverage():
    """Check coverage for a specific service"""
    if request.method == 'OPTIONS':
        return '', 200
    
    data = request.json
    service = data.get("service", "").lower()
    
    coverage_map = {
        "preventive": 100,
        "emergency": 80,
        "specialist": 80,
        "prescription": 80,
        "dental": 0,
        "vision": 50
    }
    
    coverage = coverage_map.get(service, 50)
    
    return jsonify({
        "service": service,
        "coverage_percentage": coverage,
        "requires_preauth": coverage < 80,
        "deductible_applies": coverage < 100
    })

@app.route('/', methods=['GET', 'OPTIONS'])
def index():
    """Root endpoint"""
    if request.method == 'OPTIONS':
        return '', 200
    
    return jsonify({
        "service": "Insurance Server",
        "version": "1.0.0",
        "port": PORT,
        "endpoints": {
            "health": "/health",
            "policies": "/api/v1/policies",
            "assess_claim": "/api/v1/claims/assess",
            "check_coverage": "/api/v1/coverage"
        }
    })

if __name__ == '__main__':
    print("="*60)
    print("INSURANCE SERVER")
    print("="*60)
    print(f"Starting on http://localhost:{PORT}")
    print("="*60)
    # Use debug=False for production
    debug_mode = os.environ.get('DEBUG', 'False').lower() == 'true'
    app.run(host=HOST, port=PORT, debug=debug_mode)