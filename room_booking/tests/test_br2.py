"""T2 - BR2 (Identity/state rule): Booking state transitions.

Covers: the valid PENDING -> CONFIRMED transition, and two rejection
cases (confirming twice, confirming a cancelled booking). See
``domain/aggregates/booking.py`` for the rule itself.
"""

from datetime import datetime

import pytest

from domain.aggregates.booking import BookingAggregate, InvalidBookingStateTransitionError
from domain.entities.booking import BookingStatus
from domain.value_objects.booking_date import BookingPeriod


def make_booking():
    period = BookingPeriod(datetime(2026, 10, 1, 9, 0), datetime(2026, 10, 1, 10, 0))
    return BookingAggregate(
        id="b1", room_id="r1", requester="Kennedy", attendee_count=3, period=period
    )


def test_br2_pending_booking_can_be_confirmed():
    booking = make_booking()
    booking.confirm()
    assert booking.status == BookingStatus.CONFIRMED


def test_br2_confirmed_booking_cannot_be_confirmed_again():
    booking = make_booking()
    booking.confirm()
    with pytest.raises(InvalidBookingStateTransitionError):
        booking.confirm()


def test_br2_cancelled_booking_cannot_be_confirmed():
    booking = make_booking()
    booking.cancel()
    with pytest.raises(InvalidBookingStateTransitionError):
        booking.confirm()
