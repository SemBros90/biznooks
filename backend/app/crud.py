from sqlmodel import Session, select
from typing import Optional
from . import models
import datetime

def create_currency(session: Session, currency: models.Currency):
    session.add(currency)
    session.commit()
    session.refresh(currency)
    return currency

def create_exchange_rate(session: Session, rate: models.ExchangeRate):
    session.add(rate)
    session.commit()
    session.refresh(rate)
    return rate

def create_account(session: Session, account: models.Account):
    session.add(account)
    session.commit()
    session.refresh(account)
    return account

def create_journal(session: Session, journal: models.JournalEntry, lines: list[models.LedgerEntry]):
    total_debit = sum(l.debit for l in lines)
    total_credit = sum(l.credit for l in lines)
    if round(total_debit, 2) != round(total_credit, 2):
        raise ValueError("Journal not balanced: debits must equal credits")
    session.add(journal)
    session.commit()
    for l in lines:
        l.journal_id = journal.id
        session.add(l)
    session.commit()
    return journal

def get_latest_rate(session: Session, base: str, target: str):
    q = select(models.ExchangeRate).where(models.ExchangeRate.base == base, models.ExchangeRate.target == target).order_by(models.ExchangeRate.timestamp.desc())
    return session.exec(q).first()


def create_invoice(session: Session, invoice: models.Invoice, lines: list[models.InvoiceLine]):
    session.add(invoice)
    session.commit()
    for l in lines:
        l.invoice_id = invoice.id
        session.add(l)
    session.commit()
    session.refresh(invoice)
    return invoice


def build_einvoice_payload(session: Session, invoice_id: int) -> dict:
    inv = session.get(models.Invoice, invoice_id)
    if not inv:
        raise ValueError("Invoice not found")
    q = select(models.InvoiceLine).where(models.InvoiceLine.invoice_id == inv.id)
    lines = session.exec(q).all()
    total = sum(l.amount for l in lines)
    payload = {
        "supplier_name": None,
        "supplier_gstin": None,
        "invoice_number": inv.invoice_number,
        "date": str(inv.date),
        "customer_name": inv.customer_name,
        "customer_gstin": inv.customer_gstin,
        "place_of_supply": inv.place_of_supply,
        "is_export": bool(inv.is_export),
        "lut_applicable": bool(inv.lut_applicable),
        "iec": inv.iec,
        "currency": inv.currency,
        "total_amount": total,
        "lines": [
            {"description": l.description, "quantity": l.quantity, "unit_rate": l.unit_rate, "amount": l.amount, "igst": l.igst, "cgst": l.cgst, "sgst": l.sgst}
            for l in lines
        ],
    }
    return payload


def mark_einvoice_submitted(session: Session, invoice_id: int, irn: str, status: str = "SUBMITTED") -> models.Invoice:
    inv = session.get(models.Invoice, invoice_id)
    if not inv:
        raise ValueError("Invoice not found")
    inv.einvoice_irn = irn
    inv.einvoice_status = status
    session.add(inv)
    session.commit()
    session.refresh(inv)
    return inv


def create_tds_deduction(session: Session, tds: models.TDSDeduction):
    session.add(tds)
    session.commit()
    session.refresh(tds)
    return tds


def create_ewaybill(session: Session, ewb: models.EWaybill):
    session.add(ewb)
    session.commit()
    session.refresh(ewb)
    return ewb


def record_einvoice_audit(session: Session, invoice_id: int, event: str, details: Optional[str] = None) -> models.EInvoiceAudit:
    audit = models.EInvoiceAudit(invoice_id=invoice_id, event=event, details=details)
    session.add(audit)
    session.commit()
    session.refresh(audit)
    return audit


def list_einvoice_audit(session: Session, invoice_id: int, limit: int = 10):
    q = select(models.EInvoiceAudit).where(models.EInvoiceAudit.invoice_id == invoice_id).order_by(models.EInvoiceAudit.timestamp.desc()).limit(limit)
    return session.exec(q).all()


def attach_signed_document(session: Session, invoice_id: int, filename: str, path: str) -> models.SignedDocument:
    doc = models.SignedDocument(invoice_id=invoice_id, filename=filename, path=path)
    session.add(doc)
    session.commit()
    session.refresh(doc)
    record_einvoice_audit(session, invoice_id, "SIGNED_DOC_UPLOADED", f"{filename} at {path}")
    return doc


def get_einvoice_status(session: Session, invoice_id: int) -> dict:
    inv = session.get(models.Invoice, invoice_id)
    if not inv:
        raise ValueError("Invoice not found")
    events = list_einvoice_audit(session, invoice_id, limit=5)
    return {
        "invoice_id": inv.id,
        "einvoice_irn": inv.einvoice_irn,
        "status": inv.einvoice_status,
        "events": [{"event": e.event, "details": e.details, "timestamp": str(e.timestamp)} for e in events],
    }


def update_einvoice_status_by_irn(session: Session, irn: str, status: str) -> models.Invoice:
    q = select(models.Invoice).where(models.Invoice.einvoice_irn == irn)
    inv = session.exec(q).first()
    if not inv:
        raise ValueError("Invoice not found for IRN")
    inv.einvoice_status = status
    session.add(inv)
    session.commit()
    session.refresh(inv)
    record_einvoice_audit(session, inv.id, "GSTN_STATUS_UPDATE", f"status={status}")
    return inv


def check_and_store_nonce(session: Session, nonce: str, ts: Optional[str]) -> bool:
    """Return True if nonce stored successfully; raise ValueError if nonce exists or invalid timestamp."""
    if not nonce:
        raise ValueError("Missing nonce")
    # check existence
    q = select(models.WebhookNonce).where(models.WebhookNonce.nonce == nonce)
    exists = session.exec(q).first()
    if exists:
        raise ValueError("Nonce already used")
    # optional timestamp validation
    try:
        if ts:
            # expect ISO format
            parsed = datetime.datetime.fromisoformat(ts)
            now = datetime.datetime.utcnow()
            delta = abs((now - parsed).total_seconds())
            if delta > 300:
                raise ValueError("Timestamp out of acceptable range")
    except Exception as e:
        raise ValueError("Invalid timestamp")
    # store
    wn = models.WebhookNonce(nonce=nonce)
    session.add(wn)
    session.commit()
    session.refresh(wn)
    return True


def create_fx_realization(session: Session, invoice_id: int, payment_amount: float, payment_currency: str, realized_in_currency: str) -> models.FXRealization:
    """Create FX realization record and return it. Simplified: compares invoice currency amount vs payment in realized currency using latest rates."""
    inv = session.get(models.Invoice, invoice_id)
    if not inv:
        raise ValueError("Invoice not found")
    # sum invoice lines
    q = select(models.InvoiceLine).where(models.InvoiceLine.invoice_id == inv.id)
    lines = session.exec(q).all()
    invoice_total = sum(l.amount for l in lines)
    # convert invoice_total from invoice.currency -> realized_in_currency
    converted = _convert_amount(session, invoice_total, inv.currency, realized_in_currency)
    # realized difference = payment_amount - converted
    gain_loss = payment_amount - converted
    fx = models.FXRealization(
        invoice_id=inv.id,
        base_currency=inv.currency,
        realized_currency=realized_in_currency,
        original_amount=invoice_total,
        realized_amount=payment_amount,
        gain_loss=gain_loss,
    )
    session.add(fx)
    session.commit()
    session.refresh(fx)
    # create automatic journal lines: post gain/loss to a FX Gain/Loss account placeholder
    # find or create FX gain account
    qacc = select(models.Account).where(models.Account.name == 'FX Gain/Loss')
    acct = session.exec(qacc).first()
    if not acct:
        acct = models.Account(name='FX Gain/Loss', type='expense', currency=realized_in_currency)
        session.add(acct)
        session.commit()
        session.refresh(acct)
    # Post journal
    journal = models.JournalEntry(narration=f'FX realization for invoice {inv.invoice_number}')
    # If gain_loss >0 -> credit gain (revenue) else debit loss (expense). We'll simplify: treat positive as revenue (credit)
    if gain_loss > 0:
        lines = [
            models.LedgerEntry(account_id=acct.id, debit=0.0, credit=abs(gain_loss)),
            models.LedgerEntry(account_id=acct.id, debit=0.0, credit=0.0),
        ]
        # In practice we'd post to bank and fx gain accounts separately; keep simple placeholder
    else:
        lines = [
            models.LedgerEntry(account_id=acct.id, debit=abs(gain_loss), credit=0.0),
            models.LedgerEntry(account_id=acct.id, debit=0.0, credit=0.0),
        ]
    session.add(journal)
    session.commit()
    for l in lines:
        l.journal_id = journal.id
        session.add(l)
    session.commit()
    return fx


def summarize_gstr1(session: Session, period_start: datetime.date, period_end: datetime.date) -> dict:
    """Summarize invoices for a period for a basic GSTR-1 report (taxable value and tax by type)."""
    q = select(models.Invoice).where(models.Invoice.date >= period_start, models.Invoice.date <= period_end)
    invoices = session.exec(q).all()
    summary = {}
    total_taxable = 0.0
    total_igst = total_cgst = total_sgst = 0.0
    for inv in invoices:
        ql = select(models.InvoiceLine).where(models.InvoiceLine.invoice_id == inv.id)
        lines = session.exec(ql).all()
        for l in lines:
            total_taxable += l.amount
            total_igst += l.igst
            total_cgst += l.cgst
            total_sgst += l.sgst
    summary['total_taxable'] = total_taxable
    summary['total_igst'] = total_igst
    summary['total_cgst'] = total_cgst
    summary['total_sgst'] = total_sgst
    summary['invoice_count'] = len(invoices)
    return summary


def _convert_amount(session: Session, amount: float, from_currency: str, to_currency: str) -> float:
    """Convert amount from from_currency to to_currency using latest rate; returns same amount if currencies equal or rate missing."""
    if from_currency == to_currency:
        return amount
    rate_obj = get_latest_rate(session, from_currency, to_currency)
    if not rate_obj:
        # try inverse
        inv = get_latest_rate(session, to_currency, from_currency)
        if inv and inv.rate != 0:
            return amount / inv.rate
        return amount
    return amount * rate_obj.rate


def get_account_balance(session: Session, account_id: int, target_currency: str | None = None) -> dict:
    account = session.get(models.Account, account_id)
    if not account:
        raise ValueError("Account not found")
    q = select(models.LedgerEntry).where(models.LedgerEntry.account_id == account_id)
    lines = session.exec(q).all()
    debit = sum(l.debit for l in lines)
    credit = sum(l.credit for l in lines)
    balance = debit - credit
    result = {"account_id": account_id, "currency": account.currency, "balance": balance}
    if target_currency:
        converted = _convert_amount(session, balance, account.currency, target_currency.upper())
        result["converted_balance"] = converted
        result["target_currency"] = target_currency.upper()
    return result


def trial_balance(session: Session, target_currency: str | None = None) -> list[dict]:
    q = select(models.Account)
    accounts = session.exec(q).all()
    report = []
    for acc in accounts:
        ql = select(models.LedgerEntry).where(models.LedgerEntry.account_id == acc.id)
        lines = session.exec(ql).all()
        debit = sum(l.debit for l in lines)
        credit = sum(l.credit for l in lines)
        bal = debit - credit
        row = {"account_id": acc.id, "account_name": acc.name, "currency": acc.currency, "balance": bal}
        if target_currency:
            row["converted_balance"] = _convert_amount(session, bal, acc.currency, target_currency.upper())
            row["target_currency"] = target_currency.upper()
        report.append(row)
    return report


