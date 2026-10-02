# Room Booking — DDD / TDD / Clean Architecture Coursework

## How to run the tests

```bash
cd room_booking
pip install pytest
pytest -v
```

All 8 required tests (plus extra rejection/boundary cases inside T1–T4) are
in `tests/`. Saved output from an actual run is in `tdd_evidence/`:

- `tdd_evidence/1_red_failing.txt` — T1's "too long duration" test failing
  before the upper-bound rule was implemented.
- `tdd_evidence/2_implementation_and_green.txt` — the same test passing
  once `MAX_DURATION` was enforced in `BookingPeriod`.
- `tdd_evidence/3_full_suite_final_run.txt` — the full 20-test suite passing.

## Rule → component map

See `domain/rules/business_rules.py` for the BR1–BR6 → component → test
traceability table used on Slide 15.

## Architecture

See [`ARCHITECTURE.md`](ARCHITECTURE.md) for the layer-dependency diagram
and the BR5 event-flow sequence diagram (Slide 8 and Slide 10 material).

## Code documentation

Every module, class and public method has a docstring explaining what it
does, which business rule it enforces (where relevant), its arguments,
return value and the exceptions it can raise. Start at
`domain/aggregates/booking.py` and `domain/aggregates/room.py` for the
two aggregate roots, or `application/services/create_booking.py` for the
full use-case walkthrough (Slide 13 material).

## AI usage

Claude (Anthropic) was used to help design the domain model, implement the
Clean Architecture layers, and write/run the automated tests described
above.
