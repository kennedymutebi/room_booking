"""Aggregate Root: Booking (Aggregate A).

BR2 (Identity/state rule): a Booking is identified by its ``id`` and moves
through the states in :class:`domain.entities.booking.BookingStatus`.
Only forward, valid transitions are allowed, and the aggregate root is the
sole object permitted to change its own status -- external code can never
set ``booking.status`` directly and bypass the rule. That guarantee is
what makes this an Aggregate Root rather than a plain Entity.
"""

from typing import List

from domain.entities.booking import Booking, BookingStatus
from domain.events.booking_created import BookingConfirmed


class InvalidBookingStateTransitionError(ValueError):
    """Raised when BR2 is violated.

    This happens when :meth:`BookingAggregate.confirm`,
    :meth:`BookingAggregate.cancel` or :meth:`BookingAggregate.reject` is
    called while the booking is not in a state that permits that
    transition (see the state diagram in
    :class:`domain.entities.booking.BookingStatus`).
    """


class BookingAggregate(Booking):
    """The Booking aggregate root.

    Wraps the plain :class:`~domain.entities.booking.Booking` entity with
    the behaviour that enforces BR2 and raises the BR5 domain event.
    Collects raised domain events internally; callers must retrieve them
    explicitly with :meth:`pull_events` (a simple, dependency-free
    alternative to an event bus, appropriate for this small, in-process
    system).
    """

    def __init__(self, *args, **kwargs) -> None:
        """Create a new booking aggregate.

        Accepts the same arguments as
        :class:`domain.entities.booking.Booking` (``id``, ``room_id``,
        ``requester``, ``attendee_count``, ``period``, and optionally
        ``status``), plus initialises an empty, private list of
        not-yet-dispatched domain events.
        """
        super().__init__(*args, **kwargs)
        self._domain_events: List[BookingConfirmed] = []

    def confirm(self) -> None:
        """Transition the booking from ``PENDING`` to ``CONFIRMED``.

        On success, records a :class:`BookingConfirmed` domain event
        (BR5) so that the Room aggregate can later be asked to reserve
        the matching slot. The event is not dispatched here; the caller
        must retrieve it via :meth:`pull_events` and hand it to a
        handler.

        Raises:
            InvalidBookingStateTransitionError: If the booking is not
                currently ``PENDING``.
        """
        if self.status != BookingStatus.PENDING:
            raise InvalidBookingStateTransitionError(
                f"Cannot confirm a booking in {self.status.value} state."
            )
        self.status = BookingStatus.CONFIRMED
        self._domain_events.append(
            BookingConfirmed(booking_id=self.id, room_id=self.room_id, period=self.period)
        )

    def cancel(self) -> None:
        """Transition the booking to ``CANCELLED``.

        Allowed from either ``PENDING`` or ``CONFIRMED`` -- a requester
        may cancel a booking they have not yet used, whether or not the
        room slot was already reserved.

        Raises:
            InvalidBookingStateTransitionError: If the booking is
                already ``CANCELLED`` or ``REJECTED``.
        """
        if self.status not in (BookingStatus.PENDING, BookingStatus.CONFIRMED):
            raise InvalidBookingStateTransitionError(
                f"Cannot cancel a booking in {self.status.value} state."
            )
        self.status = BookingStatus.CANCELLED

    def reject(self) -> None:
        """Transition the booking to ``REJECTED``.

        Called by the caller handling the BR5 follow-up action (see
        :class:`application.services.create_booking.CreateBookingService`)
        when Aggregate B (the Room) refuses to honour the
        :class:`BookingConfirmed` event -- for example because another
        booking already reserved an overlapping slot.

        Raises:
            InvalidBookingStateTransitionError: If the booking is not
                currently ``CONFIRMED``.
        """
        if self.status != BookingStatus.CONFIRMED:
            raise InvalidBookingStateTransitionError(
                "Only a confirmed booking awaiting room allocation can be rejected."
            )
        self.status = BookingStatus.REJECTED

    def pull_events(self) -> List[BookingConfirmed]:
        """Retrieve and clear all domain events raised so far.

        Returns:
            The list of :class:`BookingConfirmed` events recorded since
            the last call to this method (empty if none are pending).
            The aggregate's internal event list is reset to empty as a
            side effect, so each event is returned exactly once.
        """
        events, self._domain_events = self._domain_events, []
        return events
