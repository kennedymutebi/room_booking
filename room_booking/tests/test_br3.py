"""T3 - BR3 (Invariant rule): a Room's reserved slots may never overlap.

Covers: two non-overlapping slots (both accepted), an overlapping slot
(rejected), and the back-to-back boundary case (accepted, since touching
is not overlapping). See ``domain/aggregates/room.py`` for the rule
itself.
"""

from datetime import datetime

import pytest

from domain.aggregates.room import OverlappingBookingError, RoomAggregate
from domain.value_objects.booking_date import BookingPeriod


def make_room():
    return RoomAggregate(id="r1", name="Lab A", capacity=10)


def test_br3_non_overlapping_slots_are_both_accepted():
    room = make_room()
    p1 = BookingPeriod(datetime(2026, 10, 1, 9, 0), datetime(2026, 10, 1, 10, 0))
    p2 = BookingPeriod(datetime(2026, 10, 1, 10, 0), datetime(2026, 10, 1, 11, 0))
    room.reserve_slot(p1)
    room.reserve_slot(p2)
    assert len(room.reserved_slots) == 2


def test_br3_overlapping_slot_is_rejected():
    room = make_room()
    p1 = BookingPeriod(datetime(2026, 10, 1, 9, 0), datetime(2026, 10, 1, 10, 0))
    p2 = BookingPeriod(datetime(2026, 10, 1, 9, 30), datetime(2026, 10, 1, 10, 30))
    room.reserve_slot(p1)
    with pytest.raises(OverlappingBookingError):
        room.reserve_slot(p2)
    assert len(room.reserved_slots) == 1


def test_br3_boundary_back_to_back_slots_do_not_overlap():
    room = make_room()
    p1 = BookingPeriod(datetime(2026, 10, 1, 9, 0), datetime(2026, 10, 1, 10, 0))
    p2 = BookingPeriod(datetime(2026, 10, 1, 10, 0), datetime(2026, 10, 1, 10, 30))
    room.reserve_slot(p1)
    room.reserve_slot(p2)  # boundary case: touching, not overlapping
    assert len(room.reserved_slots) == 2
