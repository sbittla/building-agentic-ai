"""Chapter 11 (and 14): fetching web pages safely.

An agent that fetches URLs is a network client that ANYONE can steer: a page, a
file or an issue can contain a URL. Two dangers:
- SSRF: the URL points INSIDE your network (http://169.254.169.254/,
  http://localhost:8080, a 10.x address) and the agent reads something only your
  machine should see.
- Exfiltration: the URL points OUT, with your data in it
  (https://evil.example/?d=<notes>).
url_problem() handles the first; chapter 14's policy layer handles the second."""
import ipaddress
import re
import socket
from urllib.parse import urljoin, urlsplit
import httpx

def url_problem(url: str, allow_domains=None, resolve: bool = True) -> str | None:
    """None if the URL is OK to fetch, else the reason it isn't. resolve=False skips the
    DNS check (for simulated sites in tests); real fetchers must keep it on."""
    u = urlsplit(url)
    if u.scheme != "https":
        return "only https:// URLs are allowed"
    host = (u.hostname or "").lower()
    if not host:
        return "the URL has no host"
    if allow_domains is not None and not any(host == d or host.endswith("." + d)
                                             for d in allow_domains):
        return f"{host} is not on the list of allowed sites"
    if not resolve:
        return None
    try:
        addresses = {info[4][0] for info in socket.getaddrinfo(host, u.port or 443)}
    except socket.gaierror:
        return f"cannot resolve {host}"
    for a in addresses:
        ip = ipaddress.ip_address(a)
        if not ip.is_global:  # private, loopback, link-local, reserved...
            return f"{host} resolves to a non-public address ({ip}); refusing"
    return None

def fetch_url(url: str, max_redirects: int = 5) -> str:
    """Fetch a web page and return the first 4,000 characters of its text.
    Redirects are followed by hand so EVERY hop is checked, not just the first URL."""
    for _ in range(max_redirects + 1):
        if problem := url_problem(url):
            return f"ERROR: {problem}"
        r = httpx.get(url, timeout=15, follow_redirects=False)
        if r.is_redirect:
            url = urljoin(url, r.headers.get("location", ""))
            continue
        text = re.sub(r"<script.*?</script>|<style.*?</style>", "", r.text, flags=re.S)
        text = re.sub(r"<[^>]+>", " ", text)
        return re.sub(r"\s+", " ", text)[:4000]
    return f"ERROR: more than {max_redirects} redirects"
