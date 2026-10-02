"""Output DTO for the create-booking use case.

Kept as a plain, framework-agnostic data holder so callers (tests, the
Django view, or any other future interface) get a consistent, serialisable
result regardless of which business rule caused a rejection.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class CreateBookingResponse:
    """The outcome of a create-booking request.

    Attributes:
        success: ``True`` only if the booking was created and confirmed
            end to end, including the Room accepting the BR5 follow-up
            action.
        booking_id: The id of the created booking, if one was created.
            ``None`` when the request failed before a booking could be
            created at all (e.g. BR6's room lookup failed, or BR1/BR4
            rejected the request).
        status: The booking's final status as a string (one of
            :class:`domain.entities.booking.BookingStatus`'s values), or
            ``"REJECTED"`` for failures that happened before a booking
            object existed.
        message: A short, human-readable explanation, primarily the text
            of whichever domain exception was raised.
    """

    success: bool
    booking_id: Optional[str]
    status: str
    message: str
