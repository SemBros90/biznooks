"""Demo: create an e-waybill for an invoice."""
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
        # create an e-waybill for invoice 1
        ewb = models.EWaybill(invoice_id=1, vehicle_number='KA01AB1234', distance=500.0, transporter_gstin='29AAAAA0000A1Z5')
        created = crud.create_ewaybill(session, ewb)
        print("Created e-waybill", created.id, "for invoice", created.invoice_id, "vehicle", created.vehicle_number)

if __name__ == '__main__':
    demo()