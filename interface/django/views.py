"""Interface layer: the only place in this codebase allowed to know about
HTTP or Django.

This view does nothing but translate an HTTP request into a
:class:`~application.dto.create_booking_request.CreateBookingRequest`,
call the Application Service, and translate the resulting
:class:`~application.dto.create_booking_response.CreateBookingResponse`
back into a JSON HTTP response. No business rules and no domain objects
are referenced directly here -- this is the "keep it minimal" entry point
the Clean Architecture brief asks for.
"""

from datetime import datetime

from django.http import HttpRequest, JsonResponse

from application.dto.create_booking_request import CreateBookingRequest
from application.services.create_booking import CreateBookingService
from infrastructure.repositories.in_memory_booking_repository import (
    InMemoryBookingRepository,
)
from infrastructure.repositories.in_memory_room_repository import InMemoryRoomRepository

# Module-level, in-memory repositories shared across requests for this
# small demo app. A production deployment would construct these once
# per process (or per request, backed by a real database) via Django's
# app configuration instead.
_booking_repository = InMemoryBookingRepository()
_room_repository = InMemoryRoomRepository()
_service = CreateBookingService(_booking_repository, _room_repository)


def create_booking(request: HttpRequest) -> JsonResponse:
    """Handle ``POST /bookings/``: create a new room booking.

    Expects ``request.POST`` to contain ``room_id``, ``requester``,
    ``attendee_count`` and ISO-8601 ``start_time`` / ``end_time`` fields.

    Args:
        request: The incoming Django request.

    Returns:
        A ``JsonResponse`` with the booking outcome. HTTP 201 with
        ``success: true`` if the booking was confirmed; HTTP 400 with
        ``success: false`` and an explanatory ``message`` otherwise
        (e.g. an unknown room, an invalid period, or a scheduling
        conflict -- see
        :meth:`application.services.create_booking.CreateBookingService.execute`).
    """
    body = request.POST
    dto = CreateBookingRequest(
        room_id=body["room_id"],
        requester=body["requester"],
        attendee_count=int(body["attendee_count"]),
        start_time=datetime.fromisoformat(body["start_time"]),
        end_time=datetime.fromisoformat(body["end_time"]),
    )
    result = _service.execute(dto)
    return JsonResponse(
        {
            "success": result.success,
            "booking_id": result.booking_id,
            "status": result.status,
            "message": result.message,
        },
        status=201 if result.success else 400,
    )
