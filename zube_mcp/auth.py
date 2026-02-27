"""Zube.io JWT authentication.

Zube uses RS256-signed JWTs. Flow:
1. Sign a short-lived refresh JWT with your private key
2. POST it to /api/users/tokens to get a 24-hour access JWT
3. Use the access JWT for all subsequent API calls
"""

from __future__ import annotations

import time
from pathlib import Path

import jwt


def load_private_key(path: str) -> str:
    return Path(path).read_text()


def create_refresh_jwt(client_id: str, private_key: str) -> str:
    now = int(time.time())
    payload = {
        "iat": now,
        "exp": now + 60,
        "iss": client_id,
    }
    return jwt.encode(payload, private_key, algorithm="RS256")
