"""URL path converters shared across apps."""


class ObjectIdConverter:
    """Matches a 24-character MongoDB ObjectId in a URL path, e.g. /resumes/<oid:pk>."""

    regex = r"[0-9a-fA-F]{24}"

    def to_python(self, value: str) -> str:
        return value.lower()

    def to_url(self, value: str) -> str:
        return value
