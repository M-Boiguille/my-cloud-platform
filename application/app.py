"""Online Boutique - Application de démonstration."""

import os
from flask import Flask, jsonify

app = Flask(__name__)

version = os.environ.get("APP_VERSION", "dev")


@app.route("/")
def index():
    return jsonify({"service": "online-boutique", "version": version, "status": "ok"})


@app.route("/healthz")
def healthz():
    return jsonify({"status": "healthy"})


@app.route("/readyz")
def readyz():
    return jsonify({"status": "ready"})
