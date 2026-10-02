"""T5 - BR5 (Follow-up rule): confirming a Booking raises BookingConfirmed.

Covers: the event is raised with the correct payload on confirm, and the
event queue is cleared once pulled (so it is never handled twice). See
``domain/events/booking_created.py`` and
``domain/aggregates/booking.py`` for the rule itself.
"""

from datetime import datetime

from domain.aggregates.booking import BookingAggregate
from domain.events.booking_created import BookingConfirmed
from domain.value_objects.booking_date import BookingPeriod


def test_br5_confirming_a_booking_raises_a_booking_confirmed_event():
    period = BookingPeriod(datetime(2026, 10, 1, 9, 0), datetime(2026, 10, 1, 10, 0))
    booking = BookingAggregate(
        id="b1", room_id="r1", requester="Kennedy", attendee_count=3, period=period
    )

    booking.confirm()
    events = booking.pull_events()

    assert len(events) == 1
    event = events[0]
    assert isinstance(event, BookingConfirmed)
    assert event.booking_id == "b1"
    assert event.room_id == "r1"
    assert event.period == period


def test_br5_events_are_cleared_after_being_pulled():
    period = BookingPeriod(datetime(2026, 10, 1, 9, 0), datetime(2026, 10, 1, 10, 0))
    booking = BookingAggregate(
        id="b1", room_id="r1", requester="Kennedy", attendee_count=3, period=period
    )
    booking.confirm()
    booking.pull_events()
    assert booking.pull_events() == []
