from flask import Flask, request
import ssl
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.x509 import load_pem_x509_certificate
from cryptography.hazmat.primitives.serialization import load_pem_public_key

app = Flask(__name__)

@app.route("/receive", methods=["POST"])
def receive():
    try:
        xml_file = request.files['xml_file'].read()
        signature = request.files['signature'].read()

        # Load sender's certificate to extract public key
        with open("certs/seg_sender.pem", "rb") as cert_file:
            cert = load_pem_x509_certificate(cert_file.read())
            public_key = cert.public_key()

        # Verify signature
        public_key.verify(
            signature,
            xml_file,
            padding.PKCS1v15(),
            hashes.SHA256()
        )

        # Save verified XML
        with open("received_document.xml", "wb") as f:
            f.write(xml_file)

        print("✅ Signature verified and XML saved.")
        return "Signature valid. Document accepted.", 200

    except Exception as e:
        print("❌ Signature verification failed:", str(e))
        return f"Signature verification failed: {str(e)}", 400

if __name__ == "__main__":
    context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    context.load_cert_chain(certfile='certs/seg_receiver.pem', keyfile='certs/seg_receiver.key')
    context.load_verify_locations(cafile='certs/rootCA.pem')
    context.verify_mode = ssl.CERT_REQUIRED

    print("🚀 SEG-Receiver running on https://127.0.0.1:8443")
    app.run(host="127.0.0.1", port=8443, ssl_context=context)
