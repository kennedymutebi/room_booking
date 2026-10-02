"""Traceability reference for BR1-BR6 (backs Slide 3 / Slide 15).

This module enforces nothing itself -- each rule is actually enforced in
the component named in :data:`RULE_TO_COMPONENT` below. It exists purely
so the rule -> component -> test mapping required for traceability is
easy to point to, and to check programmatically, from one place.

Rule reference
--------------
BR1  Value rule
    Enforced by :class:`domain.value_objects.booking_date.BookingPeriod`.
    Violation -> ``InvalidBookingPeriodError``. Tested in ``tests/test_br1.py``.

BR2  Identity/state rule
    Enforced by :class:`domain.aggregates.booking.BookingAggregate`.
    Violation -> ``InvalidBookingStateTransitionError``. Tested in
    ``tests/test_br2.py``.

BR3  Invariant rule
    Enforced by :class:`domain.aggregates.room.RoomAggregate`.
    Violation -> ``OverlappingBookingError``. Tested in ``tests/test_br3.py``.

BR4  Cross-concept rule
    Enforced by :class:`domain.services.booking_service.RoomAllocationService`.
    Violation -> ``RoomNotSuitableError``. Tested in ``tests/test_br4.py``.

BR5  Follow-up rule
    Enforced by the flow from
    :class:`domain.events.booking_created.BookingConfirmed` through
    :class:`infrastructure.events.event_handler.BookingConfirmedHandler`.
    Violation path -> ``booking.reject()``. Tested in ``tests/test_br5.py``,
    ``tests/test_main_use_case.py`` (T7) and
    ``tests/test_aggregate_b_rejection.py`` (T8).

BR6  Lookup rule
    Enforced by
    :class:`application.services.create_booking.CreateBookingService`.
    Violation -> ``CreateBookingResponse(success=False, status="REJECTED")``.
    Tested in ``tests/test_br6.py``.
"""

from typing import Dict

#: Maps each business rule id to the fully qualified name of the
#: component that enforces it, for use in traceability documentation
#: and, if desired, automated checks that the mapping stays in sync
#: with the codebase.
RULE_TO_COMPONENT: Dict[str, str] = {
    "BR1": "domain.value_objects.booking_date.BookingPeriod",
    "BR2": "domain.aggregates.booking.BookingAggregate",
    "BR3": "domain.aggregates.room.RoomAggregate",
    "BR4": "domain.services.booking_service.RoomAllocationService",
    "BR5": "domain.events.booking_created.BookingConfirmed",
    "BR6": "application.services.create_booking.CreateBookingService",
}
