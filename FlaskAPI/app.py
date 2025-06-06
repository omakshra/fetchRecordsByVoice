from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Allow cross-origin requests from Razor frontend

@app.route('/api/command', methods=['POST'])
def handle_command():
    data = request.get_json()
    command = data.get('command', '')
    
    # For demo: just echo back the command
    print(f"Received command: {command}")

    # You can add your logic here, e.g. parse command, do actions, etc.
    response_message = f"Command received: {command}"

    return jsonify({'message': response_message})

if __name__ == '__main__':
    app.run(debug=True)
