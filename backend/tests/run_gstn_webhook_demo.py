"""Demo: simulate GSTN sending a webhook callback with signature."""
from app import database, models, crud
from app.gst_signing import sign_payload
from pathlib import Path
import os


def demo():
    # reset DB
    db_path = Path(__file__).resolve().parents[1] / 'data.db'
    if db_path.exists():
        try:
            os.remove(db_path)
        except Exception:
            pass
    database.init_db()
    with next(database.get_session()) as session:
        # create invoice and assign IRN
        inv = models.Invoice(invoice_number='INV-WEB-1', customer_name='Buyer', currency='INR')
        line = models.InvoiceLine(description='Item', quantity=1, unit_rate=100, amount=100)
        created = crud.create_invoice(session, inv, [line])
        created = crud.mark_einvoice_submitted(session, created.id, irn='IRN-TEST-0001', status='IRN_ASSIGNED')
        print('Invoice IRN assigned:', created.einvoice_irn)
        # GSTN sends webhook updating status to VALID
        text = f"{created.einvoice_irn}|VALID"
        signature = sign_payload(text)
        # simulate webhook by directly calling CRUD update (in real usage the endpoint would be called)
        updated = crud.update_einvoice_status_by_irn(session, created.einvoice_irn, 'VALID')
        print('Webhook processed, new status:', updated.einvoice_status)

if __name__ == '__main__':
    demo()
