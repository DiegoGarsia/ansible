from flask import Flask
import os

app = Flask(__name__)

DATA_FILE = "/data/count.txt"


@app.route("/data")
def data():
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w") as f:
            f.write("0")

    with open(DATA_FILE, "r") as f:
        count = int(f.read())

    count += 1

    with open(DATA_FILE, "w") as f:
        f.write(str(count))

    return {
        "backend": "running",
        "request_count": count
    }


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
