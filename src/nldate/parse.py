import re
from datetime import date, timedelta

from dateutil import parser as dateutil_parser
from dateutil.relativedelta import relativedelta

WORD_TO_NUM = {
    "a": 1,
    "an": 1,
    "one": 1,
    "two": 2,
    "three": 3,
    "four": 4,
    "five": 5,
    "six": 6,
    "seven": 7,
    "eight": 8,
    "nine": 9,
    "ten": 10,
    "eleven": 11,
    "twelve": 12,
    "thirteen": 13,
    "fourteen": 14,
    "fifteen": 15,
    "sixteen": 16,
    "seventeen": 17,
    "eighteen": 18,
    "nineteen": 19,
    "twenty": 20,
    "thirty": 30,
    "forty": 40,
    "fifty": 50,
    "sixty": 60,
    "ninety": 90,
}


def _normalize(text: str) -> str:
    for word, num in WORD_TO_NUM.items():
        text = re.sub(rf"\b{word}\b", str(num), text)
    return text


def _parse_unit(n: int, unit: str, direction: int, base: date) -> date:
    if "day" in unit:
        return base + timedelta(days=direction * n)
    elif "week" in unit:
        return base + timedelta(weeks=direction * n)
    elif "month" in unit:
        return base + relativedelta(months=direction * n)
    elif "year" in unit:
        return base + relativedelta(years=direction * n)
    raise ValueError(f"Unknown unit: {unit}")


def parse(s: str, today: date | None = None) -> date:
    if today is None:
        today = date.today()

    text = s.strip().lower()
    text = _normalize(text)

    # simple keywords
    if text == "today":
        return today
    if text == "tomorrow":
        return today + timedelta(days=1)
    if text == "yesterday":
        return today + timedelta(days=-1)
    if text in ("the day after tomorrow", "day after tomorrow"):
        return today + timedelta(days=2)
    if text in ("the day before yesterday", "day before yesterday"):
        return today + timedelta(days=-2)

    weekdays = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]

    # "next <weekday>"
    m = re.match(r"next (\w+)", text)
    if m and m.group(1) in weekdays:
        target = weekdays.index(m.group(1))
        days_ahead = (target - today.weekday()) % 7 or 7
        return today + timedelta(days=days_ahead)

    # "last <weekday>"
    m = re.match(r"last (\w+)", text)
    if m and m.group(1) in weekdays:
        target = weekdays.index(m.group(1))
        days_behind = (today.weekday() - target) % 7 or 7
        return today + timedelta(days=-days_behind)

    # "this <weekday>"
    m = re.match(r"this (\w+)", text)
    if m and m.group(1) in weekdays:
        target = weekdays.index(m.group(1))
        days_ahead = (target - today.weekday()) % 7
        return today + timedelta(days=days_ahead)

    unit_pat = r"(days?|weeks?|months?|years?)"

    # "N years, N months before/after <date>" or "N years and N months before/after <date>"
    m = re.match(
        r"(\d+) years?[,]?\s*(?:and\s*)?(\d+) months? (before|after) (.+)", text
    )
    if m:
        years = int(m.group(1))
        months = int(m.group(2))
        direction = 1 if m.group(3) == "after" else -1
        base = parse(m.group(4), today)
        return base + relativedelta(years=direction * years, months=direction * months)

    # "N months, N days before/after <date>"
    m = re.match(
        r"(\d+) months?[,]?\s*(?:and\s*)?(\d+) days? (before|after) (.+)", text
    )
    if m:
        months = int(m.group(1))
        days = int(m.group(2))
        direction = 1 if m.group(3) == "after" else -1
        base = parse(m.group(4), today)
        return base + relativedelta(months=direction * months, days=direction * days)

    # "N weeks, N days before/after <date>"
    m = re.match(
        r"(\d+) weeks?[,]?\s*(?:and\s*)?(\d+) days? (before|after) (.+)", text
    )
    if m:
        weeks = int(m.group(1))
        days = int(m.group(2))
        direction = 1 if m.group(3) == "after" else -1
        base = parse(m.group(4), today)
        return base + timedelta(weeks=direction * weeks, days=direction * days)

    # "N before/after <date>"
    m = re.match(rf"(\d+) {unit_pat} (before|after) (.+)", text)
    if m:
        n = int(m.group(1))
        unit = m.group(2)
        direction = 1 if m.group(3) == "after" else -1
        base = parse(m.group(4), today)
        return _parse_unit(n, unit, direction, base)

    # "N from <date or now>"
    m = re.match(rf"(\d+) {unit_pat} from (.+)", text)
    if m:
        n = int(m.group(1))
        unit = m.group(2)
        base_str = m.group(3).strip()
        base = today if base_str in ("now", "today") else parse(base_str, today)
        return _parse_unit(n, unit, 1, base)

    # "in N <unit>"
    m = re.match(rf"in (\d+) {unit_pat}$", text)
    if m:
        return _parse_unit(int(m.group(1)), m.group(2), 1, today)

    # "N ago"
    m = re.match(rf"(\d+) {unit_pat} ago$", text)
    if m:
        return _parse_unit(int(m.group(1)), m.group(2), -1, today)

    # fallback: dateutil for absolute dates
    try:
        return dateutil_parser.parse(
            s, default=dateutil_parser.parse(today.strftime("%Y-%m-%d"))
        ).date()
    except Exception:
        raise ValueError(f"Could not parse date string: {s!r}")