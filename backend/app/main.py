from fastapi import FastAPI, HTTPException, Depends
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('biznooks')
from fastapi import UploadFile, File
from sqlmodel import Session
from . import models, schemas, crud, database
from .storage import storage
from .auth import get_current_user_optional, get_current_user, require_role

app = FastAPI(title="Biznooks Accounting - Demo")
from .middleware import SimpleRateLimiter


app.add_middleware(SimpleRateLimiter, calls_per_minute=600)


@app.on_event("startup")
def on_startup():
    database.init_db()


@app.post("/currencies")
def add_currency(data: schemas.CurrencyCreate, user=Depends(get_current_user)):
    # require admin role to create currencies
    if not require_role(user, 'admin'):
        raise HTTPException(status_code=403, detail='admin role required')
    with next(database.get_session()) as session:
        cur = models.Currency(code=data.code.upper(), name=data.name)
        return crud.create_currency(session, cur)


@app.post("/rates")
def add_rate(data: schemas.ExchangeRateCreate):
    with next(database.get_session()) as session:
        rate = models.ExchangeRate(base=data.base.upper(), target=data.target.upper(), rate=data.rate)
        return crud.create_exchange_rate(session, rate)


@app.post("/accounts")
def add_account(data: schemas.AccountCreate, user=Depends(get_current_user)):
    # require admin role to create accounts
    if not require_role(user, 'admin'):
        raise HTTPException(status_code=403, detail='admin role required')
    with next(database.get_session()) as session:
        acc = models.Account(name=data.name, type=data.type, currency=data.currency.upper())
        return crud.create_account(session, acc)


@app.post("/journals")
def add_journal(data: schemas.JournalCreate):
    with next(database.get_session()) as session:
        journal = models.JournalEntry(narration=data.narration, date=data.date)
        lines = []
        for ln in data.lines:
            lines.append(models.LedgerEntry(account_id=ln.account_id, debit=ln.debit, credit=ln.credit))
        try:
            created = crud.create_journal(session, journal, lines)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        return {"journal_id": created.id}


@app.post("/invoices")
def add_invoice(data: schemas.InvoiceCreate):
    with next(database.get_session()) as session:
        inv = models.Invoice(
            invoice_number=data.invoice_number,
            date=data.date,
            customer_name=data.customer_name,
            customer_gstin=data.customer_gstin,
            place_of_supply=data.place_of_supply,
            is_export=data.is_export,
            lut_applicable=data.lut_applicable,
            iec=data.iec,
            currency=data.currency.upper(),
        )
        lines = []
        for ln in data.lines:
            lines.append(models.InvoiceLine(description=ln.description, quantity=ln.quantity, unit_rate=ln.unit_rate, amount=ln.amount, igst=ln.igst, cgst=ln.cgst, sgst=ln.sgst))
        created = crud.create_invoice(session, inv, lines)
        return {"invoice_id": created.id}


@app.get("/invoices/{invoice_id}/einvoice_payload")
def get_einvoice_payload(invoice_id: int):
    with next(database.get_session()) as session:
        try:
            payload = crud.build_einvoice_payload(session, invoice_id)
        except ValueError as e:
            raise HTTPException(status_code=404, detail=str(e))
        return payload


@app.post("/invoices/{invoice_id}/submit_einvoice")
def submit_einvoice(invoice_id: int):
    # Simulated submission to GSTN/GSP; in real system we'd call external API and handle responses
    with next(database.get_session()) as session:
        try:
            payload = crud.build_einvoice_payload(session, invoice_id)
        except ValueError as e:
            raise HTTPException(status_code=404, detail=str(e))
        # simulate IRN generation
        irn = f"IRN-{invoice_id:06d}"
        inv = crud.mark_einvoice_submitted(session, invoice_id, irn, status="IRN_ASSIGNED")
        # record audit
        crud.record_einvoice_audit(session, inv.id, "IRN_ASSIGNED", f"IRN={irn}")
        return {"invoice_id": inv.id, "irn": irn, "status": inv.einvoice_status}


@app.post("/tds_deductions")
def add_tds_deduction(data: schemas.TDSDeductionCreate):
    with next(database.get_session()) as session:
        tds = models.TDSDeduction(
            payment_id=data.payment_id,
            amount=data.amount,
            tds_rate=data.tds_rate,
            tds_amount=data.tds_amount,
            section=data.section,
            date=data.date,
        )
        created = crud.create_tds_deduction(session, tds)
        return {"tds_id": created.id}


@app.post("/ewaybills")
def add_ewaybill(data: schemas.EWaybillCreate):
    with next(database.get_session()) as session:
        ewb = models.EWaybill(
            invoice_id=data.invoice_id,
            vehicle_number=data.vehicle_number,
            distance=data.distance,
            transporter_gstin=data.transporter_gstin,
            date=data.date,
        )
        created = crud.create_ewaybill(session, ewb)
        return {"ewaybill_id": created.id}


@app.get("/accounts/{account_id}/balance")
def account_balance(account_id: int, target_currency: str | None = None):
    with next(database.get_session()) as session:
        try:
            res = crud.get_account_balance(session, account_id, target_currency)
        except ValueError as e:
            raise HTTPException(status_code=404, detail=str(e))
        return res


@app.get("/reports/trial_balance")
def get_trial_balance(target_currency: str | None = None):
    with next(database.get_session()) as session:
        report = crud.trial_balance(session, target_currency)
        return {"rows": report}


@app.post("/fx/realize")
def fx_realize(invoice_id: int, payment_amount: float, payment_currency: str):
    with next(database.get_session()) as session:
        try:
            fx = crud.create_fx_realization(session, invoice_id, payment_amount, payment_currency, payment_currency.upper())
        except ValueError as e:
            raise HTTPException(status_code=404, detail=str(e))
        return {"fx_id": fx.id, "gain_loss": fx.gain_loss}


@app.get("/reports/gstr1")
def gstr1_report(start: str, end: str):
    # expects YYYY-MM-DD strings
    try:
        s = __import__('datetime').date.fromisoformat(start)
        e = __import__('datetime').date.fromisoformat(end)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid date format, expected YYYY-MM-DD")
    with next(database.get_session()) as session:
        summary = crud.summarize_gstr1(session, s, e)
        return summary


@app.get("/invoices/{invoice_id}/status")
def invoice_status(invoice_id: int):
    with next(database.get_session()) as session:
        try:
            st = crud.get_einvoice_status(session, invoice_id)
        except ValueError as e:
            raise HTTPException(status_code=404, detail=str(e))
        return st


@app.post("/invoices/{invoice_id}/attach_signed")
def attach_signed(invoice_id: int, data: schemas.SignedDocumentCreate):
    # For demo we accept a path; production would accept file upload and store securely
    with next(database.get_session()) as session:
        try:
            doc = crud.attach_signed_document(session, invoice_id, data.filename, data.path)
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))
        return {"doc_id": doc.id, "path": doc.path}


@app.post("/invoices/{invoice_id}/upload_signed")
def upload_signed(invoice_id: int, file: UploadFile = File(...), user=Depends(get_current_user_optional)):
    """Upload a signed PDF (multipart). Stores in S3 or local storage and records a SignedDocument.

    Authentication is optional for demos; in production `get_current_user_optional` should be replaced with a required auth dependency.
    """
    content = file.file.read()
    key = f"signed/{invoice_id}/{file.filename}"
    try:
        path = storage.upload_bytes(key, content, content_type=file.content_type)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    with next(database.get_session()) as session:
        doc = crud.attach_signed_document(session, invoice_id, file.filename, path)
        return {"doc_id": doc.id, "path": doc.path}


@app.post("/invoices/{invoice_id}/presign_signed")
def presign_signed(invoice_id: int, filename: str, user=Depends(get_current_user_optional)):
    """Return a presigned URL for uploading a signed file directly to S3/MinIO.

    Client should perform a PUT to the returned URL and then call the `attach_signed` endpoint
    with the returned storage path.
    """
    key = f"signed/{invoice_id}/{filename}"
    try:
        presigned = storage.presign_upload(key)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return {"upload": presigned, "storage_path": key}


@app.post("/invoices/{invoice_id}/apply_lut")
def apply_lut(invoice_id: int, lut_ref: str):
    """Mark an invoice as LUT-applied (export concession) with a reference."""
    with next(database.get_session()) as session:
        inv = session.get(models.Invoice, invoice_id)
        if not inv:
            raise HTTPException(status_code=404, detail="Invoice not found")
        inv.lut_applicable = True
        # store LUT reference in einvoice_status temporarily (demo). In production add a dedicated field.
        inv.einvoice_status = f"LUT:{lut_ref}"
        session.add(inv)
        session.commit()
        session.refresh(inv)
        return {"invoice_id": inv.id, "lut_ref": lut_ref}


@app.post("/webhooks/gstn")
def gstn_webhook(payload: schemas.GSTNWebhook):
    """Receive webhook callbacks from GSTN/GSP. Verifies signature and updates invoice status."""
    # verify signature
    sig = payload.signature
    text = f"{payload.irn}|{payload.status}"
    # verify nonce/timestamp and signature
    with next(database.get_session()) as session:
        try:
            crud.check_and_store_nonce(session, payload.nonce or '', payload.timestamp)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        from .gst_signing import verify_signature
        from .gsp_client import GSPClient, generate_rsa_keypair
        import os
        if sig is None or not verify_signature(f"{text}|{payload.nonce or ''}|{payload.timestamp or ''}", sig):
            raise HTTPException(status_code=400, detail="Invalid signature")
        try:
            inv = crud.update_einvoice_status_by_irn(session, payload.irn, payload.status)
        except ValueError as e:
            raise HTTPException(status_code=404, detail=str(e))
        return {"invoice_id": inv.id, "irn": inv.einvoice_irn, "status": inv.einvoice_status}


@app.post("/invoices/{invoice_id}/submit_to_gsp")
def submit_to_gsp(invoice_id: int):
    """Submit invoice payload to configured GSP. Uses RSA keys from env or simulated client if none configured."""
    with next(database.get_session()) as session:
        try:
            payload = crud.build_einvoice_payload(session, invoice_id)
        except ValueError as e:
            raise HTTPException(status_code=404, detail=str(e))
        # load keys and base url from env
        base_url = os.environ.get('GSP_BASE_URL')
        priv_pem = None
        pub_pem = None
        priv_path = os.environ.get('GSP_PRIVATE_PEM_PATH')
        pub_path = os.environ.get('GSP_PUBLIC_PEM_PATH')
        if priv_path:
            try:
                with open(priv_path, 'rb') as f:
                    priv_pem = f.read()
            except Exception:
                pass
        if pub_path:
            try:
                with open(pub_path, 'rb') as f:
                    pub_pem = f.read()
            except Exception:
                pass
        client = GSPClient(base_url=base_url, pem_private=priv_pem, pem_public=pub_pem)
        try:
            resp = client.submit_einvoice(payload)
        except Exception as e:
            raise HTTPException(status_code=502, detail=str(e))
        # on success, record IRN if returned
        irn = resp.get('irn')
        status = resp.get('status')
        if irn:
            inv = crud.mark_einvoice_submitted(session, invoice_id, irn, status=status or 'IRN_ASSIGNED')
            crud.record_einvoice_audit(session, invoice_id, 'GSP_SUBMISSION', f'irn={irn}')
            return {"invoice_id": invoice_id, "irn": irn, "status": inv.einvoice_status}
        return {"invoice_id": invoice_id, "response": resp}
