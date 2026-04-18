import logging
import sys


def setup_logging(level: str = "INFO") -> None:
    """Configure root logger: stdout, consistent format, given level name."""
    numeric_level = getattr(logging, level.upper(), logging.INFO)
    root = logging.getLogger()
    if root.handlers:
        root.handlers.clear()
    root.setLevel(numeric_level)
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(numeric_level)
    handler.setFormatter(
        logging.Formatter(
            fmt="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
    )
    root.addHandler(handler)
