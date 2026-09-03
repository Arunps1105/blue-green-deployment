from flask import Flask, jsonify
import os

app = Flask(__name__)

VERSION = "3"
ENVIRONMENT = os.getenv("ENVIRONMENT", "UNKNOWN")


@app.route("/")
def home():
    return f"Application Version {VERSION} - {ENVIRONMENT}"


@app.route("/health")
def health():
    return "OK"


@app.route("/version")
def version():
    return jsonify({
        "version": VERSION,
        "environment": ENVIRONMENT
    })


app.run(host="0.0.0.0", port=5000)