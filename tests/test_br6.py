"""T6 - BR6 (Lookup rule): the Application Service must find the Room via
RoomRepository before a booking can proceed.

Covers: an unknown room (rejected, no booking created) and a known room
(the lookup succeeds and the use case proceeds). See
``application/services/create_booking.py`` for the rule itself.
"""

from datetime import datetime

from application.dto.create_booking_request import CreateBookingRequest
from application.services.create_booking import CreateBookingService
from domain.aggregates.room import RoomAggregate
from infrastructure.repositories.in_memory_booking_repository import (
    InMemoryBookingRepository,
)
from infrastructure.repositories.in_memory_room_repository import InMemoryRoomRepository


def test_br6_booking_for_unknown_room_is_rejected():
    service = CreateBookingService(InMemoryBookingRepository(), InMemoryRoomRepository())
    request = CreateBookingRequest(
        room_id="does-not-exist",
        requester="Kennedy",
        attendee_count=3,
        start_time=datetime(2026, 10, 1, 9, 0),
        end_time=datetime(2026, 10, 1, 10, 0),
    )

    response = service.execute(request)

    assert response.success is False
    assert response.status == "REJECTED"
    assert response.booking_id is None


def test_br6_booking_for_existing_room_passes_the_lookup():
    room_repo = InMemoryRoomRepository()
    room_repo.save(RoomAggregate(id="r1", name="Lab A", capacity=10))
    service = CreateBookingService(InMemoryBookingRepository(), room_repo)
    request = CreateBookingRequest(
        room_id="r1",
        requester="Kennedy",
        attendee_count=3,
        start_time=datetime(2026, 10, 1, 9, 0),
        end_time=datetime(2026, 10, 1, 10, 0),
    )

    response = service.execute(request)

    assert response.success is True
