"""Shared test setup: keep every test offline and independent of the machine's HALIO_ENGINE."""

import os

# Tests never reach the network. The v1 agent is stubbed by the tests that need it; v2 tests pass `evidence_engine="v2"`
# explicitly and inject discover/fetch/judge, so no test depends on whatever HALIO_ENGINE the machine has.
os.environ["HALIO_ENGINE"] = "v1"
