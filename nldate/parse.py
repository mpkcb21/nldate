from datetime import date, timedelta
import re
from dateutil import parser as dateutil_parser
from dateutil.relativedelta import relativedelta


def parse(s: str, today: date | None = None) -> date:
    if today is None:
        today = date.today()

    text = s.strip().lower()

    # "today"
    if text == "today":
        return today

    # "tomorrow"
    if text == "tomorrow":
        return today + timedelta(days=1)

    # "yesterday"
    if text == "yesterday":
        return today + timedelta(days=-1)

    # "next <weekday>" e.g. "next Tuesday"
    next_match = re.match(r"next (\w+)", text)
    if next_match:
        weekday_str = next_match.group(1)
        weekdays = ["monday","tuesday","wednesday","thursday","friday","saturday","sunday"]
        if weekday_str in weekdays:
            target = weekdays.index(weekday_str)
            current = today.weekday()
            days_ahead = (target - current) % 7
            if days_ahead == 0:
                days_ahead = 7
            return today + timedelta(days=days_ahead)

    # "last <weekday>" e.g. "last Monday"
    last_match = re.match(r"last (\w+)", text)
    if last_match:
        weekday_str = last_match.group(1)
        weekdays = ["monday","tuesday","wednesday","thursday","friday","saturday","sunday"]
        if weekday_str in weekdays:
            target = weekdays.index(weekday_str)
            current = today.weekday()
            days_behind = (current - target) % 7
            if days_behind == 0:
                days_behind = 7
            return today + timedelta(days=-days_behind)

    # "in N days/weeks/months/years"
    in_match = re.match(r"in (\d+) (day|days|week|weeks|month|months|year|years)", text)
    if in_match:
        n = int(in_match.group(1))
        unit = in_match.group(2)
        if "day" in unit:
            return today + timedelta(days=n)
        elif "week" in unit:
            return today + timedelta(weeks=n)
        elif "month" in unit:
            return today + relativedelta(months=n)
        elif "year" in unit:
            return today + relativedelta(years=n)

    # "N days/weeks/months/years ago"
    ago_match = re.match(r"(\d+) (day|days|week|weeks|month|months|year|years) ago", text)
    if ago_match:
        n = int(ago_match.group(1))
        unit = ago_match.group(2)
        if "day" in unit:
            return today + timedelta(days=-n)
        elif "week" in unit:
            return today + timedelta(weeks=-n)
        elif "month" in unit:
            return today + relativedelta(months=-n)
        elif "year" in unit:
            return today + relativedelta(years=-n)

    # "N days/weeks/months/years before <date>"
    before_match = re.match(r"(\d+) (day|days|week|weeks|month|months|year|years) before (.+)", text)
    if before_match:
        n = int(before_match.group(1))
        unit = before_match.group(2)
        base = parse(before_match.group(3), today)
        if "day" in unit:
            return base + timedelta(days=-n)
        elif "week" in unit:
            return base + timedelta(weeks=-n)
        elif "month" in unit:
            return base + relativedelta(months=-n)
        elif "year" in unit:
            return base + relativedelta(years=-n)

    # "N days/weeks/months/years after <date>"
    after_match = re.match(r"(\d+) (day|days|week|weeks|month|months|year|years) after (.+)", text)
    if after_match:
        n = int(after_match.group(1))
        unit = after_match.group(2)
        base = parse(after_match.group(3), today)
        if "day" in unit:
            return base + timedelta(days=n)
        elif "week" in unit:
            return base + timedelta(weeks=n)
        elif "month" in unit:
            return base + relativedelta(months=n)
        elif "year" in unit:
            return base + relativedelta(years=n)

    # "1 year and 2 months after/before <date>"
    compound_match = re.match(
        r"(\d+) (year|years) and (\d+) (month|months) (after|before) (.+)", text
    )
    if compound_match:
        years = int(compound_match.group(1))
        months = int(compound_match.group(3))
        direction = compound_match.group(5)
        base = parse(compound_match.group(6), today)
        delta = relativedelta(years=years, months=months)
        return base + delta if direction == "after" else base - delta

    # fallback: try dateutil for absolute dates like "December 1st, 2025"
    try:
        return dateutil_parser.parse(s, default=dateutil_parser.parse(today.strftime("%Y-%m-%d"))).date()
    except Exception:
        raise ValueError(f"Could not parse date string: {s!r}")