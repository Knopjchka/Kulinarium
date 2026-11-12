import time
from collections import defaultdict

MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB
CHUNK_SIZE = 1024 * 64  # 64 KB chunks for streaming
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".gif"}

RATE_LIMIT_WINDOW_SECONDS = 60
RATE_LIMIT_MAX_UPLOADS = 10


def detect_image_type(header: bytes) -> str | None:
    """Validate image magic bytes signature and return canonical extension."""
    if len(header) < 12:
        return None

    # JPEG
    if header.startswith(b"\xff\xd8\xff"):
        return ".jpg"

    # PNG
    if header.startswith(b"\x89PNG\r\n\x1a\n"):
        return ".png"

    # GIF
    if header.startswith((b"GIF87a", b"GIF89a")):
        return ".gif"

    # WebP: RIFF????WEBP
    if header.startswith(b"RIFF") and header[8:12] == b"WEBP":
        return ".webp"

    return None


class UploadRateLimiter:
    """In-memory sliding window rate limiter per user."""

    def __init__(self, max_requests: int = 10, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._history: dict[int, list[float]] = defaultdict(list)

    def is_allowed(self, user_id: int) -> bool:
        now = time.monotonic()
        cutoff = now - self.window_seconds
        # Retain only timestamps inside window
        self._history[user_id] = [t for t in self._history[user_id] if t > cutoff]

        if len(self._history[user_id]) >= self.max_requests:
            return False

        self._history[user_id].append(now)
        return True

    def reset(self):
        """Reset limiter state (useful in testing)."""
        self._history.clear()


upload_rate_limiter = UploadRateLimiter(
    max_requests=RATE_LIMIT_MAX_UPLOADS,
    window_seconds=RATE_LIMIT_WINDOW_SECONDS,
)
