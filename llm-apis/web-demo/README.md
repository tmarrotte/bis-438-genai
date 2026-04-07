# Expense Approval System - Web Demo

A simple web interface demonstrating the automated expense approval system using AWS Bedrock and Claude 3 Haiku.

## Features

- Clean, modern user interface
- Submit expense descriptions via text input
- Select from pre-loaded sample expenses
- View structured analysis results
- See real-time token usage and cost calculations
- Inspect raw API responses
- No framework dependencies - pure HTML/CSS/JavaScript

## Quick Start

### 1. Start the Python Backend

The web interface requires a simple Python HTTP server to handle API calls to AWS Bedrock.

```bash
# From the web-demo directory
cd web-demo
python server.py
```

The server will start on `http://localhost:5000`

### 2. Open the Web Interface

Simply open `index.html` in your web browser:

```bash
# Option 1: Open directly
open index.html

# Option 2: Use Python's built-in HTTP server for the frontend
python -m http.server 8000
# Then visit: http://localhost:8000
```

### 3. Analyze Expenses

1. Either:
   - Type or paste an expense description in the text area, OR
   - Select a sample expense from the dropdown
2. Click "Analyze Expense"
3. View the results, including:
   - Structured expense data (category, amount, vendor, etc.)
   - Approval decision with reasoning
   - Token usage and cost breakdown
   - Raw API response (collapsible)

## GitHub Codespaces Setup

This demo works perfectly in GitHub Codespaces:

### Method 1: Port Forwarding (Recommended)

1. Start the backend server:
   ```bash
   cd web-demo
   python server.py
   ```

2. GitHub Codespaces will automatically detect port 5000 and offer to forward it

3. Click "Open in Browser" for port 5000 to test the API

4. Open `index.html` in the Simple Browser (Cmd+Shift+P > "Simple Browser: Show")

### Method 2: VS Code Live Server Extension

1. Install the "Live Server" extension in Codespaces

2. Right-click `index.html` and select "Open with Live Server"

3. The extension will serve the files and automatically reload on changes

## File Structure

```
web-demo/
├── index.html      # Main HTML interface
├── styles.css      # Styling and layout
├── app.js          # Frontend JavaScript logic
├── samples.js      # Sample expense data
├── server.py       # Python backend API server
└── README.md       # This file
```

## How It Works

### Frontend (HTML/CSS/JavaScript)

- **index.html**: Structure and layout
- **styles.css**: Modern, responsive design with gradient background
- **app.js**: Handles user interactions, API calls, and result display
- **samples.js**: Contains pre-loaded sample expenses

### Backend (Python)

- **server.py**: Simple HTTP server that:
  - Accepts POST requests with expense descriptions
  - Loads the prompt template
  - Calls AWS Bedrock API
  - Returns structured results and metadata
  - Handles CORS for local development

## API Endpoint

### POST /analyze

**Request:**
```json
{
  "expense_description": "string"
}
```

**Response:**
```json
{
  "result": {
    "category": "string",
    "amount": number,
    "date": "YYYY-MM-DD",
    "vendor": "string",
    "business_justification": "string",
    "decision": "AUTO-APPROVE | FLAG FOR REVIEW | REJECT",
    "reasoning": "string"
  },
  "metadata": {
    "model": "string",
    "stop_reason": "string",
    "usage": {
      "input_tokens": number,
      "output_tokens": number
    },
    "full_response": {...}
  }
}
```

## Configuration

The backend reads credentials from the `.env` file in the parent directory:

```bash
# .env file
BEDROCK_API_KEY=your_api_key_here
AWS_REGION=us-east-1
```

## Troubleshooting

### "Failed to analyze expense" Error

**Problem**: The frontend can't reach the backend server

**Solutions**:
1. Make sure `server.py` is running (`python server.py`)
2. Check that the server is on port 5000
3. In Codespaces, ensure port 5000 is forwarded

### "BEDROCK_API_KEY not found" Error

**Problem**: Environment variables not loaded

**Solutions**:
1. Make sure `.env` file exists in the parent directory
2. Verify the API key is correctly set in `.env`
3. Restart the server after updating `.env`

### CORS Errors

**Problem**: Browser blocks cross-origin requests

**Solution**: The server already includes CORS headers. If you still see errors:
1. Use the same origin (e.g., serve both frontend and backend from localhost)
2. In production, implement proper CORS configuration

## Educational Use

This demo is designed for educational purposes to demonstrate:

1. **Real-time LLM API Calls**: See how API requests work in practice
2. **Token Economics**: Understand actual costs per request
3. **Structured Data Extraction**: Transform unstructured text to JSON
4. **Business Logic Application**: Automated decision-making based on rules
5. **User Experience**: How AI can be integrated into business workflows

## Production Considerations

This is a learning demo. For production use:

1. **Authentication**: Add proper user authentication
2. **Rate Limiting**: Implement request throttling
3. **Input Validation**: More robust validation and sanitization
4. **Error Handling**: Comprehensive error handling and logging
5. **Security**: Use environment-specific API keys, HTTPS, etc.
6. **Scalability**: Use proper backend framework (Flask, FastAPI, Express)
7. **Database**: Store expense analysis history
8. **Monitoring**: Track usage, costs, and performance

## Browser Compatibility

Works in all modern browsers:
- Chrome/Edge (recommended)
- Firefox
- Safari
- Opera

Requires JavaScript enabled.

## License

Educational use only - Part of BIS 438 course materials
