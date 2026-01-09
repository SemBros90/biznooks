"""Quick demo script to validate DB and double-entry balancing."""
from app import database, models, crud

def demo():
    database.init_db()
    with next(database.get_session()) as session:
        # create currencies
        try:
            crud.create_currency(session, models.Currency(code="INR", name="Indian Rupee"))
        except Exception:
            pass
        try:
            crud.create_currency(session, models.Currency(code="USD", name="US Dollar"))
        except Exception:
            pass

        # create a sample exchange rate
        crud.create_exchange_rate(session, models.ExchangeRate(base="USD", target="INR", rate=83.5))

        # create accounts
        a_bank = crud.create_account(session, models.Account(name="Bank - INR", type="asset", currency="INR"))
        a_sales = crud.create_account(session, models.Account(name="Sales - USD", type="revenue", currency="USD"))

        # create a balanced journal: receive 1000 USD sale into bank (converted to INR not stored here)
        lines = [
            models.LedgerEntry(account_id=a_bank.id, debit=83500.0, credit=0.0),
            models.LedgerEntry(account_id=a_sales.id, debit=0.0, credit=83500.0),
        ]
        journal = models.JournalEntry(narration="Export sale received (converted)")
        created = crud.create_journal(session, journal, lines)
        print("Created journal", created.id)

if __name__ == '__main__':
    demo()
