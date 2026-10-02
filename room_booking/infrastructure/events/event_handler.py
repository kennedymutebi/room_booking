"""In-process handler for BR5's follow-up action.

Sits in the Infrastructure layer because it is the *mechanism* that wires
the two aggregates together (a plain, synchronous, in-process function
call), not domain behaviour itself. The rule it enforces indirectly (BR3,
no overlapping slots) still lives inside
:class:`domain.aggregates.room.RoomAggregate`; this handler's only job is
routing the event to the right aggregate.

A real deployment could replace this with a message-broker-backed
handler without changing the Domain layer at all, since the handler only
depends on the abstract
:class:`application.repositories.room_repository.RoomRepository`.
"""

from application.repositories.room_repository import RoomRepository
from domain.events.booking_created import BookingConfirmed


class BookingConfirmedHandler:
    """Reacts to a :class:`BookingConfirmed` event by reserving the slot
    on the corresponding Room aggregate."""

    def __init__(self, room_repository: RoomRepository) -> None:
        """Wire the handler to the repository it needs to fetch and save
        rooms.

        Args:
            room_repository: Used to load the target Room and persist it
                again after the slot is reserved.
        """
        self._room_repository = room_repository

    def handle(self, event: BookingConfirmed) -> None:
        """Reserve the event's period on the event's room.

        Args:
            event: The event raised by
                :meth:`domain.aggregates.booking.BookingAggregate.confirm`.

        Raises:
            ValueError: If ``event.room_id`` does not correspond to any
                room known to the repository.
            domain.aggregates.room.OverlappingBookingError: If BR3 is
                violated -- i.e. the room already has a slot overlapping
                ``event.period``. In this case nothing is persisted and
                the caller (see
                :class:`application.services.create_booking.CreateBookingService`)
                is responsible for rejecting the booking.
        """
        room = self._room_repository.get(event.room_id)
        if room is None:
            raise ValueError(f"Room {event.room_id} not found.")
        room.reserve_slot(event.period)  # BR3 enforced here, inside Aggregate B
        self._room_repository.save(room)
