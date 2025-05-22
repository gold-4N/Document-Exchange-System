import requests
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.serialization import load_pem_private_key

# Load XML file
with open("sample_document.xml", "rb") as f:
    xml_data = f.read()

# Load sender private key
with open("certs/seg_sender.key", "rb") as key_file:
    private_key = load_pem_private_key(key_file.read(), password=None)

# Create signature
signature = private_key.sign(
    xml_data,
    padding.PKCS1v15(),
    hashes.SHA256()
)

# Send both XML and signature
response = requests.post(
    url="https://127.0.0.1:8443/receive",
    files={
        "xml_file": ("document.xml", xml_data, "application/xml"),
        "signature": ("signature.sig", signature, "application/octet-stream")
    },
    cert=("certs/seg_sender.pem", "certs/seg_sender.key"),
    verify="certs/rootCA.pem"
)

print("🔁 Response from SEG-Receiver:")
print(response.status_code, response.text)
