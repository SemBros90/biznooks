"""Demo: create accounts, exchange rate, journals and print trial balance."""
from app import database, models, crud
from pathlib import Path
import os


def demo():
    # reset demo DB so schema changes apply
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
        # exchange rate USD->INR
        crud.create_exchange_rate(session, models.ExchangeRate(base='USD', target='INR', rate=83.5))
        # accounts
        bank_inr = crud.create_account(session, models.Account(name='Bank INR', type='asset', currency='INR'))
        receivable_usd = crud.create_account(session, models.Account(name='AR USD', type='asset', currency='USD'))
        sales_usd = crud.create_account(session, models.Account(name='Sales USD', type='revenue', currency='USD'))
        # journal: export sale 1000 USD received into bank after conversion
        # credit sales 1000 USD -> in USD account; debit bank in INR 83500
        journal = models.JournalEntry(narration='Export sale with FX')
        lines = [
            models.LedgerEntry(account_id=bank_inr.id, debit=83500.0, credit=0.0),
            models.LedgerEntry(account_id=sales_usd.id, debit=0.0, credit=83500.0),
        ]
        crud.create_journal(session, journal, lines)
        # trial balance in native currencies
        tb_native = crud.trial_balance(session)
        print('Trial Balance (native):')
        for r in tb_native:
            print(r)
        # trial balance converted to INR
        tb_inr = crud.trial_balance(session, target_currency='INR')
        print('\nTrial Balance (converted to INR):')
        for r in tb_inr:
            print(r)


if __name__ == '__main__':
    demo()
