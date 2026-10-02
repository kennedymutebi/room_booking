"""Repository abstraction for the Booking aggregate.

Defined in the Application layer (not Infrastructure) so that
:class:`application.services.create_booking.CreateBookingService` can
depend only on this interface. The concrete implementation
(:class:`infrastructure.repositories.in_memory_booking_repository.InMemoryBookingRepository`)
is supplied from outside via dependency injection -- see
``CreateBookingService.__init__``.
"""

from abc import ABC, abstractmethod
from typing import Optional

from domain.aggregates.booking import BookingAggregate


class BookingRepository(ABC):
    """Persistence boundary for :class:`BookingAggregate` instances."""

    @abstractmethod
    def get(self, booking_id: str) -> Optional[BookingAggregate]:
        """Retrieve a booking by id.

        Args:
            booking_id: The booking's unique identifier.

        Returns:
            The matching :class:`BookingAggregate`, or ``None`` if no
            booking with that id has been saved.
        """
        ...

    @abstractmethod
    def save(self, booking: BookingAggregate) -> None:
        """Persist a booking, creating or overwriting it.

        Args:
            booking: The aggregate to save. Implementations should save
                by ``booking.id``, so calling this again with the same
                id updates the stored record.
        """
        ...
