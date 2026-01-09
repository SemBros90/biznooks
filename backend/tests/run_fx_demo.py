"""Demo: create an invoice in USD, create rate, then realize payment in INR and record FX gain/loss."""
from app import database, models, crud
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
        # currencies
        if not session.get(models.Currency, 'INR'):
            crud.create_currency(session, models.Currency(code='INR', name='Indian Rupee'))
        if not session.get(models.Currency, 'USD'):
            crud.create_currency(session, models.Currency(code='USD', name='US Dollar'))
        # exchange rate USD->INR at sale time
        crud.create_exchange_rate(session, models.ExchangeRate(base='USD', target='INR', rate=80.0))
        # create invoice 1000 USD
        inv = models.Invoice(invoice_number='INV-FX-1', customer_name='Buyer', currency='USD')
        line = models.InvoiceLine(description='Export', quantity=1, unit_rate=1000.0, amount=1000.0)
        created = crud.create_invoice(session, inv, [line])
        print('Invoice created', created.id)
        # later, rate USD->INR is 83.5; create a new rate
        crud.create_exchange_rate(session, models.ExchangeRate(base='USD', target='INR', rate=83.5))
        # payment received in INR equivalent of 1000 USD at rate 83.5 -> 83500
        fx = crud.create_fx_realization(session, created.id, payment_amount=83500.0, payment_currency='INR', realized_in_currency='INR')
        print('FX realization created', fx.id, 'gain_loss', fx.gain_loss)

if __name__ == '__main__':
    demo()
