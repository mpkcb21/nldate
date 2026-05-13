from datetime import date
from nldate import parse


def test_today():
    today = date(2025, 6, 15)
    assert parse("today", today) == date(2025, 6, 15)


def test_tomorrow():
    today = date(2025, 6, 15)
    assert parse("tomorrow", today) == date(2025, 6, 16)


def test_yesterday():
    today = date(2025, 6, 15)
    assert parse("yesterday", today) == date(2025, 6, 14)


def test_next_tuesday():
    today = date(2025, 6, 15)  # Sunday
    assert parse("next Tuesday", today) == date(2025, 6, 17)


def test_last_monday():
    today = date(2025, 6, 15)  # Sunday
    assert parse("last Monday", today) == date(2025, 6, 9)


def test_in_3_days():
    today = date(2025, 6, 15)
    assert parse("in 3 days", today) == date(2025, 6, 18)


def test_in_2_weeks():
    today = date(2025, 6, 15)
    assert parse("in 2 weeks", today) == date(2025, 6, 29)


def test_n_days_ago():
    today = date(2025, 6, 15)
    assert parse("5 days ago", today) == date(2025, 6, 10)


def test_days_before_absolute():
    today = date(2025, 6, 15)
    assert parse("5 days before December 1st, 2025", today) == date(2025, 11, 26)


def test_days_after_absolute():
    today = date(2025, 6, 15)
    assert parse("3 days after December 1st, 2025", today) == date(2025, 12, 4)


def test_compound_after():
    today = date(2025, 6, 15)
    assert parse("1 year and 2 months after January 1st, 2025", today) == date(2026, 3, 1)


def test_absolute_date():
    today = date(2025, 6, 15)
    assert parse("December 1st, 2025", today) == date(2025, 12, 1)


def test_in_1_month():
    today = date(2025, 6, 15)
    assert parse("in 1 month", today) == date(2025, 7, 15)


def test_days_after_tomorrow():
    today = date(2025, 6, 15)
    assert parse("3 days after tomorrow", today) == date(2025, 6, 19)