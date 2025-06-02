from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/ping', methods=['GET'])
def ping():
    return jsonify(message="Flask is alive!")

if __name__ == '__main__':
    app.run(port=5000, debug=True)
