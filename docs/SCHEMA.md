# Data Model (high level)

- `Currency(code)` — ISO code like INR, USD.
- `ExchangeRate(base, target, rate, timestamp)` — rate to convert base -> target.
- `Account(id, name, type, currency)` — accounting ledger account.
- `JournalEntry(id, date, narration)` — grouping for ledger lines.
- `LedgerEntry(journal_id, account_id, debit, credit)` — double-entry lines.

Notes:
- Amounts stored in account currency; conversion for consolidated reporting uses latest rates or historic rate at transaction date.
- Realized/unrealized FX gains are accounted via dedicated GL accounts.

- `Invoice` / `InvoiceLine` — captures invoice header and line items including GST breakdown fields (`igst`, `cgst`, `sgst`), `is_export`, `lut_applicable`, and `iec` for export workflows.

