import os
import tempfile

# Must run before halio.api is imported anywhere: isolated DB, no network features.
os.environ["HALIO_DB"] = os.path.join(tempfile.mkdtemp(), "test.db")
os.environ["HALIO_RATE_LIMIT"] = "1000"
for var in ("GOOGLE_FACTCHECK_API_KEY", "HALIO_LLM", "RADAR_TOKEN", "HALIO_CHANNEL_KEY"):
    os.environ.pop(var, None)
