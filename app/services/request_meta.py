from typing import Dict, Optional

from fastapi import Request


def extract_client_ip(request: Request) -> Optional[str]:
    forwarded_for = request.headers.get("x-forwarded-for", "")
    if forwarded_for:
        # x-forwarded-for can be a comma-separated chain; first one is original client.
        first = forwarded_for.split(",")[0].strip()
        if first:
            return first

    for hdr in ("cf-connecting-ip", "x-real-ip"):
        value = (request.headers.get(hdr) or "").strip()
        if value:
            return value

    if request.client:
        return request.client.host
    return None


def extract_request_device_meta(request: Request) -> Dict[str, Optional[str]]:
    return {
        "ip": extract_client_ip(request),
        "x_forwarded_for": (request.headers.get("x-forwarded-for") or "")[:300],
        "x_real_ip": (request.headers.get("x-real-ip") or "")[:100],
        "cf_connecting_ip": (request.headers.get("cf-connecting-ip") or "")[:100],
        "user_agent": (request.headers.get("user-agent") or "")[:700],
        "accept_language": (request.headers.get("accept-language") or "")[:200],
        "referer": (request.headers.get("referer") or "")[:700],
        "sec_ch_ua": (request.headers.get("sec-ch-ua") or "")[:300],
        "sec_ch_ua_platform": (request.headers.get("sec-ch-ua-platform") or "")[:100],
        "sec_ch_ua_mobile": (request.headers.get("sec-ch-ua-mobile") or "")[:50],
    }
