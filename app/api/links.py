from fastapi import Request
from typing import List, Optional
from app.schemas.base import Link


def build_link(rel: str, href: str, method: str = "GET") -> Link:
    return Link(rel=rel, href=href, method=method)


def build_url(request: Optional[Request], path: str) -> str:
    if request is None:
        return f"/{path.lstrip('/')}"
    base = str(request.base_url).rstrip("/")
    return f"{base}/{path.lstrip('/')}"


def resource_links(
    request: Optional[Request],
    self_path: str,
    collection_path: Optional[str] = None,
    extra: Optional[List[Link]] = None,
) -> List[Link]:
    links = [build_link("self", build_url(request, self_path))]
    if collection_path:
        links.append(build_link("collection", build_url(request, collection_path)))
    if extra:
        links.extend(extra)
    return links
