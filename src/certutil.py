from cryptography import x509
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from datetime import datetime, timedelta
import logging as log

def get_selfsigned_cert(cname,valid_days):
    log.info("Generating new RSA key")
    key = rsa.generate_private_key(key_size=4096, public_exponent=65537, backend=default_backend())
    log.info("Generating SSL certificate")
    name=x509.Name([x509.NameAttribute(x509.oid.NameOID.COMMON_NAME, cname)])
    now = datetime.utcnow()
    cert = (x509.CertificateBuilder()
        .subject_name(name)
        .issuer_name(name)
        .public_key(key.public_key())
        .serial_number(1000)
        .not_valid_before(now - timedelta(days=1))
        .not_valid_after(now + timedelta(days=valid_days))
        .add_extension(x509.BasicConstraints(ca=True, path_length=0), False)
        .sign(key, hashes.SHA256(), default_backend()))

    key_encoded = key.private_bytes(encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption())
    cert_encoded = cert.public_bytes(encoding=serialization.Encoding.PEM)

    return key_encoded, cert_encoded