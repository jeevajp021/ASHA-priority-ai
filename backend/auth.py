"""
Lightweight session token auth — no external JWT library.
Token = base64(worker_id:role:timestamp) signed with a fixed secret using hmac-sha256.
Suitable for POC demo; swap for proper JWT in production.
"""
import hmac, hashlib, base64, time
from fastapi import Header, HTTPException, Depends
from sqlalchemy.orm import Session
from database import get_db
import models

SECRET = "asha-poc-secret-2026"   # hardcoded for demo; move to env var in prod

def _make_token(worker_id: int, role: str) -> str:
    payload = f"{worker_id}:{role}:{int(time.time())}"
    sig = hmac.new(SECRET.encode(), payload.encode(), hashlib.sha256).hexdigest()[:16]
    return base64.b64encode(f"{payload}:{sig}".encode()).decode()

def _parse_token(token: str):
    try:
        decoded = base64.b64decode(token.encode()).decode()
        parts = decoded.rsplit(":", 1)          # split off sig from the right
        payload, sig = parts[0], parts[1]
        expected = hmac.new(SECRET.encode(), payload.encode(), hashlib.sha256).hexdigest()[:16]
        if not hmac.compare_digest(sig, expected):
            return None
        wid, role, ts = payload.split(":")
        if time.time() - int(ts) > 86400:       # 24-hour expiry
            return None
        return {"worker_id": int(wid), "role": role}
    except Exception:
        return None

def create_token(worker_id: int, role: str) -> str:
    return _make_token(worker_id, role)

def get_current_worker(x_auth_token: str = Header(...),
                        db: Session = Depends(get_db)):
    """Dependency: validates token, returns AshaWorker ORM object."""
    claims = _parse_token(x_auth_token)
    if not claims:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    worker = db.query(models.AshaWorker).filter(
        models.AshaWorker.id == claims["worker_id"]
    ).first()
    if not worker:
        raise HTTPException(status_code=401, detail="Worker not found")
    return worker

def require_role(*roles):
    """Factory: returns a FastAPI dependency that enforces allowed roles."""
    def _check(worker: models.AshaWorker = Depends(get_current_worker)):
        if worker.role not in roles:
            raise HTTPException(status_code=403, detail=f"Requires role: {roles}")
        return worker
    return _check