"""Demo: upload a dummy signed document using the storage adapter (filesystem fallback).

Run: `PYTHONPATH=. python3 backend/tests/run_store_signed_demo.py`
"""
from backend.app.storage import storage


def main():
    data = b"%PDF-1.4\n%Dummy PDF content for demo\n" * 10
    path = storage.upload_bytes('demo/invoice-1-signed.pdf', data, content_type='application/pdf')
    print('Stored at:', path)


if __name__ == '__main__':
    main()
