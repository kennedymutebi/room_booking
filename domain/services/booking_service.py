"""Domain Service enforcing BR4.

BR4 (Cross-concept rule): deciding whether a room can accept a booking
request needs the Room's capacity *and* schedule together with the
request's attendee count *and* period. It doesn't belong on
:class:`~domain.aggregates.room.RoomAggregate` (which shouldn't know
about a booking request it hasn't accepted yet) or on
:class:`~domain.aggregates.booking.BookingAggregate` (which shouldn't
know about a specific room's other bookings), so it is modelled as a
stateless Domain Service that takes both as input instead.
"""

from domain.aggregates.room import RoomAggregate
from domain.value_objects.booking_date import BookingPeriod


class RoomNotSuitableError(ValueError):
    """Raised when BR4 is violated.

    Covers two independent reasons a room may not be suitable: the
    requested attendee count exceeds the room's capacity, or the
    requested period overlaps a slot the room has already reserved.
    """


class RoomAllocationService:
    """Stateless domain service that decides room suitability (BR4)."""

    @staticmethod
    def assess(room: RoomAggregate, attendee_count: int, period: BookingPeriod) -> None:
        """Check whether ``room`` can accommodate a booking request.

        Args:
            room: The room being considered.
            attendee_count: Number of people the booking is for.
            period: The requested time period.

        Raises:
            RoomNotSuitableError: If ``room.capacity`` is too small for
                ``attendee_count``, or if ``period`` overlaps any slot
                already reserved on ``room``. This method performs no
                mutation either way -- it only validates and raises;
                the caller is responsible for reserving the slot
                afterwards (see
                :class:`application.services.create_booking.CreateBookingService`).
        """
        if not room.has_capacity_for(attendee_count):
            raise RoomNotSuitableError(
                f"Room {room.name} (capacity {room.capacity}) cannot hold "
                f"{attendee_count} attendees."
            )
        for slot in room.reserved_slots:
            if slot.overlaps_with(period):
                raise RoomNotSuitableError(
                    f"Room {room.name} is already booked during the requested period."
                )
