"""Demo: create an invoice and enqueue submission via `tasks.enqueue_einvoice_submission`.

Run with: `PYTHONPATH=. python3 backend/tests/run_enqueue_demo.py`
"""
from sqlmodel import Session
from backend.app import database, models, crud, tasks


def main():
    database.init_db()
    # create invoice and lines
    with Session(database.engine) as session:
        inv = models.Invoice(invoice_number='ENQ-001', date='2026-01-09', customer_name='RQ Buyer', customer_gstin='22AAAAA0000A1Z5', place_of_supply='22', currency='INR')
        line = models.InvoiceLine(description='Demo item', quantity=1, unit_rate=500.0, amount=500.0, igst=0.0, cgst=0.0, sgst=0.0)
        inv = crud.create_invoice(session, inv, [line])
        payload = crud.build_einvoice_payload(session, inv.id)

    result = tasks.enqueue_einvoice_submission(inv.id, payload, use_sandbox=False)
    print('Enqueue result:', result)


if __name__ == '__main__':
    main()
