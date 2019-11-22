#!/usr/bin/env python3

from flask import Flask, request, jsonify

app = Flask(__name__)

# TODO: avoid logging of health check request (or disable request logging completely)
@app.route('/', methods=['GET'])
def healthcheck():
    return "Webhook running"

@app.route('/', methods=['POST'])
def webhook():
    print(request.json)
    return "OK"

def run(port, ssl_cert_path,ssl_key_path):
    app.run(host='0.0.0.0', port=port, ssl_context=(ssl_cert_path, ssl_key_path))

