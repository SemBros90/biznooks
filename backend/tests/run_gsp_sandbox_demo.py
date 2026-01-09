"""Demo: submit a sample invoice to the GSP client using sandbox settings.

Run from repo root with: `PYTHONPATH=. python3 backend/tests/run_gsp_sandbox_demo.py`
"""
import os
import json
from backend.app.gsp_client import GSPClient


def main():
    # Use sandbox URL if provided in env; otherwise this demo will use the simulated GSTN.
    client = GSPClient()

    payload = {
        "invoice": {
            "number": "SAND-001",
            "date": "2026-01-09",
            "buyer": {"gstin": "22AAAAA0000A1Z5", "name": "Sandbox Buyer"},
            "seller": {"gstin": "27BBBBB1111B2Z6", "name": "Sandbox Seller"},
            "items": [{"desc": "Test item", "qty": 1, "rate": 1000.0}],
            "total": 1000.0
        }
    }

    resp = client.submit_einvoice(payload, use_sandbox=True)
    print('GSP sandbox response:')
    print(json.dumps(resp, indent=2))


if __name__ == '__main__':
    main()
