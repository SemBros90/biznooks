from pydantic import BaseModel
from typing import Optional, List
import datetime

class CurrencyCreate(BaseModel):
    code: str
    name: Optional[str]

class ExchangeRateCreate(BaseModel):
    base: str
    target: str
    rate: float

class AccountCreate(BaseModel):
    name: str
    type: str
    currency: str

class LedgerLine(BaseModel):
    account_id: int
    debit: float = 0.0
    credit: float = 0.0

class JournalCreate(BaseModel):
    narration: Optional[str]
    date: Optional[datetime.date]
    lines: List[LedgerLine]


class InvoiceLineCreate(BaseModel):
    description: Optional[str]
    quantity: float = 1.0
    unit_rate: float = 0.0
    amount: float = 0.0
    igst: float = 0.0
    cgst: float = 0.0
    sgst: float = 0.0


class InvoiceCreate(BaseModel):
    invoice_number: str
    date: Optional[datetime.date]
    customer_name: Optional[str]
    customer_gstin: Optional[str]
    place_of_supply: Optional[str]
    is_export: bool = False
    lut_applicable: bool = False
    iec: Optional[str]
    currency: str
    lines: List[InvoiceLineCreate]


class TDSDeductionCreate(BaseModel):
    payment_id: Optional[int]
    amount: float
    tds_rate: float
    tds_amount: float
    section: str
    date: Optional[datetime.date]


class EWaybillCreate(BaseModel):
    invoice_id: int
    vehicle_number: Optional[str]
    distance: Optional[float]
    transporter_gstin: Optional[str]
    date: Optional[datetime.date]


class EInvoicePayload(BaseModel):
    supplier_name: Optional[str]
    supplier_gstin: Optional[str]
    invoice_number: str
    date: Optional[datetime.date]
    customer_name: Optional[str]
    customer_gstin: Optional[str]
    place_of_supply: Optional[str]
    is_export: bool
    lut_applicable: bool
    iec: Optional[str]
    currency: str
    total_amount: float
    lines: List[InvoiceLineCreate]


class EInvoiceStatusResponse(BaseModel):
    invoice_id: int
    einvoice_irn: Optional[str]
    status: Optional[str]
    last_events: List[dict]


class SignedDocumentCreate(BaseModel):
    filename: str
    path: str


class GSTNWebhook(BaseModel):
    irn: str
    status: str
    signature: Optional[str]
    nonce: Optional[str]
    timestamp: Optional[str]


