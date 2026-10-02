"""Aggregate Root: Room (Aggregate B).

BR3 (Invariant rule): a Room holds a collection of reserved
:class:`~domain.value_objects.booking_date.BookingPeriod` slots (its
"child objects"), and no two slots may ever overlap. This must hold no
matter which code path adds a slot, so the check lives inside the
aggregate root's own :meth:`RoomAggregate.reserve_slot` method rather than
in calling code -- there is no other way to add a slot to a Room.
"""

from typing import List

from domain.entities.room import Room
from domain.value_objects.booking_date import BookingPeriod


class OverlappingBookingError(ValueError):
    """Raised when BR3 is violated.

    Raised by :meth:`RoomAggregate.reserve_slot` when the period being
    added overlaps a slot the room has already reserved.
    """


class RoomAggregate(Room):
    """The Room aggregate root.

    Wraps the plain :class:`domain.entities.room.Room` entity with a
    private collection of reserved time slots and the behaviour that
    enforces BR3 (no overlapping slots) and supports BR4's capacity
    check.
    """

    def __init__(self, *args, **kwargs) -> None:
        """Create a new room aggregate with an empty schedule.

        Accepts the same arguments as
        :class:`domain.entities.room.Room` (``id``, ``name``,
        ``capacity``).
        """
        super().__init__(*args, **kwargs)
        self._reserved_slots: List[BookingPeriod] = []

    @property
    def reserved_slots(self) -> List[BookingPeriod]:
        """The room's currently reserved periods.

        Returns:
            A **copy** of the internal list, so callers cannot mutate the
            aggregate's schedule except through :meth:`reserve_slot`.
        """
        return list(self._reserved_slots)

    def reserve_slot(self, period: BookingPeriod) -> None:
        """Reserve a time slot on this room, enforcing BR3.

        Args:
            period: The period to reserve.

        Raises:
            OverlappingBookingError: If ``period`` overlaps any slot
                already reserved on this room. In that case the schedule
                is left unchanged.
        """
        for existing in self._reserved_slots:
            if existing.overlaps_with(period):
                raise OverlappingBookingError(
                    f"Room {self.name} already has a booking overlapping this period."
                )
        self._reserved_slots.append(period)

    def has_capacity_for(self, attendee_count: int) -> bool:
        """Check whether this room's capacity can hold a given party size.

        Used by :class:`domain.services.booking_service.RoomAllocationService`
        as one half of BR4.

        Args:
            attendee_count: The number of people to check for.

        Returns:
            ``True`` if ``attendee_count`` does not exceed ``self.capacity``.
        """
        return attendee_count <= self.capacity
