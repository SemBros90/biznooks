"""Run an RQ worker for processing background jobs.

Usage: set `REDIS_URL` in env and run `python backend/worker.py`.
If `REDIS_URL` is not set, prints instructions.
"""
import os

REDIS_URL = os.environ.get('REDIS_URL')

if not REDIS_URL:
    print('REDIS_URL not configured. To run background workers set REDIS_URL and run an RQ worker:')
    print('  pip install rq redis')
    print('  REDIS_URL=redis://localhost:6379 python -m rq worker gsp')
    raise SystemExit(1)

from redis import from_url
from rq import Worker, Queue, Connection

conn = from_url(REDIS_URL)
with Connection(conn):
    q = Queue('gsp')
    worker = Worker([q])
    print('Starting RQ worker for queue: gsp')
    worker.work()
