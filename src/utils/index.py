from datetime import datetime, timezone

def default_datetime():
    return datetime.now().astimezone(timezone.utc)