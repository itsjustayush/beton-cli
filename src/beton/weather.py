"""Optional weather lookup using wttr.in."""

from __future__ import annotations

import urllib.error
import urllib.parse
import urllib.request

from .models import ActionResult, ResultStatus


def weather(location: str = "", dry_run: bool = False) -> ActionResult:
    encoded = urllib.parse.quote(location.strip() or "")
    url = f"https://wttr.in/{encoded}?format=3"
    if dry_run:
        return ActionResult(ResultStatus.DRY_RUN, f"Would request weather for {location or 'current location'}.", detail=url)
    try:
        with urllib.request.urlopen(url, timeout=10) as response:
            value = response.read().decode("utf-8").strip()
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError) as exc:
        return ActionResult(ResultStatus.UNAVAILABLE, f"Weather lookup failed: {exc}")
    return ActionResult(ResultStatus.SUCCESS, value or "Weather provider returned no data.")
