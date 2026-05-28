from datetime import datetime
import os
from typing import Optional

from fastapi import FastAPI, Header, HTTPException, Query, Path, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


SERVICE_NAME = os.getenv("SERVICE_NAME", "access-gate")
AUTH_TOKEN = os.getenv("AUTH_TOKEN", "lab-token")

app = FastAPI(
    title="Smart Campus — Access Gate Service",
    version="1.0.0",
    description="Access Gate service for FIT4110 Lab 04 Docker deployment.",
)


ACCESS_LOGS = [
    {
        "logType": "GRANTED",
        "logId": "log-001",
        "cardId": "card-001",
        "gateId": "gate-main",
        "direction": "IN",
        "timestamp": "2026-05-10T08:00:00Z",
        "status": "GRANTED",
        "personId": "SV001",
        "operatorNote": None,
        "grantedBy": "access-policy",
        "accessMode": "RFID",
    },
    {
        "logType": "DENIED",
        "logId": "log-002",
        "cardId": "card-009",
        "gateId": "gate-main",
        "direction": "OUT",
        "timestamp": "2026-05-10T08:05:00Z",
        "status": "DENIED",
        "personId": None,
        "operatorNote": "The dang bi khoa",
        "deniedReason": "CARD_BLOCKED",
        "accessMode": "RFID",
    },
]

GATES = {
    "gate-main": {
        "gateId": "gate-main",
        "gateName": "Cong chinh",
        "status": "ONLINE",
        "currentMode": "TWO_WAY",
        "lastUpdatedAt": "2026-05-10T08:00:00Z",
        "reason": None,
    },
    "gate-parking": {
        "gateId": "gate-parking",
        "gateName": "Cong nha xe",
        "status": "MAINTENANCE",
        "currentMode": "ENTRY_ONLY",
        "lastUpdatedAt": "2026-05-10T08:10:00Z",
        "reason": "Dang bao tri barrier chieu ra",
    },
}

CARDS = {
    "card-001": {
        "cardId": "card-001",
        "cardCode": "RFID-2026-001",
        "cardType": "RFID",
        "status": "ACTIVE",
        "issuedTo": "SV001",
        "validFrom": "2026-01-01",
        "validTo": "2026-12-31",
        "lastUsedAt": "2026-05-10T08:00:00Z",
        "note": None,
    },
    "card-009": {
        "cardId": "card-009",
        "cardCode": "RFID-2026-009",
        "cardType": "RFID",
        "status": "BLOCKED",
        "issuedTo": "SV009",
        "validFrom": "2026-01-01",
        "validTo": "2026-12-31",
        "lastUsedAt": "2026-05-09T17:30:00Z",
        "note": "The bi khoa do bao mat",
    },
}


def problem(status_code: int, title: str, detail: str, instance: str = ""):
    return {
        "type": "https://campus.local/errors/access-gate",
        "title": title,
        "status": status_code,
        "detail": detail,
        "instance": instance,
        "correlationId": None,
        "errors": [],
    }


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={
            "type": "https://campus.local/errors/validation",
            "title": "Validation Error",
            "status": 422,
            "detail": "Request validation failed",
            "instance": str(request.url.path),
            "correlationId": request.headers.get("X-Correlation-Id"),
            "errors": [
                {
                    "field": ".".join(str(part) for part in error.get("loc", [])),
                    "code": error.get("type", "VALIDATION_ERROR"),
                    "message": error.get("msg", "Invalid value"),
                }
                for error in exc.errors()
            ],
        },
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    if isinstance(exc.detail, dict) and "status" in exc.detail:
        return JSONResponse(status_code=exc.status_code, content=exc.detail)

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "type": "https://campus.local/errors/access-gate",
            "title": "HTTP Error",
            "status": exc.status_code,
            "detail": str(exc.detail),
            "instance": str(request.url.path),
            "correlationId": request.headers.get("X-Correlation-Id"),
            "errors": [],
        },
    )


def require_auth(authorization: Optional[str]) -> None:
    expected = f"Bearer {AUTH_TOKEN}"
    if not authorization or authorization.strip() != expected:
        raise HTTPException(
            status_code=401,
            detail=problem(
                401,
                "Unauthorized",
                "Missing or invalid Bearer token",
            ),
        )


@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": SERVICE_NAME,
        "time": datetime.utcnow().isoformat() + "Z",
    }


@app.get("/access/logs/recent")
def get_recent_access_logs(
    authorization: Optional[str] = Header(default=None, alias="Authorization"),
    x_correlation_id: Optional[str] = Header(default=None, alias="X-Correlation-Id"),
    cursor: Optional[str] = Query(default=None, min_length=1, max_length=200),
    limit: int = Query(default=20, ge=1, le=100),
    gateId: Optional[str] = Query(default=None),
    cardId: Optional[str] = Query(default=None),
    direction: Optional[str] = Query(default=None, pattern="^(IN|OUT)$"),
    status: Optional[str] = Query(default=None, pattern="^(GRANTED|DENIED|ERROR)$"),
    from_time: Optional[str] = Query(default=None, alias="from"),
    to_time: Optional[str] = Query(default=None, alias="to"),
):
    require_auth(authorization)

    items = ACCESS_LOGS

    if gateId:
        items = [item for item in items if item["gateId"] == gateId]

    if cardId:
        items = [item for item in items if item["cardId"] == cardId]

    if direction:
        items = [item for item in items if item["direction"] == direction]

    if status:
        items = [item for item in items if item["status"] == status]

    return {
        "items": items[:limit],
        "nextCursor": None,
        "hasMore": False,
    }


@app.get("/access/logs/{logId}")
def get_access_log_by_id(
    logId: str = Path(..., pattern=r"^log-[a-zA-Z0-9-]{3,64}$"),
    authorization: Optional[str] = Header(default=None, alias="Authorization"),
    x_correlation_id: Optional[str] = Header(default=None, alias="X-Correlation-Id"),
):
    require_auth(authorization)

    for item in ACCESS_LOGS:
        if item["logId"] == logId:
            return item

    raise HTTPException(
        status_code=404,
        detail=problem(
            404,
            "Not Found",
            "Access log not found",
            f"/access/logs/{logId}",
        ),
    )


@app.get("/gates")
def list_gates(
    authorization: Optional[str] = Header(default=None, alias="Authorization"),
    x_correlation_id: Optional[str] = Header(default=None, alias="X-Correlation-Id"),
    cursor: Optional[str] = Query(default=None),
    limit: int = Query(default=20, ge=1, le=100),
):
    require_auth(authorization)

    return {
        "items": list(GATES.values())[:limit],
        "nextCursor": None,
        "hasMore": False,
    }


@app.get("/gates/{gateId}/status")
def get_gate_status(
    gateId: str = Path(..., pattern=r"^gate-[a-z0-9-]{2,40}$"),
    authorization: Optional[str] = Header(default=None, alias="Authorization"),
    x_correlation_id: Optional[str] = Header(default=None, alias="X-Correlation-Id"),
):
    require_auth(authorization)

    gate = GATES.get(gateId)
    if not gate:
        raise HTTPException(
            status_code=404,
            detail=problem(
                404,
                "Not Found",
                "Gate not found",
                f"/gates/{gateId}/status",
            ),
        )

    return gate


@app.get("/cards/{cardId}")
def get_card_by_id(
    cardId: str = Path(..., pattern=r"^card-[a-zA-Z0-9-]{3,64}$"),
    authorization: Optional[str] = Header(default=None, alias="Authorization"),
    x_correlation_id: Optional[str] = Header(default=None, alias="X-Correlation-Id"),
):
    require_auth(authorization)

    card = CARDS.get(cardId)
    if not card:
        raise HTTPException(
            status_code=404,
            detail=problem(
                404,
                "Not Found",
                "Card not found",
                f"/cards/{cardId}",
            ),
        )

    return card