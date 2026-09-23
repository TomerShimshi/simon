from urllib.parse import parse_qs, urlsplit

# Slug (used in the URL and as the storage namespace) -> Hebrew display name.
# "other" is a deliberate catch-all for anyone testing the live site (e.g.
# development/QA) so that traffic never lands in a named family member's
# real progress history.
PROFILES = {
    "efraim": "אפרים",
    "tomer": "תומר",
    "other": "אחר",
}


def route_path(route: str) -> str:
    """The route's path only, stripped of any query string -- for matching
    against ROUTE_BUILDERS, which key on plain paths like "/simon"."""
    return urlsplit(route).path or "/"


def profile_from_route(route: str) -> str | None:
    """Reads ?user=<slug> from the route's query string, returning it only
    if it names a known profile -- so a bookmarked URL like .../?user=efraim
    skips the profile picker on every future visit."""
    query = parse_qs(urlsplit(route).query)
    values = query.get("user")
    if not values:
        return None
    slug = values[0]
    return slug if slug in PROFILES else None
