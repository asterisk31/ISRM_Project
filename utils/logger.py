import logging
import re


def _sanitize_log_value(value):
    if value is None:
        return "-"
    safe_value = re.sub(r"[\r\n\t]+", " ", str(value))
    safe_value = re.sub(r"[^\x20-\x7E]", "", safe_value)
    return safe_value[:200]


logger = logging.getLogger("isrm_security")
if not logger.handlers:
    logger.setLevel(logging.INFO)
    file_handler = logging.FileHandler("app.log")
    formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    logger.propagate = False


def log_event(event, username=None, details=None, level="info"):
    message = (
        f"event={_sanitize_log_value(event)} "
        f"user={_sanitize_log_value(username)} "
        f"details={_sanitize_log_value(details)}"
    )

    log_method = getattr(logger, level, logger.info)
    log_method(message)
