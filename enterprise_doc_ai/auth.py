"""Fail-closed local demo identity: short-lived HMAC-SHA256 bearer tokens.

This is NOT enterprise authentication, OIDC, JWT federation, token revocation
or an identity provider. Only the operator holding the local signing key can
mint identities. Do not expose the demo API to a public network.
"""
from __future__ import annotations

import argparse
import base64
from dataclasses import dataclass
import hashlib
import hmac
import json
import os
import re
import secrets
import time
from typing import Callable

from .engine import Principal

SECRET_ENV = "ENTERPRISE_DOC_AI_DEMO_SECRET"
MAX_TTL_SECONDS = 3600
ALLOWED_SCOPES = frozenset({"read", "extract", "review", "approve"})
ALLOWED_ROLES = frozenset({
    "employee", "hr", "it", "security", "finance", "procurement",
    "legal", "manager", "sales", "support", "operations", "approver",
})
IDENTITY_PATTERN = re.compile(r"[A-Za-z0-9_.:@-]{1,100}\Z")
TENANT_PATTERN = re.compile(r"[A-Za-z0-9_-]{1,48}\Z")
B64_PATTERN = re.compile(r"[A-Za-z0-9_-]+\Z")

class AuthenticationError(ValueError):
    """A token cannot be trusted."""

class SecurityConfigurationError(RuntimeError):
    """No suitably strong demo signing key has been configured."""

@dataclass(frozen=True)
class VerifiedIdentity:
    principal: Principal
    scopes: frozenset[str]
    issued_at: int
    expires_at: int

def _secret_bytes() -> bytes:
    value = os.environ.get(SECRET_ENV, "")
    key = value.encode("utf-8")
    if len(key) < 32:
        raise SecurityConfigurationError(
            f"{SECRET_ENV} must contain at least 32 bytes of locally generated secret"
        )
    return key

def _encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode("ascii").rstrip("=")

def _decode(text: str) -> bytes:
    if not B64_PATTERN.fullmatch(text) or len(text) > 4000:
        raise AuthenticationError("Malformed token encoding")
    try:
        binary = base64.b64decode(text + "=" * (-len(text) % 4), altchars=b"-_", validate=True)
    except (ValueError, base64.binascii.Error) as exc:
        raise AuthenticationError("Malformed token encoding") from exc
    if _encode(binary) != text:
        raise AuthenticationError("Noncanonical token encoding")
    return binary

def _validated_identity(tenant: object, subject: object, roles: object, scopes: object) -> tuple[str, str, frozenset[str], frozenset[str]]:
    if not isinstance(tenant, str) or not TENANT_PATTERN.fullmatch(tenant):
        raise AuthenticationError("Invalid tenant")
    if not isinstance(subject, str) or not IDENTITY_PATTERN.fullmatch(subject):
        raise AuthenticationError("Invalid subject")
    if not isinstance(roles, list) or not roles or any(
        not isinstance(role, str) or role not in ALLOWED_ROLES for role in roles
    ) or len(set(roles)) != len(roles):
        raise AuthenticationError("Invalid roles")
    if not isinstance(scopes, list) or not scopes or any(
        not isinstance(scope, str) or scope not in ALLOWED_SCOPES for scope in scopes
    ) or len(set(scopes)) != len(scopes):
        raise AuthenticationError("Invalid scopes")
    return tenant, subject, frozenset(roles), frozenset(scopes)

def mint_local_token(
    tenant: str,
    subject: str,
    roles: list[str],
    scopes: list[str],
    ttl_seconds: int = 900,
    now: int | None = None,
) -> str:
    """Operator-side issuance only. There is deliberately no HTTP mint endpoint."""
    key = _secret_bytes()
    tenant, subject, roles_set, scope_set = _validated_identity(tenant, subject, roles, scopes)
    if type(ttl_seconds) is not int or not 1 <= ttl_seconds <= MAX_TTL_SECONDS:
        raise ValueError("Token lifetime must be 1 to 3600 seconds")
    issued = int(time.time()) if now is None else int(now)
    claims = {
        "version": 1, "issuer": "enterprise-doc-ai-local",
        "audience": "enterprise-doc-ai-demo",
        "tenant": tenant, "subject": subject,
        "roles": sorted(roles_set), "scopes": sorted(scope_set),
        "issued_at": issued, "expires_at": issued + ttl_seconds,
    }
    encoded = _encode(json.dumps(claims, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("ascii"))
    mac = _encode(hmac.new(key, encoded.encode("ascii"), hashlib.sha256).digest())
    return encoded + "." + mac

def _no_duplicate_keys(pairs: list[tuple[str, object]]) -> dict:
    out = {}
    for key, value in pairs:
        if key in out:
            raise AuthenticationError("Duplicate token claim")
        out[key] = value
    return out

def verify_local_token(token: str, now: int | None = None) -> VerifiedIdentity:
    """Verify integrity, issuer, audience, identities, scopes, and short expiry."""
    key = _secret_bytes()  # Missing secret means service cannot authenticate anyone.
    if not isinstance(token, str) or len(token) > 4096 or token.count(".") != 1:
        raise AuthenticationError("Invalid bearer token")
    payload, mac = token.split(".", 1)
    signature = _decode(mac)
    if len(signature) != hashlib.sha256().digest_size:
        raise AuthenticationError("Invalid signature size")
    expected = hmac.new(key, payload.encode("ascii", errors="ignore"), hashlib.sha256).digest()
    if not hmac.compare_digest(signature, expected):
        raise AuthenticationError("Invalid signature")
    try:
        obj = json.loads(_decode(payload), object_pairs_hook=_no_duplicate_keys)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise AuthenticationError("Invalid token payload") from exc
    if not isinstance(obj, dict) or set(obj) != {
        "version", "issuer", "audience", "tenant", "subject",
        "roles", "scopes", "issued_at", "expires_at",
    } or obj["version"] != 1 or obj["issuer"] != "enterprise-doc-ai-local" or obj["audience"] != "enterprise-doc-ai-demo":
        raise AuthenticationError("Invalid token claims")
    issued, expires = obj["issued_at"], obj["expires_at"]
    current = int(time.time()) if now is None else int(now)
    if type(issued) is not int or type(expires) is not int or (
        issued > current + 30 or expires <= current or
        expires <= issued or expires - issued > MAX_TTL_SECONDS
    ):
        raise AuthenticationError("Expired or invalid token lifetime")
    tenant, subject, roles, scopes = _validated_identity(
        obj["tenant"], obj["subject"], obj["roles"], obj["scopes"]
    )
    return VerifiedIdentity(Principal(tenant, roles, subject), scopes, issued, expires)

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Create a local signed demo token. Never expose the signing key."
    )
    parser.add_argument("command", choices=["mint"])
    parser.add_argument("--tenant", required=True)
    parser.add_argument("--subject", required=True)
    parser.add_argument("--roles", required=True, help="Comma-separated simulated roles")
    parser.add_argument("--scopes", default="read", help="read,extract,review,approve")
    parser.add_argument("--ttl", type=int, default=900)
    args = parser.parse_args()
    print(mint_local_token(
        args.tenant, args.subject, args.roles.split(","), args.scopes.split(","), args.ttl
    ))

if __name__ == "__main__":
    main()
