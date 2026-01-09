from sqlmodel import SQLModel, Field, Relationship
from typing import Optional
import datetime

class Currency(SQLModel, table=True):
    code: str = Field(primary_key=True)
    name: Optional[str]

class ExchangeRate(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    base: str = Field(foreign_key="currency.code")
    target: str = Field(foreign_key="currency.code")
    rate: float
    timestamp: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)

class Account(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    type: str  # asset/liability/equity/revenue/expense
    currency: str = Field(foreign_key="currency.code")

class JournalEntry(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    date: datetime.date = Field(default_factory=datetime.date.today)
    narration: Optional[str]

class LedgerEntry(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    journal_id: Optional[int] = Field(foreign_key="journalentry.id")
    account_id: Optional[int] = Field(foreign_key="account.id")
    debit: float = 0.0
    credit: float = 0.0


class Invoice(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    invoice_number: str
    date: datetime.date = Field(default_factory=datetime.date.today)
    customer_name: Optional[str]
    customer_gstin: Optional[str]
    place_of_supply: Optional[str]
    is_export: bool = False
    lut_applicable: bool = False
    iec: Optional[str]
    currency: str = Field(foreign_key="currency.code")
    einvoice_irn: Optional[str] = None
    einvoice_status: Optional[str] = None


class InvoiceLine(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    invoice_id: Optional[int] = Field(foreign_key="invoice.id")
    description: Optional[str]
    quantity: float = 1.0
    unit_rate: float = 0.0
    amount: float = 0.0
    igst: float = 0.0
    cgst: float = 0.0
    sgst: float = 0.0


class TDSDeduction(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    payment_id: Optional[int]  # link to payment (placeholder, assume payment model exists)
    amount: float
    tds_rate: float
    tds_amount: float
    section: str  # e.g., '195' for non-resident payments
    date: datetime.date = Field(default_factory=datetime.date.today)


class EWaybill(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    invoice_id: Optional[int] = Field(foreign_key="invoice.id")
    ewb_number: Optional[str] = None
    vehicle_number: Optional[str]
    distance: Optional[float]
    transporter_gstin: Optional[str]
    status: Optional[str] = None
    date: datetime.date = Field(default_factory=datetime.date.today)


class EInvoiceAudit(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    invoice_id: Optional[int] = Field(foreign_key="invoice.id")
    event: str
    details: Optional[str]
    timestamp: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)


class SignedDocument(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    invoice_id: Optional[int] = Field(foreign_key="invoice.id")
    filename: str
    path: str
    uploaded_at: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)


class WebhookNonce(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    nonce: str
    timestamp: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)


class FXRealization(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    invoice_id: Optional[int] = Field(foreign_key="invoice.id")
    base_currency: str
    realized_currency: str
    original_amount: float
    realized_amount: float
    gain_loss: float
    timestamp: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)

