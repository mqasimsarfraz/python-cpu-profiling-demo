import os
import time
import urllib.error
import urllib.request

TARGET_URL = os.getenv(
    "TARGET_URL", "http://cpu-profile-demo/analyze?size=5000"
)
PAUSE_SECONDS = float(os.getenv("PAUSE_SECONDS", "0.05"))


def main() -> None:
    while True:
        started = time.perf_counter()
        try:
            with urllib.request.urlopen(TARGET_URL, timeout=30) as response:
                response.read()
            elapsed_ms = (time.perf_counter() - started) * 1_000
            print(f"status=success elapsed_ms={elapsed_ms:.1f}", flush=True)
        except (urllib.error.URLError, TimeoutError) as error:
            print(f"status=error error={error}", flush=True)
            time.sleep(1)
        time.sleep(PAUSE_SECONDS)


if __name__ == "__main__":
    main()
