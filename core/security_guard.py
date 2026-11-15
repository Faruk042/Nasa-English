# -*- coding: utf-8 -*-
"""
ALTAR-NASA v6.3 Zero-Trust Isolation and Network Security Guard.
Defense Layers:
1. Loopback-only (`127.0.0.1` / `localhost`) client IP and Host header verification (DNS rebinding defense)
2. Cross-Origin / Cross-Site (`Origin` & `Sec-Fetch-Site`) blocking — wildcard CORS disabled
3. Cryptographic 192-bit per-session CSRF token (`X-Altar-CSRF`) validation
4. Hardened Content-Security-Policy (CSP), clickjacking (`X-Frame-Options: DENY`), and MIME protection
5. Socket/DNS-level private IP and cloud metadata SSRF blocker on outbound URL fetches
"""

from __future__ import annotations

import hmac
import ipaddress
import re
import secrets
import socket
from typing import Tuple
from urllib.parse import urlparse

from flask import Request, Response

_VALID_LOOPBACK_HOST_RE = re.compile(r"^(127\.0\.0\.1|localhost)(:\d{1,5})?$", re.IGNORECASE)


def generate_session_csrf_token() -> str:
    """Generate a unique 192-bit cryptographic session CSRF token at server startup."""
    return secrets.token_hex(24)


def verify_request_isolation(req: Request, expected_csrf_token: str) -> Tuple[bool, str]:
    """
    Validate incoming HTTP requests against DNS rebinding, cross-site request forgery, and non-loopback access.
    """
    # 1. Client IP check: accept strictly 127.0.0.1 / ::1 (or local Flask test_client)
    remote_ip = (req.remote_addr or "127.0.0.1").strip()
    if remote_ip not in ("127.0.0.1", "::1", "localhost"):
        return (False, "Forbidden: Non-loopback client rejected.")

    # 2. Host header verification (prevents DNS rebinding attacks)
    host_hdr = (req.headers.get("Host") or "").strip()
    if not host_hdr or not _VALID_LOOPBACK_HOST_RE.match(host_hdr):
        return (False, "Forbidden: Invalid Host header (DNS rebinding protection).")

    # 3. Browser Sec-Fetch-Site check: reject cross-site requests from external browser tabs
    sec_site = (req.headers.get("Sec-Fetch-Site") or "").strip().lower()
    if sec_site and sec_site not in ("same-origin", "none"):
        return (False, "Forbidden: Cross-site browser request blocked.")

    # 4. Origin header check: when present, permit only local http://127.0.0.1 or http://localhost
    origin_hdr = (req.headers.get("Origin") or "").strip()
    if origin_hdr:
        parsed_orig = urlparse(origin_hdr)
        if parsed_orig.scheme != "http" or not _VALID_LOOPBACK_HOST_RE.match(parsed_orig.netloc or ""):
            return (False, "Forbidden: Untrusted Origin blocked.")

    # 5. State-mutating API requests require constant-time X-Altar-CSRF verification
    if req.path.startswith("/api/") and req.method in ("POST", "PUT", "DELETE", "PATCH"):
        provided_token = (req.headers.get("X-Altar-CSRF") or "").strip()
        if not provided_token or not hmac.compare_digest(provided_token, expected_csrf_token):
            return (False, "Forbidden: Missing or invalid X-Altar-CSRF security token.")

    return (True, "ok")


def apply_hardened_security_headers(response: Response, is_api: bool = False) -> Response:
    """
    Apply strict browser and local-server headers against XSS, clickjacking, MIME sniffing, and data leakage.
    Wildcard CORS ('*') is never enabled.
    """
    # Strip any residual CORS headers
    response.headers.pop("Access-Control-Allow-Origin", None)
    response.headers.pop("Access-Control-Allow-Headers", None)
    response.headers.pop("Access-Control-Allow-Methods", None)

    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["Cross-Origin-Opener-Policy"] = "same-origin"
    response.headers["Cross-Origin-Resource-Policy"] = "same-origin"
    response.headers["Permissions-Policy"] = (
        "camera=(self), microphone=(), geolocation=(), payment=(), usb=(), bluetooth=(), magnetometer=()"
    )
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        "script-src 'self'; "
        "style-src 'self' 'unsafe-inline'; "
        "img-src 'self' data: blob:; "
        "media-src 'self' blob:; "
        "font-src 'self' data:; "
        "connect-src 'self'; "
        "object-src 'none'; "
        "base-uri 'self'; "
        "frame-ancestors 'none'; "
        "form-action 'self';"
    )

    if is_api:
        response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
        response.headers["Pragma"] = "no-cache"
    return response


def validate_external_url_strict(raw_url: str) -> Tuple[bool, str]:
    """
    SSRF (Server-Side Request Forgery) and DNS Rebinding Guard:
    - Accepts only `https://` or `http://` schemes on standard web ports (80/443).
    - Rejects URLs containing embedded credentials.
    - Resolves A/AAAA records via DNS and blocks private ranges (10.x, 192.168.x, 172.16-31.x),
      loopback (127.x, ::1), link-local / cloud metadata (169.254.169.254), and reserved addresses.
    """
    clean = (raw_url or "").strip().strip("'\"")
    if clean and not re.match(r"^[a-zA-Z][a-zA-Z0-9+\-.]*://", clean):
        if re.match(r"^[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}(/|$)", clean):
            clean = f"https://{clean}"
    if not clean or len(clean) > 2048:
        return (False, "Invalid or excessively long URL.")

    try:
        parsed = urlparse(clean)
    except Exception:
        return (False, "Failed to parse URL.")

    if parsed.scheme not in ("https", "http"):
        return (False, "Security policy permits only https:// or http:// schemes.")

    if parsed.username or parsed.password:
        return (False, "URLs containing embedded credentials are blocked by security policy.")

    hostname = (parsed.hostname or "").strip().lower()
    if not hostname or hostname in ("localhost", "localhost.localdomain", "broadcasthost", "metadata.google.internal"):
        return (False, "Access to loopback or internal metadata hosts is blocked by the SSRF guard.")

    if parsed.port and parsed.port not in (80, 443):
        return (False, "Security policy permits only standard web ports (80/443).")

    # Inspect direct IP literals and all resolved DNS A/AAAA records
    try:
        addr_infos = socket.getaddrinfo(
            hostname,
            parsed.port or (443 if parsed.scheme == "https" else 80),
            proto=socket.IPPROTO_TCP,
        )
    except Exception:
        # Check direct IP literal even if DNS lookup failed
        try:
            ip_direct = ipaddress.ip_address(hostname)
            if _is_forbidden_ip(ip_direct):
                return (False, f"Private or internal IP address ({ip_direct}) blocked by the SSRF guard.")
        except ValueError:
            pass
        return (False, f"Could not resolve hostname: {hostname}")

    if not addr_infos:
        return (False, "No routable public IP address found for hostname.")

    for info in addr_infos:
        sockaddr = info[4]
        ip_str = sockaddr[0]
        try:
            ip_obj = ipaddress.ip_address(ip_str)
            if _is_forbidden_ip(ip_obj):
                return (False, f"Security Block (SSRF Protection): {hostname} resolves to a private/local IP ({ip_str}).")
        except ValueError:
            return (False, "Invalid IP address response blocked.")

    return (True, clean)


def _is_forbidden_ip(ip_obj: ipaddress._BaseAddress) -> bool:
    return bool(
        ip_obj.is_private
        or ip_obj.is_loopback
        or ip_obj.is_link_local
        or ip_obj.is_multicast
        or ip_obj.is_reserved
        or ip_obj.is_unspecified
    )
