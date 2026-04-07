"""
Flask web application for Expense Approval System
Demonstrates a simple UI for uploading expenses and calling the LLM API
"""

from flask import Flask, render_template, request, jsonify
import os
import json
import requests
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Configuration
BEDROCK_API_KEY = os.getenv('BEDROCK_API_KEY')
AWS_REGION = os.getenv('AWS_REGION', 'us-east-1')

def load_prompt_template():
    """Load the prompt template from prompt.txt"""
    try:
        with open('prompt.txt', 'r') as f:
            return f.read()
    except FileNotFoundError:
        # Fallback to answer key if prompt.txt doesn't exist
        with open('prompt_ANSWER_KEY.txt', 'r') as f:
            return f.read()

def analyze_expense_with_llm(expense_description, prompt_template):
    """
    Send expense description to AWS Bedrock for analysis.
    
    Args:
        expense_description (str): The unstructured expense text
        prompt_template (str): The prompt template
    
    Returns:
        dict: Response containing result and metadata
    """
    
    # Insert the expense description into the prompt template
    full_prompt = prompt_template.replace("{EXPENSE_DESCRIPTION}", expense_description)
    
    # Prepare the request body for Claude 3 Haiku
    request_body = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 1000,
        "messages": [
            {
                "role": "user",
                "content": full_prompt
            }
        ],
        "temperature": 0.0,
        "top_p": 1.0
    }
    
    # Call the Bedrock API using Bearer token authentication
    url = f"https://bedrock-runtime.{AWS_REGION}.amazonaws.com/model/anthropic.claude-3-haiku-20240307-v1:0/invoke"
    headers = {
        "Authorization": f"Bearer {BEDROCK_API_KEY}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(url, headers=headers, json=request_body, timeout=30)
        
        if response.status_code != 200:
            return {
                "success": False,
                "error": f"API error: {response.status_code} - {response.text}"
            }
        
        # Parse the response from Bedrock
        response_body = response.json()
        
        # Store metadata
        metadata = {
            "model": response_body.get('model', 'anthropic.claude-3-haiku-20240307-v1:0'),
            "stop_reason": response_body.get('stop_reason'),
            "usage": response_body.get('usage', {})
        }
        
        llm_output = response_body['content'][0]['text']
        
        # Extract JSON from the response
        if '```json' in llm_output:
            llm_output = llm_output.split('```json')[1].split('```')[0].strip()
        elif '```' in llm_output:
            llm_output = llm_output.split('```')[1].split('```')[0].strip()
        
        # Parse the JSON response
        result = json.loads(llm_output)
        
        # Calculate cost
        input_tokens = metadata['usage'].get('input_tokens', 0)
        output_tokens = metadata['usage'].get('output_tokens', 0)
        input_cost = (input_tokens / 1_000_000) * 0.25
        output_cost = (output_tokens / 1_000_000) * 1.25
        total_cost = input_cost + output_cost
        
        return {
            "success": True,
            "result": result,
            "metadata": {
                "model": metadata['model'],
                "stop_reason": metadata['stop_reason'],
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "total_tokens": input_tokens + output_tokens,
                "cost": {
                    "input_cost": round(input_cost, 6),
                    "output_cost": round(output_cost, 6),
                    "total_cost": round(total_cost, 6)
                }
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@app.route('/')
def index():
    """Render the main page"""
    return render_template('index.html')

@app.route('/api/analyze', methods=['POST'])
def analyze_expense():
    """API endpoint to analyze an expense"""
    try:
        data = request.get_json()
        expense_description = data.get('expense_description', '').strip()
        
        if not expense_description:
            return jsonify({
                "success": False,
                "error": "Expense description is required"
            }), 400
        
        # Load prompt template
        prompt_template = load_prompt_template()
        
        # Analyze the expense
        response = analyze_expense_with_llm(expense_description, prompt_template)
        
        return jsonify(response)
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/sample-expenses', methods=['GET'])
def get_sample_expenses():
    """Get list of sample expense files"""
    try:
        sample_dir = 'sample_expenses'
        files = []
        
        if os.path.exists(sample_dir):
            for filename in sorted(os.listdir(sample_dir)):
                if filename.endswith('.txt'):
                    filepath = os.path.join(sample_dir, filename)
                    with open(filepath, 'r') as f:
                        content = f.read().strip()
                    files.append({
                        "filename": filename,
                        "content": content
                    })
        
        return jsonify({
            "success": True,
            "samples": files
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "api_configured": bool(BEDROCK_API_KEY),
        "region": AWS_REGION
    })

if __name__ == '__main__':
    # Run the Flask app
    # In Codespaces, this will be accessible via port forwarding
    # Note: Use port 5001 if 5000 is in use (common on macOS with AirPlay)
    app.run(host='0.0.0.0', port=5001, debug=True)
