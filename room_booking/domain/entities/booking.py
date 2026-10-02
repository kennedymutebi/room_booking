"""Booking entity and its lifecycle states.

Holds the plain data that identifies and describes a booking request. The
behaviour that protects BR2 (valid state transitions) and raises BR5's
domain event lives on :class:`domain.aggregates.booking.BookingAggregate`,
which subclasses this entity.
"""

from dataclasses import dataclass, field
from enum import Enum

from domain.value_objects.booking_date import BookingPeriod


class BookingStatus(Enum):
    """The lifecycle states a :class:`Booking` can be in.

    Valid forward transitions (enforced by BR2, in
    :class:`domain.aggregates.booking.BookingAggregate`) are::

        PENDING -> CONFIRMED -> CANCELLED
        PENDING -> CANCELLED
        CONFIRMED -> REJECTED   (only via the BR5 follow-up path)

    No other transition is permitted; in particular, a booking can never
    leave ``CANCELLED`` or ``REJECTED`` once it reaches one of them.
    """

    PENDING = "PENDING"
    CONFIRMED = "CONFIRMED"
    CANCELLED = "CANCELLED"
    REJECTED = "REJECTED"


@dataclass
class Booking:
    """A request to reserve a room for a specific period.

    A Booking's identity is its ``id``, not its ``room_id``, ``requester``
    or ``period`` -- the same requester could make two distinct bookings
    with identical details on separate occasions, and each must be
    tracked independently. That identity, combined with the fact that a
    booking moves through the states in :class:`BookingStatus`, is why
    BR2 requires an Entity/Aggregate Root (see
    :class:`domain.aggregates.booking.BookingAggregate`) rather than a
    Value Object.

    Attributes:
        id: Unique identifier for this booking.
        room_id: Identifier of the :class:`domain.entities.room.Room`
            being requested. Held by reference (id only), never by
            object, to keep the Booking and Room aggregates independent.
        requester: Name (or identifier) of the person making the request.
        attendee_count: Number of people the booking is for; checked
            against room capacity by BR4.
        period: The requested :class:`BookingPeriod` (BR1 is enforced
            when this value object is constructed).
        status: Current lifecycle state; defaults to
            :attr:`BookingStatus.PENDING`.
    """

    id: str
    room_id: str
    requester: str
    attendee_count: int
    period: BookingPeriod
    status: BookingStatus = BookingStatus.PENDING
