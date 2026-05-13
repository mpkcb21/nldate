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
}


def _normalize(text: str) -> str:
    """Replace written-out numbers with digits."""
    for word, num in WORD_TO_NUM.items():
        text = re.sub(
            rf"\b{word}\b",
            str(num),
            text,
        )
    return text


def _parse_unit(n: int, unit: str, direction: int, base: date) -> date:
    """Apply n units in direction (+1 or -1) to base date."""
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

    # "today"
    if text == "today":
        return today

    # "tomorrow"
    if text == "tomorrow":
        return today + timedelta(days=1)

    # "yesterday"
    if text == "yesterday":
        return today + timedelta(days=-1)

    # "the day after tomorrow"
    if text == "the day after tomorrow":
        return today + timedelta(days=2)

    # "the day before yesterday"
    if text == "the day before yesterday":
        return today + timedelta(days=-2)

    # "next <weekday>"
    next_match = re.match(r"next (\w+)", text)
    if next_match:
        weekday_str = next_match.group(1)
        weekdays = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
        if weekday_str in weekdays:
            target = weekdays.index(weekday_str)
            current = today.weekday()
            days_ahead = (target - current) % 7
            if days_ahead == 0:
                days_ahead = 7
            return today + timedelta(days=days_ahead)

    # "last <weekday>"
    last_match = re.match(r"last (\w+)", text)
    if last_match:
        weekday_str = last_match.group(1)
        weekdays = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
        if weekday_str in weekdays:
            target = weekdays.index(weekday_str)
            current = today.weekday()
            days_behind = (current - target) % 7
            if days_behind == 0:
                days_behind = 7
            return today + timedelta(days=-days_behind)

    # "this <weekday>"
    this_match = re.match(r"this (\w+)", text)
    if this_match:
        weekday_str = this_match.group(1)
        weekdays = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
        if weekday_str in weekdays:
            target = weekdays.index(weekday_str)
            current = today.weekday()
            days_ahead = (target - current) % 7
            return today + timedelta(days=days_ahead)

    unit_pattern = r"(day|days|week|weeks|month|months|year|years)"

    # "in N days/weeks/months/years" or "N days/weeks/months/years from now"
    in_match = re.match(rf"(?:in )?(\d+) {unit_pattern}(?: from now)?$", text)
    if in_match and ("from now" in text or text.startswith("in ")):
        n = int(in_match.group(1))
        unit = in_match.group(2)
        return _parse_unit(n, unit, 1, today)

    # "N days/weeks/months/years ago"
    ago_match = re.match(rf"(\d+) {unit_pattern} ago$", text)
    if ago_match:
        n = int(ago_match.group(1))
        unit = ago_match.group(2)
        return _parse_unit(n, unit, -1, today)

    # "1 year and 2 months before/after <date>"
    compound_match = re.match(
        rf"(\d+) (year|years) and (\d+) (month|months) (after|before) (.+)", text
    )
    if compound_match:
        years = int(compound_match.group(1))
        months = int(compound_match.group(3))
        direction = 1 if compound_match.group(5) == "after" else -1
        base = parse(compound_match.group(6), today)
        return base + relativedelta(years=direction * years, months=direction * months)

    # "N days/weeks/months/years before <date>"
    before_match = re.match(rf"(\d+) {unit_pattern} before (.+)", text)
    if before_match:
        n = int(before_match.group(1))
        unit = before_match.group(2)
        base = parse(before_match.group(3), today)
        return _parse_unit(n, unit, -1, base)

    # "N days/weeks/months/years after <date>"
    after_match = re.match(rf"(\d+) {unit_pattern} after (.+)", text)
    if after_match:
        n = int(after_match.group(1))
        unit = after_match.group(2)
        base = parse(after_match.group(3), today)
        return _parse_unit(n, unit, 1, base)

    # "N days/weeks/months/years from <date>"
    from_match = re.match(rf"(\d+) {unit_pattern} from (.+)", text)
    if from_match:
        n = int(from_match.group(1))
        unit = from_match.group(2)
        base_str = from_match.group(3)
        if base_str == "now" or base_str == "today":
            base = today
        else:
            base = parse(base_str, today)
        return _parse_unit(n, unit, 1, base)

    # fallback: try dateutil for absolute dates like "December 1st, 2025"
    try:
        return dateutil_parser.parse(
            s, default=dateutil_parser.parse(today.strftime("%Y-%m-%d"))
        ).date()
    except Exception:
        raise ValueError(f"Could not parse date string: {s!r}")