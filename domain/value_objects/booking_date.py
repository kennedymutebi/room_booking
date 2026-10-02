"""Value Object enforcing BR1.

BR1 (Value rule): a booking period is only valid if its end is strictly
after its start and its duration falls within an allowed range (30 minutes
to 8 hours inclusive).

``BookingPeriod`` has no identity of its own: two periods with the same
``start_time`` and ``end_time`` are completely interchangeable and compare
equal. That is precisely what makes it a Value Object rather than an
Entity, and is why it is immutable (``frozen=True``) and validates itself
in ``__post_init__`` -- an invalid ``BookingPeriod`` can never exist.
"""

from dataclasses import dataclass
from datetime import datetime, timedelta

#: Minimum permitted booking length (inclusive).
MIN_DURATION: timedelta = timedelta(minutes=30)

#: Maximum permitted booking length (inclusive).
MAX_DURATION: timedelta = timedelta(hours=8)


class InvalidBookingPeriodError(ValueError):
    """Raised when a requested period violates BR1.

    Covers three cases: an end time that is not after the start time, a
    duration shorter than :data:`MIN_DURATION`, and a duration longer
    than :data:`MAX_DURATION`.
    """


@dataclass(frozen=True)
class BookingPeriod:
    """An immutable, self-validating time span for a single booking.

    Attributes:
        start_time: The moment the booking begins.
        end_time: The moment the booking ends. Must be strictly after
            ``start_time``.

    Raises:
        InvalidBookingPeriodError: If BR1 is violated at construction
            time (see :meth:`__post_init__`).
    """

    start_time: datetime
    end_time: datetime

    def __post_init__(self) -> None:
        """Validate BR1 immediately after the frozen dataclass is built.

        Raises:
            InvalidBookingPeriodError: If ``end_time`` is not after
                ``start_time``, or the resulting duration falls outside
                ``[MIN_DURATION, MAX_DURATION]``.
        """
        if self.end_time <= self.start_time:
            raise InvalidBookingPeriodError("End time must be after start time.")

        duration = self.end_time - self.start_time
        if duration < MIN_DURATION:
            raise InvalidBookingPeriodError(
                f"Booking must be at least {MIN_DURATION} long."
            )
        if duration > MAX_DURATION:
            raise InvalidBookingPeriodError(
                f"Booking cannot exceed {MAX_DURATION}."
            )

    def overlaps_with(self, other: "BookingPeriod") -> bool:
        """Check whether this period overlaps another.

        Two periods overlap when one starts before the other ends, in
        both directions. Periods that are merely back-to-back (one ends
        at the exact instant the other starts) are **not** considered
        overlapping -- that boundary case is intentional, since a room
        can legitimately be booked 09:00-10:00 and then 10:00-11:00.

        Args:
            other: The period to compare against.

        Returns:
            ``True`` if the two periods share any instant in time,
            ``False`` otherwise (including when they are exactly
            adjacent).
        """
        return self.start_time < other.end_time and other.start_time < self.end_time
#  sdhjsjsjsj#