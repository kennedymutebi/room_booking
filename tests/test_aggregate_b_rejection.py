"""T8 - Aggregate B rejects the follow-up action.

Simulates the case where Room (Aggregate B) already has a slot that would
overlap by the time the BookingConfirmed event arrives (e.g. another
booking was confirmed in between). Booking (Aggregate A) is valid on its
own terms (BR2 passes), but Room's own BR3 invariant is the final
authority and refuses the event. Verifies the final state of both
aggregates and the outcome returned.
"""

from datetime import datetime

import pytest

from domain.aggregates.booking import BookingAggregate
from domain.aggregates.room import OverlappingBookingError, RoomAggregate
from domain.entities.booking import BookingStatus
from domain.value_objects.booking_date import BookingPeriod
from infrastructure.events.event_handler import BookingConfirmedHandler
from infrastructure.repositories.in_memory_room_repository import InMemoryRoomRepository


def test_t8_room_aggregate_rejects_an_overlapping_follow_up():
    room_repo = InMemoryRoomRepository()
    room = RoomAggregate(id="r1", name="Lab A", capacity=10)
    room.reserve_slot(BookingPeriod(datetime(2026, 10, 1, 9, 0), datetime(2026, 10, 1, 10, 0)))
    room_repo.save(room)

    clashing_period = BookingPeriod(datetime(2026, 10, 1, 9, 30), datetime(2026, 10, 1, 10, 30))
    booking = BookingAggregate(
        id="b2", room_id="r1", requester="Diana", attendee_count=2, period=clashing_period
    )
    booking.confirm()  # BR2 passes: this is valid on Booking's own terms
    events = booking.pull_events()

    handler = BookingConfirmedHandler(room_repo)
    with pytest.raises(OverlappingBookingError):
        handler.handle(events[0])
    booking.reject()

    # Final state: the booking is rejected, and the room's schedule is unchanged.
    assert booking.status == BookingStatus.REJECTED
    stored_room = room_repo.get("r1")
    assert len(stored_room.reserved_slots) == 1
