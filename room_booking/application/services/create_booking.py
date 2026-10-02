"""Application Service for the main use case: creating a room booking.

BR6 (Lookup rule): the Room must be looked up via
:class:`~application.repositories.room_repository.RoomRepository` before
anything else can proceed.

This service coordinates the full workflow end to end (lookup, validate,
allocate, persist, confirm, handle the follow-up event) but contains none
of the core business rules itself -- each rule stays inside the domain
object responsible for it. Its only job is orchestration and translating
between DTOs and domain objects.
"""

import uuid

from application.dto.create_booking_request import CreateBookingRequest
from application.dto.create_booking_response import CreateBookingResponse
from application.repositories.booking_repository import BookingRepository
from application.repositories.room_repository import RoomRepository
from domain.aggregates.booking import BookingAggregate
from domain.aggregates.room import OverlappingBookingError
from domain.services.booking_service import RoomAllocationService, RoomNotSuitableError
from domain.value_objects.booking_date import BookingPeriod, InvalidBookingPeriodError
from infrastructure.events.event_handler import BookingConfirmedHandler


class CreateBookingService:
    """Orchestrates the "create a booking" use case.

    Workflow (see :meth:`execute`):

    1. **BR6** -- look up the requested Room; reject if it does not exist.
    2. **BR1** -- construct the :class:`BookingPeriod` value object;
       rejected automatically if invalid.
    3. **BR4** -- ask :class:`RoomAllocationService` whether the room can
       take this request (capacity and existing schedule).
    4. Create and persist a new :class:`BookingAggregate` in the
       ``PENDING`` state.
    5. **BR2** -- confirm the booking, which raises the BR5
       ``BookingConfirmed`` domain event.
    6. **BR5 / BR3** -- hand the event to
       :class:`BookingConfirmedHandler`, which asks the Room aggregate to
       reserve the slot; if the Room refuses (BR3), the booking is
       rejected instead.
    """

    def __init__(
        self,
        booking_repository: BookingRepository,
        room_repository: RoomRepository,
    ) -> None:
        """Wire the service to its dependencies.

        This is the point of dependency injection required by the
        coursework: concrete repository implementations (e.g.
        in-memory, for this small demo) are constructed by the caller
        and handed in here, rather than being constructed by the service
        itself.

        Args:
            booking_repository: Where Booking aggregates are persisted.
            room_repository: Where Room aggregates are persisted; also
                used to construct the internal
                :class:`BookingConfirmedHandler`.
        """
        self._bookings = booking_repository
        self._rooms = room_repository
        self._event_handler = BookingConfirmedHandler(room_repository)

    def execute(self, request: CreateBookingRequest) -> CreateBookingResponse:
        """Run the create-booking use case for a single request.

        Args:
            request: The booking details to attempt.

        Returns:
            A :class:`CreateBookingResponse` describing the outcome.
            ``success`` is ``True`` only if the booking reached
            ``CONFIRMED`` end to end; otherwise it carries a
            ``"REJECTED"`` status and an explanatory ``message`` drawn
            from whichever business rule failed (BR6, BR1, BR4, or the
            BR5/BR3 follow-up).
        """
        # BR6: look up the room before continuing.
        room = self._rooms.get(request.room_id)
        if room is None:
            return CreateBookingResponse(
                success=False,
                booking_id=None,
                status="REJECTED",
                message=f"Room {request.room_id} does not exist.",
            )

        try:
            period = BookingPeriod(request.start_time, request.end_time)  # BR1
        except InvalidBookingPeriodError as exc:
            return CreateBookingResponse(False, None, "REJECTED", str(exc))

        try:
            RoomAllocationService.assess(room, request.attendee_count, period)  # BR4
        except RoomNotSuitableError as exc:
            return CreateBookingResponse(False, None, "REJECTED", str(exc))

        booking = BookingAggregate(
            id=str(uuid.uuid4()),
            room_id=request.room_id,
            requester=request.requester,
            attendee_count=request.attendee_count,
            period=period,
        )
        self._bookings.save(booking)

        booking.confirm()  # BR2 state transition; raises BookingConfirmed
        events = booking.pull_events()

        try:
            for event in events:
                self._event_handler.handle(event)  # BR5 flow; BR3 enforced in Room
        except OverlappingBookingError as exc:
            booking.reject()
            self._bookings.save(booking)
            return CreateBookingResponse(False, booking.id, booking.status.value, str(exc))

        self._bookings.save(booking)
        return CreateBookingResponse(True, booking.id, booking.status.value, "Booking confirmed.")
