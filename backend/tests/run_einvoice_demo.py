"""Demo: create an export invoice and simulate e-invoice payload & submission."""
from app import database, models, crud

from pathlib import Path
import os

def demo():
    # remove existing demo DB so schema changes apply (safe for demo)
    db_path = Path(__file__).resolve().parents[1] / 'data.db'
    if db_path.exists():
        try:
            os.remove(db_path)
        except Exception:
            pass
    database.init_db()
    with next(database.get_session()) as session:
        # ensure currencies (avoid duplicate inserts)
        if not session.get(models.Currency, "INR"):
            crud.create_currency(session, models.Currency(code="INR", name="Indian Rupee"))
        if not session.get(models.Currency, "USD"):
            crud.create_currency(session, models.Currency(code="USD", name="US Dollar"))

        # create an export invoice
        inv = models.Invoice(invoice_number="EXP-001", customer_name="Global Buyer", customer_gstin=None, place_of_supply="Outside India", is_export=True, lut_applicable=True, iec="IEC123456", currency="USD")
        line = models.InvoiceLine(description="Export widgets", quantity=10, unit_rate=100.0, amount=1000.0, igst=0.0, cgst=0.0, sgst=0.0)
        created = crud.create_invoice(session, inv, [line])
        print("Created invoice", created.id)
        payload = crud.build_einvoice_payload(session, created.id)
        print("Payload:", payload)
        inv2 = crud.mark_einvoice_submitted(session, created.id, irn=f"IRN-{created.id:06d}", status="IRN_ASSIGNED")
        print("Marked submitted:", inv2.einvoice_irn, inv2.einvoice_status)

if __name__ == '__main__':
    demo()
