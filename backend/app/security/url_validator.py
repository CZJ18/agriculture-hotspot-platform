import ipaddress
import socket
from dataclasses import dataclass
from urllib.parse import urlparse, urlunparse


BLOCKED_HOSTS = {"localhost", "localhost.localdomain"}
BLOCKED_IPS = {ipaddress.ip_address("169.254.169.254")}
ALLOWED_SCHEMES = {"http", "https"}
BLOCKED_EXTENSIONS = (
    ".7z",
    ".apk",
    ".dmg",
    ".exe",
    ".gz",
    ".mp3",
    ".mp4",
    ".mov",
    ".msi",
    ".rar",
    ".tar",
    ".tgz",
    ".wav",
    ".webm",
    ".zip",
)


class URLValidationError(ValueError):
    pass


@dataclass(frozen=True)
class ValidatedURL:
    normalized_url: str
    hostname: str
    scheme: str


def _is_blocked_ip(ip: ipaddress._BaseAddress) -> bool:
    return (
        ip in BLOCKED_IPS
        or ip.is_private
        or ip.is_loopback
        or ip.is_link_local
        or ip.is_multicast
        or ip.is_reserved
        or ip.is_unspecified
    )


def _resolve_host(hostname: str) -> list[ipaddress._BaseAddress]:
    try:
        raw_addresses = socket.getaddrinfo(hostname, None, type=socket.SOCK_STREAM)
    except socket.gaierror as exc:
        raise URLValidationError(f"Unable to resolve host: {hostname}") from exc

    addresses: list[ipaddress._BaseAddress] = []
    for item in raw_addresses:
        address = item[4][0]
        try:
            addresses.append(ipaddress.ip_address(address))
        except ValueError as exc:
            raise URLValidationError(f"Invalid resolved address: {address}") from exc
    return addresses


def validate_url(url: str, *, resolve_dns: bool = False) -> ValidatedURL:
    parsed = urlparse((url or "").strip())
    if parsed.scheme.lower() not in ALLOWED_SCHEMES:
        raise URLValidationError("Only http and https URLs are allowed.")
    if not parsed.hostname:
        raise URLValidationError("URL must include a hostname.")

    hostname = parsed.hostname.strip().lower().rstrip(".")
    if hostname in BLOCKED_HOSTS:
        raise URLValidationError("Localhost targets are not allowed.")

    try:
        direct_ip = ipaddress.ip_address(hostname.strip("[]"))
    except ValueError:
        direct_ip = None

    if direct_ip and _is_blocked_ip(direct_ip):
        raise URLValidationError("Private, local, link-local, or metadata IP targets are not allowed.")

    if resolve_dns and not direct_ip:
        for resolved_ip in _resolve_host(hostname):
            if _is_blocked_ip(resolved_ip):
                raise URLValidationError("Hostname resolves to a blocked address.")

    netloc = parsed.netloc.lower()
    normalized = urlunparse((parsed.scheme.lower(), netloc, parsed.path or "/", "", parsed.query, ""))
    return ValidatedURL(normalized_url=normalized, hostname=hostname, scheme=parsed.scheme.lower())


def fetch_public_text(url: str) -> tuple[str, str]:
    import requests

    from app.config import get_settings

    settings = get_settings()
    current = validate_url(url, resolve_dns=True).normalized_url
    session = requests.Session()
    session.headers.update(
        {
            "User-Agent": "HotspotAISystem/0.1 (+public metadata fetcher)",
            "Accept": "text/html,application/xhtml+xml,text/plain;q=0.8",
        }
    )

    for _ in range(settings.max_redirects + 1):
        parsed = urlparse(current)
        if parsed.path.lower().endswith(BLOCKED_EXTENSIONS):
            raise URLValidationError("Binary, archive, executable, audio, and video downloads are not allowed.")

        response = session.get(
            current,
            timeout=settings.request_timeout_seconds,
            allow_redirects=False,
            stream=True,
        )
        if response.is_redirect:
            location = response.headers.get("Location")
            if not location:
                raise URLValidationError("Redirect target is missing.")
            current = requests.compat.urljoin(current, location)
            current = validate_url(current, resolve_dns=True).normalized_url
            continue

        response.raise_for_status()
        content_type = response.headers.get("Content-Type", "").lower()
        if not (
            content_type.startswith("text/html")
            or content_type.startswith("text/plain")
            or content_type.startswith("application/xhtml+xml")
        ):
            raise URLValidationError("Only text/html, application/xhtml+xml, and text/plain responses are accepted.")

        chunks: list[bytes] = []
        size = 0
        for chunk in response.iter_content(chunk_size=8192):
            if not chunk:
                continue
            size += len(chunk)
            if size > settings.max_response_bytes:
                raise URLValidationError("Response is larger than the allowed limit.")
            chunks.append(chunk)
        response.encoding = response.encoding or "utf-8"
        return b"".join(chunks).decode(response.encoding, errors="replace"), current

    raise URLValidationError("Too many redirects.")
