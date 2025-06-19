import json
from flask import Flask, request, jsonify, render_template
import requests

app = Flask(__name__, static_url_path='/static', static_folder='static', template_folder='templates')

# Load invisible context once on startup
with open('context.txt', 'r') as f:
    INVISIBLE_CONTEXT = f.read().strip()

# Load customer configuration once on startup
with open('customer_config.json', 'r') as f:
    CUSTOMER_CONFIG = json.load(f)

@app.route('/')
def index():
    return render_template('test.html')

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json(silent=True) or {}
    message = data.get('message')
    customer_id = data.get('customer_id')
    if not message or not customer_id:
        return jsonify({'error': 'Missing message or customer_id'}), 400

    customer = CUSTOMER_CONFIG.get(customer_id)
    if not customer:
        return jsonify({'error': 'Invalid customer_id'}), 400

    headers = {
        'Authorization': f"Bearer {customer['api_key']}",
        'Content-Type': 'application/json',
        'HTTP-Referer': 'http://localhost:5000',
        'X-Title': 'Local Chatbot'
    }

    payload = {
        'model': customer.get('model', 'mistralai/mixtral-8x7b-instruct'),
        'messages': [
            {'role': 'system', 'content': INVISIBLE_CONTEXT},
            {'role': 'user', 'content': message}
        ]
    }

    try:
        resp = requests.post('https://openrouter.ai/api/v1/chat/completions', headers=headers, json=payload, timeout=30)
        if resp.status_code != 200:
            return jsonify({'error': 'API error', 'detail': resp.text}), 500
        data = resp.json()
        reply = data['choices'][0]['message']['content']
        return jsonify({'reply': reply})
    except requests.exceptions.RequestException as e:
        return jsonify({'error': 'Request failed', 'detail': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
