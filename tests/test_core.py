import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))
from app import database, models, crud

def setup_module(module):
    # ensure fresh db
    db = os.path.join(os.path.dirname(__file__), '..', 'backend', 'data.db')
    try:
        os.remove(db)
    except Exception:
        pass
    database.init_db()

def test_journal_balance():
    with next(database.get_session()) as s:
        crud.create_currency(s, models.Currency(code='INR', name='Rupee'))
        a1 = crud.create_account(s, models.Account(name='Cash', type='asset', currency='INR'))
        a2 = crud.create_account(s, models.Account(name='Revenue', type='revenue', currency='INR'))
        j = models.JournalEntry(narration='Test')
        lines = [models.LedgerEntry(account_id=a1.id, debit=100.0, credit=0.0), models.LedgerEntry(account_id=a2.id, debit=0.0, credit=100.0)]
        created = crud.create_journal(s, j, lines)
        assert created.id is not None

def test_einvoice_payload():
    with next(database.get_session()) as s:
        inv = models.Invoice(invoice_number='TINV', customer_name='C', currency='INR')
        line = models.InvoiceLine(description='Item', quantity=1, unit_rate=100, amount=100)
        created = crud.create_invoice(s, inv, [line])
        payload = crud.build_einvoice_payload(s, created.id)
        assert payload['invoice_number'] == 'TINV'
        assert payload['total_amount'] == 100
