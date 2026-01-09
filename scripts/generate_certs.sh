#!/usr/bin/env bash
# Simple script to generate a test CA, server and client certs for local testing
set -e
OUT=./scripts/certs
mkdir -p $OUT

# CA
openssl genrsa -out $OUT/ca.key 4096
openssl req -x509 -new -nodes -key $OUT/ca.key -sha256 -days 3650 -subj "/CN=Test CA" -out $OUT/ca.crt

# server
openssl genrsa -out $OUT/server.key 2048
openssl req -new -key $OUT/server.key -subj "/CN=localhost" -out $OUT/server.csr
openssl x509 -req -in $OUT/server.csr -CA $OUT/ca.crt -CAkey $OUT/ca.key -CAcreateserial -out $OUT/server.crt -days 365 -sha256

# client
openssl genrsa -out $OUT/client.key 2048
openssl req -new -key $OUT/client.key -subj "/CN=webhook-client" -out $OUT/client.csr
openssl x509 -req -in $OUT/client.csr -CA $OUT/ca.crt -CAkey $OUT/ca.key -CAcreateserial -out $OUT/client.crt -days 365 -sha256

echo "Generated certs in $OUT"
