"""Demo: create a TDS deduction for export payment."""
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
        # create a TDS deduction for export payment (section 195)
        tds = models.TDSDeduction(payment_id=1, amount=10000.0, tds_rate=10.0, tds_amount=1000.0, section='195')
        created = crud.create_tds_deduction(session, tds)
        print("Created TDS deduction", created.id, "for section", created.section)

if __name__ == '__main__':
    demo()