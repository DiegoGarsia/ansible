from flask import Flask
import requests

app = Flask(__name__)

@app.route("/")
def index():
    response = requests.get("http://backend:5000/data")
    return {
        "frontend": "running",
        "backend_response": response.json()
    }

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
