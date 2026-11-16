"""Adversarial tests for locally signed identities. No external dependencies."""
import base64
import hashlib
import hmac
import json
import os
import time
import unittest
from unittest.mock import patch

from enterprise_doc_ai.auth import (
    AuthenticationError, SecurityConfigurationError, SECRET_ENV,
    mint_local_token, verify_local_token,
)

KEY = "local-integration-tests-secret-" + "a" * 40

def _alter_claim_and_resign(token: str, claim: str, value, key: str = KEY) -> str:
    payload, _ = token.split(".")
    doc = json.loads(base64.urlsafe_b64decode(payload + "=" * (-len(payload) % 4)))
    doc[claim] = value
    data = base64.urlsafe_b64encode(
        json.dumps(doc, separators=(",", ":"), sort_keys=True).encode()
    ).decode().rstrip("=")
    sig = base64.urlsafe_b64encode(
        hmac.new(key.encode(), data.encode(), hashlib.sha256).digest()
    ).decode().rstrip("=")
    return data + "." + sig

class AuthTests(unittest.TestCase):
    def setUp(self):
        self.patch = patch.dict(os.environ, {SECRET_ENV: KEY})
        self.patch.start()

    def tearDown(self):
        self.patch.stop()

    def mint(self, **kwargs):
        return mint_local_token("alpha", "alice", ["employee"], ["read"], **kwargs)

    def test_valid_signed_identity(self):
        ident = verify_local_token(self.mint())
        self.assertEqual(ident.principal.tenant, "alpha")
        self.assertEqual(ident.principal.subject, "alice")
        self.assertEqual(ident.principal.roles, frozenset({"employee"}))
        self.assertEqual(ident.scopes, frozenset({"read"}))

    def test_expired_and_not_yet_valid(self):
        old = self.mint(now=int(time.time()) - 2000, ttl_seconds=900)
        with self.assertRaises(AuthenticationError):
            verify_local_token(old)
        future = self.mint(now=int(time.time()) + 500)
        with self.assertRaises(AuthenticationError):
            verify_local_token(future)

    def test_maximum_lifetime(self):
        with self.assertRaises(ValueError):
            self.mint(ttl_seconds=3601)
        with self.assertRaises(ValueError):
            self.mint(ttl_seconds=0)
        bad = _alter_claim_and_resign(self.mint(), "expires_at", int(time.time()) + 50000)
        with self.assertRaises(AuthenticationError):
            verify_local_token(bad)

    def test_signature_tampering(self):
        token = self.mint()
        data, mac = token.split(".")
        tampered = data + "." + ("A" if mac[0] != "A" else "B") + mac[1:]
        with self.assertRaises(AuthenticationError):
            verify_local_token(tampered)

    def test_forged_tenant_and_role(self):
        token = self.mint()
        for claim, value in [("tenant", "beta"), ("roles", ["hr"]), ("scopes", ["approve"])]:
            raw, mac = token.split(".")
            doc = json.loads(base64.urlsafe_b64decode(raw + "=" * (-len(raw) % 4)))
            doc[claim] = value
            forged_data = base64.urlsafe_b64encode(json.dumps(doc).encode()).decode().rstrip("=")
            with self.assertRaises(AuthenticationError):
                verify_local_token(forged_data + "." + mac)

    def test_bad_issuer_or_audience_even_with_valid_signature(self):
        for claim, value in [("issuer", "evil"), ("audience", "other-app"), ("version", 99)]:
            with self.assertRaises(AuthenticationError):
                verify_local_token(_alter_claim_and_resign(self.mint(), claim, value))

    def test_bad_types_and_extra_fields(self):
        for claim, value in [("issued_at", True), ("expires_at", "tomorrow"), ("roles", ["root"]),
                             ("roles", ["employee", "employee"]), ("scopes", ["all"]),
                             ("tenant", "../../beta"), ("subject", "alice\nboss")]:
            with self.subTest(claim=claim, value=str(value)), self.assertRaises(AuthenticationError):
                verify_local_token(_alter_claim_and_resign(self.mint(), claim, value))

    def test_absent_or_weak_secret_is_fail_closed(self):
        for value in ("", "short"):
            with patch.dict(os.environ, {SECRET_ENV: value}):
                with self.assertRaises(SecurityConfigurationError):
                    mint_local_token("alpha", "alice", ["employee"], ["read"])
                with self.assertRaises(SecurityConfigurationError):
                    verify_local_token(self.mint() if False else "invalid.token")

    def test_rotation_revokes_old_signatures(self):
        issued = self.mint()
        with patch.dict(os.environ, {SECRET_ENV: "rotated-" + "z" * 48}):
            with self.assertRaises(AuthenticationError):
                verify_local_token(issued)

    def test_malformed_tokens_and_limits(self):
        for token in ("", "not-a-token", "a.b.c", "x" * 10000, "*.*", "____.____"):
            with self.subTest(token=token[:16]), self.assertRaises(AuthenticationError):
                verify_local_token(token)

if __name__ == "__main__":
    unittest.main()
