"""Room entity.

Holds the plain data that identifies and describes a room. The behaviour
that actually protects business rules (BR3, BR4) lives on
:class:`domain.aggregates.room.RoomAggregate`, which subclasses this
entity -- ``Room`` itself is intentionally inert.
"""

from dataclasses import dataclass


@dataclass
class Room:
    """A physical room that can be booked.

    A Room's identity is its ``id`` (e.g. a room code such as ``"LAB-A"``),
    not its ``name`` or ``capacity``. Two rooms could share a name, but
    never an ``id``; this is what makes ``Room`` an Entity rather than a
    Value Object.

    Attributes:
        id: Unique identifier for the room, stable for its lifetime.
        name: Human-readable display name (not used for identity or
            equality).
        capacity: Maximum number of attendees the room can hold.
    """

    id: str
    name: str
    capacity: int
