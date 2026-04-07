#!/usr/bin/env python3
"""
Simple HTTP server for the Expense Approval Demo
Provides a REST API endpoint for analyzing expenses using AWS Bedrock
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import os
import requests
from dotenv import load_dotenv
from urllib.parse import parse_qs

# Load environment variables
load_dotenv()

BEDROCK_API_KEY = os.getenv('BEDROCK_API_KEY')
AWS_REGION = os.getenv('AWS_REGION', 'us-east-1')

class ExpenseAPIHandler(BaseHTTPRequestHandler):
    
    def do_OPTIONS(self):
        """Handle CORS preflight requests"""
        self.send_response(200)
        self.send_cors_headers()
        self.end_headers()
    
    def do_POST(self):
        """Handle POST requests to /analyze endpoint"""
        if self.path == '/analyze':
            try:
                # Read request body
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length)
                request_data = json.loads(post_data.decode('utf-8'))
                
                expense_description = request_data.get('expense_description', '')
                
                if not expense_description:
                    self.send_error_response(400, 'expense_description is required')
                    return
                
                # Load prompt template
                with open('prompt_ANSWER_KEY.txt', 'r') as f:
                    prompt_template = f.read()
                
                # Analyze expense
                result, metadata = self.analyze_expense(expense_description, prompt_template)
                
                # Send success response
                self.send_json_response(200, {
                    'result': result,
                    'metadata': metadata
                })
                
            except FileNotFoundError:
                self.send_error_response(500, 'Prompt template not found. Make sure prompt_ANSWER_KEY.txt exists.')
            except Exception as e:
                print(f"Error processing request: {e}")
                self.send_error_response(500, str(e))
        else:
            self.send_error_response(404, 'Not found')
    
    def analyze_expense(self, expense_description, prompt_template):
        """
        Analyze expense using AWS Bedrock API
        Returns: (result dict, metadata dict)
        """
        # Insert expense description into prompt
        full_prompt = prompt_template.replace("{EXPENSE_DESCRIPTION}", expense_description)
        
        # Prepare request body
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
        
        # Call Bedrock API
        url = f"https://bedrock-runtime.{AWS_REGION}.amazonaws.com/model/anthropic.claude-3-haiku-20240307-v1:0/invoke"
        headers = {
            "Authorization": f"Bearer {BEDROCK_API_KEY}",
            "Content-Type": "application/json"
        }
        
        response = requests.post(url, headers=headers, json=request_body, timeout=30)
        
        if response.status_code != 200:
            raise Exception(f"Bedrock API error: {response.status_code} - {response.text}")
        
        # Parse response
        response_body = response.json()
        
        # Store metadata
        metadata = {
            "model": response_body.get('model', 'anthropic.claude-3-haiku-20240307-v1:0'),
            "stop_reason": response_body.get('stop_reason'),
            "usage": response_body.get('usage', {}),
            "full_response": response_body
        }
        
        # Extract JSON from LLM output
        llm_output = response_body['content'][0]['text']
        
        if '```json' in llm_output:
            llm_output = llm_output.split('```json')[1].split('```')[0].strip()
        elif '```' in llm_output:
            llm_output = llm_output.split('```')[1].split('```')[0].strip()
        
        result = json.loads(llm_output)
        
        return result, metadata
    
    def send_json_response(self, status_code, data):
        """Send JSON response with CORS headers"""
        self.send_response(status_code)
        self.send_cors_headers()
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))
    
    def send_error_response(self, status_code, error_message):
        """Send error response with CORS headers"""
        self.send_json_response(status_code, {'error': error_message})
    
    def send_cors_headers(self):
        """Send CORS headers to allow frontend access"""
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
    
    def log_message(self, format, *args):
        """Custom log format"""
        print(f"[{self.log_date_time_string()}] {format % args}")


def run_server(port=5000):
    """Start the HTTP server"""
    server_address = ('', port)
    httpd = HTTPServer(server_address, ExpenseAPIHandler)
    
    print("=" * 80)
    print("Expense Approval API Server")
    print("=" * 80)
    print(f"Server running on http://localhost:{port}")
    print(f"Region: {AWS_REGION}")
    print(f"API Key configured: {'Yes' if BEDROCK_API_KEY else 'No'}")
    print("\nEndpoints:")
    print(f"  POST http://localhost:{port}/analyze")
    print("\nPress Ctrl+C to stop the server")
    print("=" * 80)
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n\nShutting down server...")
        httpd.shutdown()


if __name__ == '__main__':
    # Check for required environment variables
    if not BEDROCK_API_KEY:
        print("ERROR: BEDROCK_API_KEY not found in .env file")
        print("Please add your AWS Bedrock API key to the .env file")
        exit(1)
    
    run_server()
