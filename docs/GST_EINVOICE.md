# GST e-Invoicing (prototype)

This document describes the simulated e-invoicing payload and flow implemented in the demo.

- Endpoint: `GET /invoices/{invoice_id}/einvoice_payload` — returns a JSON payload ready for GSTN/GSP submission.
- Endpoint: `POST /invoices/{invoice_id}/submit_einvoice` — simulates submission and assigns a mock IRN.

Notes:
- Real integration requires signing payloads, calling a GSP or GSTN endpoint, handling error responses, and storing signed documents and IRN details.
- For export invoices, set `lut_applicable = true` and provide `iec` when required.

## TDS (Tax Deducted at Source)

- Endpoint: `POST /tds_deductions` — creates a TDS deduction record.
- Model: Tracks deductions on payments, with section (e.g., 195 for non-residents), rate, and amount.
- Notes: In production, integrate with TRACES for filing quarterly returns.

## E-Waybill

- Endpoint: `POST /ewaybills` — creates an e-waybill for goods movement.
- Model: Linked to invoice, includes vehicle details, distance, transporter GSTIN.
- Notes: Real integration with GST portal for generation and cancellation.


## E-Invoice Status & Signed Documents

- Endpoint: `GET /invoices/{invoice_id}/status` — returns current IRN, status and recent audit events.
- Endpoint: `POST /invoices/{invoice_id}/attach_signed` — attach a signed document (accepts filename + path in demo).

Notes:
- In production, signed payloads and signed PDFs should be stored in secure object storage with access controls; change history and audit trail must be immutable.
- Status polling should be implemented with retries and webhook callbacks from GSP/GSTN when available.
