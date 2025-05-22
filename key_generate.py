from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.x509 import SubjectAlternativeName, DNSName, IPAddress
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from datetime import datetime, timedelta
import ipaddress
import os

def save_pem(data, filename):
    with open(filename, "wb") as f:
        f.write(data)

def generate_key():
    return rsa.generate_private_key(public_exponent=65537, key_size=2048)

def build_name(cn, org="Government", country="BD"):
    return x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME, country),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, org),
        x509.NameAttribute(NameOID.COMMON_NAME, cn),
    ])

def generate_root_ca():
    key = generate_key()
    subject = issuer = build_name("RootCA", org="GovRootCA")
    cert = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(issuer)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(datetime.utcnow())
        .not_valid_after(datetime.utcnow() + timedelta(days=3650))
        .add_extension(x509.BasicConstraints(ca=True, path_length=None), critical=True)
        .sign(key, hashes.SHA256())
    )
    return key, cert

def generate_signed_cert(subject_cn, issuer_cert, issuer_key, org, san_list=[]):
    key = generate_key()
    subject = build_name(subject_cn, org=org)

    builder = x509.CertificateBuilder()\
        .subject_name(subject)\
        .issuer_name(issuer_cert.subject)\
        .public_key(key.public_key())\
        .serial_number(x509.random_serial_number())\
        .not_valid_before(datetime.utcnow())\
        .not_valid_after(datetime.utcnow() + timedelta(days=825))\
        .add_extension(x509.BasicConstraints(ca=False, path_length=None), critical=True)

    if san_list:
        san_entries = []
        for san in san_list:
            try:
                san_entries.append(IPAddress(ipaddress.ip_address(san)))
            except ValueError:
                san_entries.append(DNSName(san))
        builder = builder.add_extension(SubjectAlternativeName(san_entries), critical=False)

    cert = builder.sign(issuer_key, hashes.SHA256())
    return key, cert

def write_cert_and_key(cert, key, name):
    save_pem(cert.public_bytes(serialization.Encoding.PEM), f"certs/{name}.pem")
    save_pem(
        key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption(),
        ),
        f"certs/{name}.key",
    )

def main():
    os.makedirs("certs", exist_ok=True)

    print(">> Generating Root CA...")
    ca_key, ca_cert = generate_root_ca()
    write_cert_and_key(ca_cert, ca_key, "rootCA")

    print(">> Generating SEG-Sender certificate...")
    sender_key, sender_cert = generate_signed_cert(
        "SEG-Sender", ca_cert, ca_key, "Ministry1", san_list=["localhost"]
    )
    write_cert_and_key(sender_cert, sender_key, "seg_sender")

    print(">> Generating SEG-Receiver certificate with SANs for localhost and 127.0.0.1...")
    receiver_key, receiver_cert = generate_signed_cert(
        "SEG-Receiver", ca_cert, ca_key, "Ministry2", san_list=["127.0.0.1", "localhost"]
    )
    write_cert_and_key(receiver_cert, receiver_key, "seg_receiver")

    print("\n✅ All certificates and keys generated in ./certs:")
    print(" - rootCA.pem (CA certificate)")
    print(" - rootCA.key (CA private key)")
    print(" - seg_sender.pem/.key (Sender cert/key)")
    print(" - seg_receiver.pem/.key (Receiver cert/key)")

if __name__ == "__main__":
    main()
