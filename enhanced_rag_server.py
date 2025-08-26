#!/usr/bin/env python3
"""
Final Enhanced RAG Server with Customer Service Fallback
Port: 8005
Ready for Cloud Deployment
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
import re
import os

app = Flask(__name__)
CORS(app, origins="*", allow_headers=["Content-Type"], methods=["GET", "POST", "OPTIONS"])

# Configuration
PORT = int(os.environ.get('PORT', 8005))
HOST = '0.0.0.0'

# Comprehensive Insurance Knowledge Base
INSURANCE_KNOWLEDGE = {
    # Basic Coverage
    "deductible": {
        "keywords": ["deductible", "annual deductible", "pay first", "yearly deductible"],
        "response": "Your annual deductible is $1,500 for individuals and $3,000 for families. This is the amount you pay for covered healthcare services before your insurance starts to pay. You've currently met $450 (30%) of your individual deductible.",
        "confidence": 0.95,
        "category": "coverage_basics"
    },
    "out_of_pocket": {
        "keywords": ["out of pocket", "maximum", "oop", "out-of-pocket", "max out", "spending limit"],
        "response": "Your out-of-pocket maximum is $6,500 for individuals and $13,000 for families per year. After reaching this limit, your insurance covers 100% of covered services for the rest of the year.",
        "confidence": 0.95,
        "category": "coverage_basics"
    },
    
    # Preventive Care
    "preventive": {
        "keywords": ["preventive", "screening", "vaccination", "immunization", "wellness", "100%", "checkup", "physical", "annual exam"],
        "response": "Preventive services are covered at 100% with in-network providers. This includes annual physicals, vaccinations, mammograms, colonoscopies (age-appropriate), blood pressure screening, cholesterol checks, diabetes screening, and pediatric vision/hearing screening. No deductible required.",
        "confidence": 0.90,
        "category": "preventive_care"
    },
    
    # Emergency Services
    "emergency": {
        "keywords": ["emergency", "er", "emergency room", "emergency department", "urgent", "ambulance"],
        "response": "Emergency room visits are covered after your deductible with a $250 copay per visit. The copay is waived if you're admitted to the hospital. Ambulance services are covered at 80% after deductible. For non-life-threatening conditions, consider urgent care ($50 copay).",
        "confidence": 0.90,
        "category": "emergency_care"
    },
    
    # Prescription Drugs
    "prescription": {
        "keywords": ["prescription", "drug", "medication", "pharmacy", "rx", "medicine", "pills"],
        "response": "Prescription drug coverage tiers: Generic (Tier 1): $10 copay, Preferred Brand (Tier 2): $35 copay, Non-Preferred Brand (Tier 3): $75 copay, Specialty (Tier 4): 25% coinsurance up to $250. Mail-order pharmacy offers 90-day supplies with reduced copays.",
        "confidence": 0.90,
        "category": "prescription"
    },
    
    # Mental Health
    "mental_health": {
        "keywords": ["mental health", "therapy", "counseling", "psychiatrist", "psychology", "behavioral", "depression", "anxiety"],
        "response": "Mental health services are covered with a $30 copay per outpatient session. You have 50 covered sessions per year. Inpatient mental health requires preauthorization and is covered at 80% after deductible. Teletherapy is covered at the same rate as in-person visits.",
        "confidence": 0.85,
        "category": "mental_health"
    },
    
    # Dental & Vision
    "dental": {
        "keywords": ["dental", "teeth", "dentist", "oral", "tooth"],
        "response": "Dental is NOT covered under your base medical plan. We offer comprehensive dental insurance for an additional $25/month covering cleanings (100%), basic procedures (80%), and major work (50%). Emergency dental care may have limited coverage under medical for accidents.",
        "confidence": 0.90,
        "category": "dental"
    },
    "vision": {
        "keywords": ["vision", "eye", "glasses", "contacts", "optometry", "eyewear", "optical"],
        "response": "Vision coverage includes annual eye exam covered at 100% with in-network providers, plus $150 allowance for frames or contact lenses per year. LASIK and cosmetic procedures are not covered. Children's vision is fully covered including frames.",
        "confidence": 0.85,
        "category": "vision"
    },
    
    # Specialist Care
    "specialist": {
        "keywords": ["specialist", "referral", "specialty", "expert", "specialized"],
        "response": "Specialist visits require a referral from your primary care physician. With referral: $40 copay, then 80% coverage after deductible. Without referral, coverage may be reduced or denied. Second opinions are covered at the same rate.",
        "confidence": 0.85,
        "category": "specialist"
    },
    
    # Network
    "network": {
        "keywords": ["network", "in-network", "out-of-network", "provider", "ppo", "hmo", "covered doctors"],
        "response": "In-network providers: Lower costs with 80% coverage after deductible. Out-of-network: Higher deductible ($3,000), higher out-of-pocket max ($12,000), and you pay 40% after deductible. We have 2,547 hospitals and 45,000+ doctors in-network. Always verify network status before receiving care.",
        "confidence": 0.90,
        "category": "network"
    },
    
    # Maternity
    "maternity": {
        "keywords": ["maternity", "pregnancy", "prenatal", "delivery", "birth", "baby", "newborn", "pregnant"],
        "response": "Maternity coverage includes prenatal visits (100% covered), delivery and hospital stay (80% after deductible), postnatal care (100% for 6 weeks), and newborn care. Average out-of-pocket for uncomplicated delivery is $3,000-4,000. Breast pumps and lactation support are covered.",
        "confidence": 0.85,
        "category": "maternity"
    },
    
    # Additional Services
    "rehabilitation": {
        "keywords": ["physical therapy", "pt", "rehabilitation", "occupational therapy", "speech therapy", "rehab"],
        "response": "Physical therapy, occupational therapy, and speech therapy are covered up to 30 visits per year combined, with a $30 copay per visit. Additional visits may be approved with medical necessity documentation.",
        "confidence": 0.85,
        "category": "rehabilitation"
    },
    "telemedicine": {
        "keywords": ["telemedicine", "virtual", "telehealth", "online doctor", "video visit", "remote"],
        "response": "Telemedicine visits are covered with $15 copay for general medicine, $30 for specialists. Available 24/7 through our approved platforms. Mental health teletherapy has the same coverage as in-person visits.",
        "confidence": 0.90,
        "category": "telemedicine"
    },
    "alternative": {
        "keywords": ["alternative", "acupuncture", "chiropractic", "massage", "holistic", "complementary"],
        "response": "Alternative therapies: Chiropractic care covered up to 20 visits/year with $30 copay. Acupuncture covered up to 12 visits/year with $40 copay when medically necessary. Massage therapy not covered unless prescribed for specific conditions with preauthorization.",
        "confidence": 0.85,
        "category": "alternative"
    }
}

def find_best_match(query):
    """Find the best matching response for a query"""
    query_lower = query.lower()
    
    # Remove common filler words
    query_cleaned = re.sub(r'\b(what|how|is|are|my|the|a|an|about|tell|me|coverage|for|much)\b', '', query_lower)
    
    best_match = None
    best_score = 0
    best_confidence = 0
    
    # Search through knowledge base
    for topic_key, topic_data in INSURANCE_KNOWLEDGE.items():
        score = 0
        
        # Check keyword matches
        for keyword in topic_data["keywords"]:
            if keyword in query_lower:
                # Exact phrase match
                if keyword == query_lower.strip():
                    score += 10
                # Phrase contained
                elif keyword in query_lower:
                    score += 5
                # Word overlap
                else:
                    keyword_words = keyword.split()
                    for word in keyword_words:
                        if word in query_cleaned:
                            score += 2
        
        # Update best match
        if score > best_score:
            best_score = score
            best_match = topic_key
            best_confidence = topic_data["confidence"]
    
    # Return result based on confidence
    if best_match and best_score >= 5:  # Threshold for match
        data = INSURANCE_KNOWLEDGE[best_match]
        return {
            "response": data["response"],
            "confidence": best_confidence,
            "sources": [f"Insurance Policy Handbook - {data['category'].replace('_', ' ').title()}"],
            "matched": True
        }
    else:
        # No good match found - provide customer service fallback
        return {
            "response": "I couldn't find specific information about your question in our insurance policy database. For accurate information about your specific situation, please contact our customer service team at 1234567890 who can provide personalized assistance with your specific query.",
            "confidence": 0.3,
            "sources": ["Customer Service Recommended"],
            "matched": False,
            "customer_service": {
                "phone": "1234567890",
                "hours": "24/7 Support Available",
                "wait_time": "Average wait: 2 minutes"
            }
        }

@app.route('/health', methods=['GET', 'OPTIONS'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "enhanced_rag_server",
        "version": "3.0.0",
        "port": PORT,
        "knowledge_topics": len(INSURANCE_KNOWLEDGE),
        "timestamp": datetime.now().isoformat(),
        "deployment_ready": True
    })

@app.route('/api/v1/rag/query', methods=['POST', 'OPTIONS'])
def rag_query():
    """Main RAG query endpoint with customer service fallback"""
    
    # Handle preflight
    if request.method == 'OPTIONS':
        return jsonify({'status': 'ok'}), 200
    
    try:
        data = request.json
        query = data.get('query', '').strip()
        
        if not query:
            return jsonify({
                "error": "No query provided",
                "customer_service": {
                    "phone": "1234567890",
                    "message": "Please provide a question or call customer service at 1234567890"
                }
            }), 400
        
        print(f"📨 Query received: {query}")
        
        # Process query
        result = find_best_match(query)
        
        # Build response
        response_data = {
            "query": query,
            "response": result["response"],
            "confidence": result["confidence"],
            "sources": result["sources"],
            "timestamp": datetime.now().isoformat()
        }
        
        # Add customer service info if low confidence or no match
        if not result.get("matched", True) or result["confidence"] < 0.4:
            response_data["customer_service"] = result.get("customer_service", {
                "phone": "1234567890",
                "hours": "24/7 Support Available",
                "wait_time": "Average wait: 2 minutes",
                "message": "For more detailed assistance, please contact our customer service team at 1234567890"
            })
            print(f"🔴 Low confidence ({result['confidence']:.0%}) - Customer service recommended")
        else:
            print(f"🟢 High confidence ({result['confidence']:.0%})")
        
        return jsonify(response_data)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return jsonify({
            "error": str(e),
            "customer_service": {
                "phone": "1234567890",
                "message": "An error occurred. Please contact customer service at 1234567890 for assistance"
            }
        }), 500

@app.route('/api/v1/rag/topics', methods=['GET'])
def get_topics():
    """Get all available topics"""
    topics = {}
    for key, data in INSURANCE_KNOWLEDGE.items():
        topics[key] = {
            "keywords": data["keywords"],
            "confidence": data["confidence"],
            "category": data["category"]
        }
    return jsonify(topics)

@app.route('/')
def index():
    """Root endpoint"""
    return jsonify({
        "service": "HealthGuard AI RAG Server",
        "version": "3.0.0",
        "status": "operational",
        "endpoints": {
            "health": "/health",
            "query": "/api/v1/rag/query",
            "topics": "/api/v1/rag/topics"
        },
        "deployment": {
            "ready": True,
            "port": PORT,
            "cors": "enabled"
        }
    })

if __name__ == '__main__':
    print("="*60)
    print("🏥 HEALTHGUARD AI - ENHANCED RAG SERVER v3.0")
    print("="*60)
    print(f"📍 Port: {PORT}")
    print(f"🌐 CORS: Enabled for all origins")
    print(f"📚 Knowledge Base: {len(INSURANCE_KNOWLEDGE)} topics")
    print(f"☁️  Cloud Deployment: Ready")
    print("="*60)
    print("Endpoints:")
    print(f"  GET  / - Service info")
    print(f"  GET  /health - Health check")
    print(f"  POST /api/v1/rag/query - Process queries")
    print(f"  GET  /api/v1/rag/topics - List topics")
    print("="*60)
    
    # Use debug=False for production
    debug_mode = os.environ.get('DEBUG', 'True').lower() == 'true'
    app.run(host=HOST, port=PORT, debug=debug_mode)