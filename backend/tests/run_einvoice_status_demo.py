"""Demo: submit an invoice, poll status, attach a signed document, and show status updates."""
from app import database, models, crud
from pathlib import Path
import os

def demo():
    # recreate DB for demo
    db_path = Path(__file__).resolve().parents[1] / 'data.db'
    if db_path.exists():
        try:
            os.remove(db_path)
        except Exception:
            pass
    database.init_db()
    with next(database.get_session()) as session:
        # create invoice
        inv = models.Invoice(invoice_number="INV-STATUS-1", customer_name="Buyer", currency="INR")
        line = models.InvoiceLine(description="Service", quantity=1, unit_rate=100.0, amount=100.0)
        created = crud.create_invoice(session, inv, [line])
        print("Created invoice", created.id)
        # submit (assign IRN)
        created = crud.mark_einvoice_submitted(session, created.id, irn=f"IRN-{created.id:06d}", status="IRN_ASSIGNED")
        print("Submitted, IRN:", created.einvoice_irn)
        # record additional audit event
        crud.record_einvoice_audit(session, created.id, "SIGNED", "Signed payload stored")
        # attach signed doc
        doc = crud.attach_signed_document(session, created.id, "signed_INV-STATUS-1.pdf", "/tmp/signed_INV-STATUS-1.pdf")
        print("Attached signed doc", doc.id, doc.path)
        # poll status
        status = crud.get_einvoice_status(session, created.id)
        print("Status:", status)

if __name__ == '__main__':
    demo()
