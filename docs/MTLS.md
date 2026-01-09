mTLS and Webhook TLS (example)

This document shows a minimal nginx config for mutual TLS (mTLS) to secure webhook endpoints, plus OpenSSL commands to generate a self-signed CA, server cert, and client cert for testing.

nginx (snippet)

```
server {
  listen 443 ssl;
  server_name example.com;

  ssl_certificate /etc/nginx/certs/server.crt;
  ssl_certificate_key /etc/nginx/certs/server.key;

  # require client certificate signed by our CA
  ssl_client_certificate /etc/nginx/certs/ca.crt;
  ssl_verify_client on;

  location /webhooks/gstn {
    proxy_pass http://127.0.0.1:8000/webhooks/gstn;
    proxy_set_header X-Forwarded-Proto https;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
  }
}
```

Generate test CA, server and client certs (example):

```bash
# create CA
openssl genrsa -out ca.key 4096
openssl req -x509 -new -nodes -key ca.key -sha256 -days 3650 -subj "/CN=Test CA" -out ca.crt

# server key/csr
openssl genrsa -out server.key 2048
openssl req -new -key server.key -subj "/CN=example.com" -out server.csr
openssl x509 -req -in server.csr -CA ca.crt -CAkey ca.key -CAcreateserial -out server.crt -days 365 -sha256

# client key/csr
openssl genrsa -out client.key 2048
openssl req -new -key client.key -subj "/CN=webhook-client" -out client.csr
openssl x509 -req -in client.csr -CA ca.crt -CAkey ca.key -CAcreateserial -out client.crt -days 365 -sha256
```

Testing with curl (client cert):

```bash
curl -v --key client.key --cert client.crt --cacert ca.crt \
  -H "Content-Type: application/json" \
  -d '{"irn":"IRN-1","status":"VALID","nonce":"n1","timestamp":"2026-01-01T00:00:00"}' \
  https://example.com/webhooks/gstn
```

Python test example using `requests` (client cert):

```
import requests
payload = {...}
resp = requests.post('https://example.com/webhooks/gstn', json=payload, cert=('client.crt','client.key'), verify='ca.crt')
```

Notes:
- For production, use certificates issued by a trusted CA and store keys securely (KMS/Secret Manager).
- Use short-lived certificates and rotate them regularly.
- Consider mutual TLS combined with message signing for defense in depth.
