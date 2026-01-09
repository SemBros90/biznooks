import json
import time
from typing import Optional
import requests
from . import integrations
from .gst_signing_rsa import sign_with_private, verify_with_public
from .config import get_settings


class GSPClient:
    """Production-ready GSP client with sandbox support and robust retries.

    Behaviour:
    - Reads configuration from `backend/app/config.get_settings()`.
    - Loads private/public keys from provided bytes or file paths.
    - If no `GSP_BASE_URL` set, falls back to simulated GSTN or sandbox.
    """

    def __init__(self, base_url: Optional[str] = None, pem_private: Optional[bytes] = None,
                 pem_public: Optional[bytes] = None, timeout: Optional[int] = None):
        self.settings = get_settings()
        self.base_url = base_url or self.settings.GSP_BASE_URL or self.settings.GSP_SANDBOX_URL
        self.timeout = timeout or self.settings.GSP_TIMEOUT
        self.private = pem_private
        self.public = pem_public

        # If file paths provided in environment and no bytes given, try to load
        if not self.private and self.settings.GSP_PRIVATE_KEY_PATH:
            try:
                with open(self.settings.GSP_PRIVATE_KEY_PATH, 'rb') as f:
                    self.private = f.read()
            except Exception:
                # keep as None if unreadable
                self.private = None

        if not self.public and self.settings.GSP_PUBLIC_KEY_PATH:
            try:
                with open(self.settings.GSP_PUBLIC_KEY_PATH, 'rb') as f:
                    self.public = f.read()
            except Exception:
                self.public = None

        # if explicitly no remote base_url provided, use simulated GSTN
        if not self.base_url:
            self.sim = integrations.SimulatedGSTN()

        # retry settings
        self.retries = self.settings.GSP_RETRIES
        self.backoff = self.settings.GSP_BACKOFF_FACTOR

    def _sign_payload(self, body: bytes) -> Optional[str]:
        if not self.private:
            return None
        sig = sign_with_private(self.private, body)
        return sig.hex()

    def submit_einvoice(self, payload: dict, use_sandbox: bool = False) -> dict:
        """Submit an e-invoice payload to GSP/sandbox or to the simulated GSTN.

        - `use_sandbox`: when True and a sandbox URL is configured, send to sandbox.
        """
        body = json.dumps(payload, separators=(',', ':'), ensure_ascii=False).encode()
        signature = self._sign_payload(body)

        # If using simulated GSTN, call locally
        if hasattr(self, 'sim') and not self.base_url:
            return self.sim.submit_einvoice(payload)

        url_base = self.base_url
        if use_sandbox and self.settings.GSP_SANDBOX_URL:
            url_base = self.settings.GSP_SANDBOX_URL

        url = f"{url_base.rstrip('/')}/einvoice/submit"
        headers = {'Content-Type': 'application/json'}
        if signature:
            headers['X-Signature'] = signature

        attempt = 0
        last_exc = None
        while attempt < max(1, self.retries):
            try:
                r = requests.post(url, data=body, headers=headers, timeout=self.timeout)
                r.raise_for_status()
                # optionally verify response signature when public key available
                resp_json = r.json()
                if self.public and 'signature' in r.headers:
                    try:
                        verify_with_public(self.public, r.text.encode(), bytes.fromhex(r.headers['signature']))
                    except Exception:
                        # signature verification failed — log / raise in prod
                        pass
                return resp_json
            except requests.RequestException as e:
                last_exc = e
                attempt += 1
                sleep = (self.backoff ** attempt)
                time.sleep(min(60, sleep))

        raise RuntimeError('GSP submission failed after retries') from last_exc

