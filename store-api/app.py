from flask import Flask
import os, socket

app = Flask(__name__)

@app.route("/health")
def health():
    return "ok", 200

@app.route("/ready")
def ready():
    return "ready", 200

@app.route("/")
def root():
    return f"Hello from {socket.gethostname()}\n"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)