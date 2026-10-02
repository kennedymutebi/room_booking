"""Input DTO for the create-booking use case.

Kept as a plain, framework-agnostic data holder so the Application Service
never depends on how the request arrived (HTTP form, CLI, test code, etc.).
"""

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class CreateBookingRequest:
    """The data needed to request a new room booking.

    Attributes:
        room_id: Identifier of the room being requested (BR6 looks this
            up before anything else happens).
        requester: Name (or identifier) of the person making the request.
        attendee_count: Number of people the booking is for.
        start_time: Requested start of the booking.
        end_time: Requested end of the booking.
    """

    room_id: str
    requester: str
    attendee_count: int
    start_time: datetime
    end_time: datetime
