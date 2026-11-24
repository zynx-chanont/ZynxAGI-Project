"""
ZynxAGI - Internal Service Authentication Dependency (S2S Security)
===================================================================
Provides token verification for Service-to-Service communication between
Zynx Gateway and Python Core.
"""

import hmac
import logging
import os
from typing import Optional

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from ..config.settings import settings

logger = logging.getLogger(__name__)

http_bearer = HTTPBearer(auto_error=False)


def verify_service_token(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(http_bearer),
) -> str:
    """
    Validate internal service token for Service-to-Service communication.
    Accepts ZYNX_INTERNAL_SERVICE_TOKEN or ZYNX_SERVICE_TOKEN.
    In development mode (DEBUG=True and no token configured), permits access with debug log.
    In production mode (DEBUG=False or token configured), strictly rejects missing or invalid tokens.
    """
    configured_token = (
        getattr(settings, "ZYNX_INTERNAL_SERVICE_TOKEN", None)
        or os.getenv("ZYNX_INTERNAL_SERVICE_TOKEN")
        or getattr(settings, "ZYNX_SERVICE_TOKEN", None)
        or os.getenv("ZYNX_SERVICE_TOKEN")
    )

    if not configured_token:
        if settings.DEBUG:
            logger.debug("ZYNX_SERVICE_TOKEN not configured; permitting call in DEBUG mode")
            return "dev-unauthenticated"
        raise HTTPException(
            status_code=500,
            detail="Server security configuration error: ZYNX_SERVICE_TOKEN not configured in production",
        )

    if not credentials or not credentials.credentials:
        raise HTTPException(
            status_code=401,
            detail="Missing Authorization header or Bearer token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Constant-time comparison to prevent timing attacks
    if not hmac.compare_digest(credentials.credentials.strip(), configured_token.strip()):
        raise HTTPException(
            status_code=401,
            detail="Invalid service token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return credentials.credentials
