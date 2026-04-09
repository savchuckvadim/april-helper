import hashlib
import hmac
import os
import time

from fastapi import Header, HTTPException, status


class AdminAuthService:
    @staticmethod
    def _parse_domain_allowlist() -> set[str]:
        raw = os.getenv("AI_ADMIN_DOMAIN_ALLOWLIST", "")
        return {item.strip().lower() for item in raw.split(",") if item.strip()}

    @staticmethod
    def verify_domain_allowed(domain: str) -> None:
        allowlist = AdminAuthService._parse_domain_allowlist()
        if allowlist and domain.lower() not in allowlist:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Domain is not allowed")

    @staticmethod
    def verify_signature(domain: str, token: str, ts: int) -> None:
        secret = os.getenv("AI_ADMIN_SIGNED_TOKEN_SECRET")
        if not secret:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="AI_ADMIN_SIGNED_TOKEN_SECRET is not configured",
            )
        ttl = int(os.getenv("AI_ADMIN_SIGNED_TOKEN_TTL_SECONDS", "900"))
        now = int(time.time())
        if abs(now - ts) > ttl:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token timestamp expired")

        payload = f"{domain}:{ts}".encode("utf-8")
        expected = hmac.new(secret.encode("utf-8"), payload, hashlib.sha256).hexdigest()
        if not hmac.compare_digest(expected, token):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token signature")


def admin_auth_dependency(
    domain: str,
    x_admin_token: str = Header(..., alias="X-Admin-Token"),
    x_admin_ts: int = Header(..., alias="X-Admin-Ts"),
) -> None:
    AdminAuthService.verify_domain_allowed(domain)
    AdminAuthService.verify_signature(domain=domain, token=x_admin_token, ts=x_admin_ts)

