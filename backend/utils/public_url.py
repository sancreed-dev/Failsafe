import os

from fastapi import Request


def get_public_api_base(request: Request) -> str:
    configured = os.getenv("FAILSAFE_PUBLIC_URL", "").strip().rstrip("/")
    if configured:
        return configured

    forwarded_proto = request.headers.get("x-forwarded-proto")
    forwarded_host = request.headers.get("x-forwarded-host") or request.headers.get("host")
    if forwarded_host:
        scheme = forwarded_proto or request.url.scheme
        return f"{scheme}://{forwarded_host}".rstrip("/")

    return str(request.base_url).rstrip("/")
