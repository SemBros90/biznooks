"""Demo: submit an invoice to a GSP client (simulated if no base URL).

This demo uses RSA keypair generation in-memory and the simulated GSP client.
"""
from app import database, models, crud
from app.gsp_client import GSPClient, generate_rsa_keypair
from pathlib import Path
import os


def demo():
    db_path = Path(__file__).resolve().parents[1] / 'data.db'
    if db_path.exists():
        try:
            os.remove(db_path)
        except Exception:
            pass
    database.init_db()
    with next(database.get_session()) as session:
        # create invoice
        inv = models.Invoice(invoice_number='INV-GSP-1', customer_name='G Buyer', currency='INR')
        line = models.InvoiceLine(description='GSP Item', quantity=1, unit_rate=100, amount=100)
        created = crud.create_invoice(session, inv, [line])
        print('Created invoice', created.id)
        # generate in-memory keys and use simulated client
        priv, pub = generate_rsa_keypair()
        client = GSPClient(base_url=None, pem_private=priv, pem_public=pub)
        payload = crud.build_einvoice_payload(session, created.id)
        resp = client.submit_einvoice(payload)
        print('GSP response:', resp)
        if resp.get('irn'):
            crud.mark_einvoice_submitted(session, created.id, resp.get('irn'), status=resp.get('status'))
            print('Invoice updated with IRN:', resp.get('irn'))

if __name__ == '__main__':
    demo()
