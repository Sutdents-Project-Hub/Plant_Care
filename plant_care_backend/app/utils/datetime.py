from __future__ import annotations

from datetime import UTC, date, datetime


def parse_ymd(value: str) -> date:
    v = value.strip()
    if len(v) == 8 and v.isdigit():
        return date(int(v[0:4]), int(v[4:6]), int(v[6:8]))
    if len(v) == 10 and v[4] in "-/" and v[7] in "-/":
        return date(int(v[0:4]), int(v[5:7]), int(v[8:10]))
    try:
        d = datetime.fromisoformat(v.replace("Z", "+00:00"))
        return d.date()
    except ValueError as e:
        raise ValueError("Invalid date format") from e


def parse_ymdhms(value: str) -> datetime:
    v = value.strip()
    if len(v) == 14 and v.isdigit():
        return datetime(
            int(v[0:4]),
            int(v[4:6]),
            int(v[6:8]),
            int(v[8:10]),
            int(v[10:12]),
            int(v[12:14]),
            tzinfo=UTC,
        )
    if len(v) == 19 and v[4] == "-" and v[7] == "-" and v[10] == " ":
        v = v.replace(" ", "T", 1)
    try:
        dt = datetime.fromisoformat(v.replace("Z", "+00:00"))
        return dt if dt.tzinfo else dt.replace(tzinfo=UTC)
    except ValueError as e:
        raise ValueError("Invalid datetime format") from e
