"""In-memory implementation of :class:`BookingRepository`.

Used in place of a real database for this small coursework
implementation, per the brief's "use in-memory persistence" requirement.
Swapping this out for a real database later only requires writing a new
class that implements
:class:`application.repositories.booking_repository.BookingRepository`
-- the Application and Domain layers do not change.
"""

from typing import Dict, Optional

from application.repositories.booking_repository import BookingRepository
from domain.aggregates.booking import BookingAggregate


class InMemoryBookingRepository(BookingRepository):
    """Stores :class:`BookingAggregate` instances in a plain ``dict``.

    Not thread-safe and not persisted across process restarts -- suitable
    only for tests and this small demo, by design.
    """

    def __init__(self) -> None:
        """Create an empty repository."""
        self._store: Dict[str, BookingAggregate] = {}

    def get(self, booking_id: str) -> Optional[BookingAggregate]:
        """See :meth:`BookingRepository.get`."""
        return self._store.get(booking_id)

    def save(self, booking: BookingAggregate) -> None:
        """See :meth:`BookingRepository.save`."""
        self._store[booking.id] = booking
