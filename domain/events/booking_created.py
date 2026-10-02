"""Domain Event enforcing BR5.

BR5 (Follow-up rule): once a Booking (Aggregate A) is confirmed, Aggregate
B (the Room) must be asked, via this event, to reserve the matching time
slot. Aggregate A never reaches into Aggregate B directly -- it only
raises this event and lets a handler
(:class:`infrastructure.events.event_handler.BookingConfirmedHandler`)
carry the request across the aggregate boundary. This keeps the two
aggregates independently consistent and independently persistable.
"""

from dataclasses import dataclass

from domain.value_objects.booking_date import BookingPeriod


@dataclass(frozen=True)
class BookingConfirmed:
    """Raised by :class:`domain.aggregates.booking.BookingAggregate` when a
    booking transitions from ``PENDING`` to ``CONFIRMED``.

    Attributes:
        booking_id: Identifier of the Booking that raised the event, so
            the handler (or caller) can update it afterwards (e.g. call
            ``.reject()`` if the follow-up action fails).
        room_id: Identifier of the Room the event's handler must act on.
        period: The exact time span to reserve on that room.
    """

    booking_id: str
    room_id: str
    period: BookingPeriod
