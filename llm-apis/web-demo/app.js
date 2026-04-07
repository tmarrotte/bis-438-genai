// DOM Elements
const expenseInput = document.getElementById('expenseInput');
const sampleSelect = document.getElementById('sampleSelect');
const analyzeBtn = document.getElementById('analyzeBtn');
const resultsSection = document.getElementById('resultsSection');
const errorSection = document.getElementById('errorSection');
const resultContent = document.getElementById('resultContent');
const tokenContent = document.getElementById('tokenContent');
const rawResponseContent = document.getElementById('rawResponseContent');
const rawResponseHeader = document.getElementById('rawResponseHeader');
const errorContent = document.getElementById('errorContent');

// Event Listeners
sampleSelect.addEventListener('change', (e) => {
    if (e.target.value) {
        expenseInput.value = SAMPLES[e.target.value];
    }
});

analyzeBtn.addEventListener('click', analyzeExpense);

rawResponseHeader.addEventListener('click', () => {
    const content = rawResponseContent;
    const icon = rawResponseHeader.querySelector('.toggle-icon');
    
    if (content.style.display === 'none') {
        content.style.display = 'block';
        icon.classList.add('open');
    } else {
        content.style.display = 'none';
        icon.classList.remove('open');
    }
});

// Main Analysis Function
async function analyzeExpense() {
    const expenseDescription = expenseInput.value.trim();
    
    if (!expenseDescription) {
        showError('Please enter an expense description or select a sample expense.');
        return;
    }
    
    // Show loading state
    setLoading(true);
    hideResults();
    hideError();
    
    try {
        // Call the Python backend API
        const response = await fetch('http://localhost:5000/analyze', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                expense_description: expenseDescription
            })
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || 'Failed to analyze expense');
        }
        
        const data = await response.json();
        
        // Display results
        displayResults(data);
        
    } catch (error) {
        console.error('Error:', error);
        showError(`Error: ${error.message}\n\nMake sure the Python backend is running. Run: python app.py`);
    } finally {
        setLoading(false);
    }
}

// Display Functions
function displayResults(data) {
    const { result, metadata } = data;
    
    // Display analysis result
    resultContent.innerHTML = `
        <div class="result-grid">
            <div class="result-item">
                <div class="result-label">Category:</div>
                <div class="result-value">${escapeHtml(result.category)}</div>
            </div>
            <div class="result-item">
                <div class="result-label">Amount:</div>
                <div class="result-value">$${result.amount.toFixed(2)}</div>
            </div>
            <div class="result-item">
                <div class="result-label">Date:</div>
                <div class="result-value">${escapeHtml(result.date)}</div>
            </div>
            <div class="result-item">
                <div class="result-label">Vendor:</div>
                <div class="result-value">${escapeHtml(result.vendor)}</div>
            </div>
            <div class="result-item">
                <div class="result-label">Business Justification:</div>
                <div class="result-value">${escapeHtml(result.business_justification)}</div>
            </div>
            <div class="result-item">
                <div class="result-label">Decision:</div>
                <div class="result-value">
                    <span class="decision-badge ${getDecisionClass(result.decision)}">
                        ${escapeHtml(result.decision)}
                    </span>
                </div>
            </div>
            <div class="result-item">
                <div class="result-label">Reasoning:</div>
                <div class="result-value">${escapeHtml(result.reasoning)}</div>
            </div>
        </div>
    `;
    
    // Display token usage
    const usage = metadata.usage;
    const inputCost = (usage.input_tokens / 1000000) * 0.25;
    const outputCost = (usage.output_tokens / 1000000) * 1.25;
    const totalCost = inputCost + outputCost;
    
    tokenContent.innerHTML = `
        <div class="token-grid">
            <div class="token-item">
                <div class="token-label">Model:</div>
                <div class="token-value">${escapeHtml(metadata.model)}</div>
            </div>
            <div class="token-item">
                <div class="token-label">Stop Reason:</div>
                <div class="token-value">${escapeHtml(metadata.stop_reason)}</div>
            </div>
            <div class="token-item">
                <div class="token-label">Input Tokens:</div>
                <div class="token-value">${usage.input_tokens.toLocaleString()}</div>
            </div>
            <div class="token-item">
                <div class="token-label">Output Tokens:</div>
                <div class="token-value">${usage.output_tokens.toLocaleString()}</div>
            </div>
            <div class="token-item">
                <div class="token-label">Total Tokens:</div>
                <div class="token-value">${(usage.input_tokens + usage.output_tokens).toLocaleString()}</div>
            </div>
        </div>
        
        <div class="cost-highlight">
            <h3>Cost Breakdown</h3>
            <div class="token-grid">
                <div class="token-item">
                    <div class="token-label">Input Cost ($0.25 per million):</div>
                    <div class="token-value">$${inputCost.toFixed(6)}</div>
                </div>
                <div class="token-item">
                    <div class="token-label">Output Cost ($1.25 per million):</div>
                    <div class="token-value">$${outputCost.toFixed(6)}</div>
                </div>
                <div class="token-item">
                    <div class="token-label">Total Cost:</div>
                    <div class="token-value"><strong>$${totalCost.toFixed(6)}</strong></div>
                </div>
                <div class="token-item">
                    <div class="token-label">Cost for 1,000 expenses:</div>
                    <div class="token-value">$${(totalCost * 1000).toFixed(2)}</div>
                </div>
            </div>
        </div>
    `;
    
    // Display raw response
    rawResponseContent.innerHTML = `
        <pre class="raw-json">${JSON.stringify(metadata.full_response, null, 2)}</pre>
    `;
    
    // Show results section
    resultsSection.style.display = 'block';
}

// Helper Functions
function setLoading(isLoading) {
    analyzeBtn.disabled = isLoading;
    const btnText = analyzeBtn.querySelector('.btn-text');
    const spinner = analyzeBtn.querySelector('.spinner');
    
    if (isLoading) {
        btnText.textContent = 'Analyzing...';
        spinner.style.display = 'inline';
    } else {
        btnText.textContent = 'Analyze Expense';
        spinner.style.display = 'none';
    }
}

function hideResults() {
    resultsSection.style.display = 'none';
}

function showError(message) {
    errorContent.textContent = message;
    errorSection.style.display = 'block';
}

function hideError() {
    errorSection.style.display = 'none';
}

function getDecisionClass(decision) {
    if (decision === 'AUTO-APPROVE') return 'decision-approve';
    if (decision === 'FLAG FOR REVIEW') return 'decision-flag';
    if (decision === 'REJECT') return 'decision-reject';
    return '';
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}
