"""T7 - successful main use case end to end.

Verifies the BookingConfirmed event is handled and Aggregate B (Room)
changes as expected.
"""

from datetime import datetime

from application.dto.create_booking_request import CreateBookingRequest
from application.services.create_booking import CreateBookingService
from domain.aggregates.room import RoomAggregate
from domain.entities.booking import BookingStatus
from infrastructure.repositories.in_memory_booking_repository import (
    InMemoryBookingRepository,
)
from infrastructure.repositories.in_memory_room_repository import InMemoryRoomRepository


def test_t7_successful_booking_confirms_and_reserves_room_slot():
    room_repo = InMemoryRoomRepository()
    room_repo.save(RoomAggregate(id="r1", name="Lab A", capacity=10))
    booking_repo = InMemoryBookingRepository()
    service = CreateBookingService(booking_repo, room_repo)

    request = CreateBookingRequest(
        room_id="r1",
        requester="Kennedy",
        attendee_count=4,
        start_time=datetime(2026, 10, 1, 9, 0),
        end_time=datetime(2026, 10, 1, 10, 0),
    )

    response = service.execute(request)

    assert response.success is True
    assert response.status == BookingStatus.CONFIRMED.value

    saved_booking = booking_repo.get(response.booking_id)
    assert saved_booking.status == BookingStatus.CONFIRMED

    room = room_repo.get("r1")
    assert len(room.reserved_slots) == 1  # proves the BookingConfirmed event was handled
