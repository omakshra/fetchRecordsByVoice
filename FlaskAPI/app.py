from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Allow cross-origin requests from Razor frontend

@app.route('/ping', methods=['GET'])
def ping():
    return jsonify({"message": "Flask is connected to Razor!"})

if __name__ == '__main__':
    app.run(debug=True)
