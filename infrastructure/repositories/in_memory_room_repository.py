"""In-memory implementation of :class:`RoomRepository`.

Used in place of a real database for this small coursework
implementation, per the brief's "use in-memory persistence" requirement.
Swapping this out for a real database later only requires writing a new
class that implements
:class:`application.repositories.room_repository.RoomRepository`
-- the Application and Domain layers do not change.
"""

from typing import Dict, Optional

from application.repositories.room_repository import RoomRepository
from domain.aggregates.room import RoomAggregate


class InMemoryRoomRepository(RoomRepository):
    """Stores :class:`RoomAggregate` instances in a plain ``dict``.

    Not thread-safe and not persisted across process restarts -- suitable
    only for tests and this small demo, by design.
    """

    def __init__(self) -> None:
        """Create an empty repository."""
        self._store: Dict[str, RoomAggregate] = {}

    def get(self, room_id: str) -> Optional[RoomAggregate]:
        """See :meth:`RoomRepository.get`."""
        return self._store.get(room_id)

    def save(self, room: RoomAggregate) -> None:
        """See :meth:`RoomRepository.save`."""
        self._store[room.id] = room
