"""T1 - BR1 (Value rule): BookingPeriod must be valid.

Covers: a valid period, the end-before-start rejection, the minimum-
duration boundary (accepted), and both the too-short and too-long
rejection cases. See ``domain/value_objects/booking_date.py`` for the
rule itself.
"""

from datetime import datetime, timedelta

import pytest

from domain.value_objects.booking_date import BookingPeriod, InvalidBookingPeriodError


def test_br1_valid_period_is_accepted():
    start = datetime(2026, 10, 1, 9, 0)
    end = start + timedelta(hours=1)
    period = BookingPeriod(start, end)
    assert period.start_time == start
    assert period.end_time == end


def test_br1_end_before_start_is_rejected():
    start = datetime(2026, 10, 1, 9, 0)
    end = start - timedelta(minutes=30)
    with pytest.raises(InvalidBookingPeriodError):
        BookingPeriod(start, end)


def test_br1_boundary_minimum_duration_is_accepted():
    start = datetime(2026, 10, 1, 9, 0)
    end = start + timedelta(minutes=30)  # exactly the minimum allowed
    period = BookingPeriod(start, end)
    assert (period.end_time - period.start_time) == timedelta(minutes=30)


def test_br1_too_short_duration_is_rejected():
    start = datetime(2026, 10, 1, 9, 0)
    end = start + timedelta(minutes=10)
    with pytest.raises(InvalidBookingPeriodError):
        BookingPeriod(start, end)


def test_br1_too_long_duration_is_rejected():
    start = datetime(2026, 10, 1, 9, 0)
    end = start + timedelta(hours=9)
    with pytest.raises(InvalidBookingPeriodError):
        BookingPeriod(start, end)
