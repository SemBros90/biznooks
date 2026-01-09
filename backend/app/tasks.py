from typing import Optional
from .config import get_settings
from .gsp_client import GSPClient
from .database import engine
from sqlmodel import Session
from . import crud


def _worker_submit(invoice_id: int, payload: dict, use_sandbox: bool = False) -> dict:
    client = GSPClient()
    resp = client.submit_einvoice(payload, use_sandbox=use_sandbox)
    irn = resp.get('irn') or resp.get('reference')
    status = resp.get('status', 'SUBMITTED')
    with Session(engine) as session:
        try:
            if irn:
                crud.mark_einvoice_submitted(session, invoice_id, irn, status)
            crud.record_einvoice_audit(session, invoice_id, 'SUBMITTED_TO_GSP', str(resp))
        except Exception:
            # If DB update fails, still return response; in production log the error
            pass
    return resp


def enqueue_einvoice_submission(invoice_id: int, payload: dict, use_sandbox: bool = False) -> dict:
    settings = get_settings()
    # If REDIS configured, enqueue to RQ; otherwise run synchronously for local demos
    if settings.REDIS_URL:
        import redis
        import rq
        conn = redis.from_url(settings.REDIS_URL)
        q = rq.Queue(settings.GSP_QUEUE_NAME or 'gsp', connection=conn)
        job = q.enqueue(_worker_submit, invoice_id, payload, use_sandbox)
        return {'queued': True, 'job_id': job.id}
    else:
        resp = _worker_submit(invoice_id, payload, use_sandbox)
        return {'queued': False, 'result': resp}
