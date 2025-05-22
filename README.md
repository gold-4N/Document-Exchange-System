============================================ 

🔐 Secure Exchange Gateway (SEG) Prototype

============================================ 

# This project demonstrates secure XML file exchange between two parties using:

- Mutual TLS (mTLS) for authentication
- Digital Signature (RSA-SHA256) for document integrity and authenticity

=======================

📦 Requirements

=======================

- Python 3.8+
- OpenSSL
- Python packages:
  - cryptography
  - flask
  - requests

# Install required Python packages:
    pip3 install cryptography flask requests

=======================

🔧 Generate Certificates

=======================

1. Run the file named key_generate.py with the following command:

    python key_generate.py

Certificates will be saved in the certs/ folder.

=======================

🚀 Start SEG Receiver

=======================

Run the receiver:
    python receiver.py

=======================

📤 Run SEG Sender

=======================
1. Create an example XML file named sample_document.xml:

--------------------------------------------------

```xml
<CriticalDocument id="doc123">
  <SenderID>MINISTRY 1_SEG01</SenderID>
  <ReceiverID>MINISTRY 2_SEG01</ReceiverID>
  <TimestampForSignature>2025-05-22T15:30:00Z</TimestampForSignature>
  <Payload>
    <SensitiveData>Lunch party at Saturday</SensitiveData>
    <Instructions>Deliver by 0300.</Instructions>
  </Payload>
</CriticalDocument>
```

--------------------------------------------------

2. Run the sender:
    python sender.py

=======================

📂 Output

=======================

- On success:
    ✅ Signature verified and XML saved.
    XML is saved as: received_document.xml

- On failure:
    ❌ Signature verification failed: <error message>

=======================

📌 Notes

=======================

- You can extend it to use full XMLDSig standard if needed.
- mTLS ensures both endpoints are authenticated.
- Signature ensures message integrity and sender authenticity.

