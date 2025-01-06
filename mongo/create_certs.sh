#!/bin/bash

# Set the directory for certificates
CERT_DIR="docker/mongo/ssl"

# Check if the certificate directory exists, if not, create it
if [ ! -d "$CERT_DIR" ]; then
    echo "Certificate directory '$CERT_DIR' does not exist. Creating it..."
    mkdir -p "$CERT_DIR"
else
    echo "Certificate directory '$CERT_DIR' already exists."
fi

# Generate the server certificate and private key
echo "Creating self-signed TLS certificates..."

openssl req -newkey rsa:4096 -nodes -sha256 -keyout "$CERT_DIR/mongodb-key.pem" -x509 -days 365 -out "$CERT_DIR/mongodb-cert.pem" -subj "/C=DE/ST=Berlin/L=Berlin/O=Example Company/OU=IT Department/CN=your-domain.com"

echo "Certificates successfully created in: $CERT_DIR"

echo "Combine to a single file"
cat "$CERT_DIR/mongodb-cert.pem" "$CERT_DIR/mongodb-key.pem" > "$CERT_DIR/mongodb.pem"
