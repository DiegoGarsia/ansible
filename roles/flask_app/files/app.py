from flask import Flask
import socket

app = Flask(__name__)

@app.route("/")
def index():
    return f"""
    <html>
        <body>
            <h1>Flask backend</h1>
            <p>Hostname: {socket.gethostname()}</p>
        </body>
    </html>
    """

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
