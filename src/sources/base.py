from __future__ import annotations
from typing import Iterable, Dict, Any

class BaseSource:
    name: str = "base"

    def fetch(self) -> Iterable[Dict[str, Any]]:
        """Yield raw posting dicts with keys:
        title, company, location, posted_at (iso or None), url, description_html/text
        """
        raise NotImplementedError
