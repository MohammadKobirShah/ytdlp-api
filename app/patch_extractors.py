"""
Monkey-patch yt-dlp's InfoExtractor to gracefully handle metadata
extraction failures instead of crashing the entire extraction.

When a HTML regex pattern fails to match (e.g. because a site changed
its HTML structure), the original code raises RegexNotFoundError which
cascades into a 400 Bad Request for the API consumer.

This patch makes _html_search_regex return None instead of raising,
and logs a warning. All format/stream data is preserved.

Applies automatically on import.
"""

import logging

import yt_dlp.extractor.common as common
from yt_dlp.utils import NO_DEFAULT, RegexNotFoundError

logger = logging.getLogger("ytdlp-api.patch")

_original = common.InfoExtractor._html_search_regex


def _patched_html_search_regex(self, pattern, string, name,
                                default=NO_DEFAULT, fatal=True,
                                flags=0, group=None):
    try:
        return _original(self, pattern, string, name,
                         default=default, fatal=fatal,
                         flags=flags, group=group)
    except RegexNotFoundError:
        extractor = type(self).__name__
        logger.warning(
            "extractor=%s field=%s not found (site HTML may have changed), "
            "falling back to None",
            extractor, name,
        )
        return None


common.InfoExtractor._html_search_regex = _patched_html_search_regex
logger.info("applied InfoExtractor._html_search_regex resilience patch")
