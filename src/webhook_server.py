#!/usr/bin/env python3

from flask import Flask, request, jsonify
import copy
import json

app = Flask(__name__)

# TODO: restart on new cert

# TODO: avoid logging of health check request (or disable request logging completely)
@app.route('/', methods=['GET'])
def healthcheck():
    return "Webhook running"

@app.route('/', methods=['POST'])
def webhook():
    admission_review=request.json
    admission_response = {
        "allowed": True,
        "uid": admission_review["request"]["uid"]
#        "patch": base64.b64encode(str(patch).encode()).decode(),
#        "patchtype": "JSONPatch"
    }
    admission_review["response"]=admission_response
    print(json.dumps(admission_review, indent=4))
    return admission_review

def run(port, ssl_cert_path,ssl_key_path):
    app.run(host='0.0.0.0', port=port, ssl_context=(ssl_cert_path, ssl_key_path))

