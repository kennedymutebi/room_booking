"""T4 - BR4 (Cross-concept rule): RoomAllocationService checks capacity
and schedule together.

Covers: a suitable room (accepted), a room that is too small (rejected),
and a room that is already booked for the requested period (rejected).
See ``domain/services/booking_service.py`` for the rule itself.
"""

from datetime import datetime

import pytest

from domain.aggregates.room import RoomAggregate
from domain.services.booking_service import RoomAllocationService, RoomNotSuitableError
from domain.value_objects.booking_date import BookingPeriod


def test_br4_room_with_enough_capacity_and_free_slot_is_accepted():
    room = RoomAggregate(id="r1", name="Lab A", capacity=10)
    period = BookingPeriod(datetime(2026, 10, 1, 9, 0), datetime(2026, 10, 1, 10, 0))
    RoomAllocationService.assess(room, attendee_count=8, period=period)  # no exception raised


def test_br4_room_over_capacity_is_rejected():
    room = RoomAggregate(id="r1", name="Lab A", capacity=5)
    period = BookingPeriod(datetime(2026, 10, 1, 9, 0), datetime(2026, 10, 1, 10, 0))
    with pytest.raises(RoomNotSuitableError):
        RoomAllocationService.assess(room, attendee_count=8, period=period)


def test_br4_room_already_booked_for_period_is_rejected():
    room = RoomAggregate(id="r1", name="Lab A", capacity=10)
    existing = BookingPeriod(datetime(2026, 10, 1, 9, 0), datetime(2026, 10, 1, 10, 0))
    room.reserve_slot(existing)
    clashing = BookingPeriod(datetime(2026, 10, 1, 9, 30), datetime(2026, 10, 1, 10, 30))
    with pytest.raises(RoomNotSuitableError):
        RoomAllocationService.assess(room, attendee_count=4, period=clashing)
