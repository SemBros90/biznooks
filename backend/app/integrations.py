"""Integration client placeholders for GSTN/GSP, banks, payment gateways, customs.

These are simple interfaces and simulated implementations used by the prototype.
"""
from typing import Protocol, Optional, Dict


class GSTNClient(Protocol):
    def submit_einvoice(self, payload: dict) -> Dict:
        ...

    def get_status(self, irn: str) -> Dict:
        ...


class SimulatedGSTN:
    def submit_einvoice(self, payload: dict) -> Dict:
        # simulate assigning an IRN
        return {"status": "IRN_ASSIGNED", "irn": f"IRN-SIM-{payload.get('invoice_number', '0')}"}

    def get_status(self, irn: str) -> Dict:
        return {"irn": irn, "status": "VALID"}


class BankConnector(Protocol):
    def fetch_statements(self, account_id: int, since: str) -> list:
        ...


class PaymentGateway(Protocol):
    def create_payment(self, amount: float, currency: str, payee: dict) -> dict:
        ...


class CustomsConnector(Protocol):
    def submit_export_declaration(self, payload: dict) -> dict:
        ...


# Note: these classes are placeholders. Implement concrete integrations with secure auth, retries, and logging.
