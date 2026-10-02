"""Repository abstraction for the Room aggregate.

Defined in the Application layer (not Infrastructure) so that
:class:`application.services.create_booking.CreateBookingService` and
:class:`infrastructure.events.event_handler.BookingConfirmedHandler` can
depend only on this interface. The concrete implementation
(:class:`infrastructure.repositories.in_memory_room_repository.InMemoryRoomRepository`)
is supplied from outside via dependency injection.
"""

from abc import ABC, abstractmethod
from typing import Optional

from domain.aggregates.room import RoomAggregate


class RoomRepository(ABC):
    """Persistence boundary for :class:`RoomAggregate` instances."""

    @abstractmethod
    def get(self, room_id: str) -> Optional[RoomAggregate]:
        """Retrieve a room by id.

        Args:
            room_id: The room's unique identifier.

        Returns:
            The matching :class:`RoomAggregate`, or ``None`` if no room
            with that id has been saved. BR6 relies on this returning
            ``None`` to reject bookings for unknown rooms.
        """
        ...

    @abstractmethod
    def save(self, room: RoomAggregate) -> None:
        """Persist a room, creating or overwriting it.

        Args:
            room: The aggregate to save. Implementations should save by
                ``room.id``, so calling this again with the same id
                updates the stored record (in particular, its reserved
                slots).
        """
        ...
