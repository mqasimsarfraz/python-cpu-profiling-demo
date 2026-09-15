import os
import time

DEFAULT_IMPLEMENTATION = os.getenv("IMPLEMENTATION", "slow")
INPUT_SIZE = int(os.getenv("INPUT_SIZE", "5000"))
REPORT_INTERVAL_SECONDS = float(os.getenv("REPORT_INTERVAL_SECONDS", "5"))
WORK_INTERVAL_SECONDS = float(os.getenv("WORK_INTERVAL_SECONDS", "0.5"))

if DEFAULT_IMPLEMENTATION not in {"slow", "fast"}:
    raise RuntimeError("IMPLEMENTATION must be 'slow' or 'fast'")
if INPUT_SIZE < 100 or INPUT_SIZE > 20_000:
    raise RuntimeError("INPUT_SIZE must be between 100 and 20000")
if REPORT_INTERVAL_SECONDS <= 0:
    raise RuntimeError("REPORT_INTERVAL_SECONDS must be greater than zero")
if WORK_INTERVAL_SECONDS <= 0:
    raise RuntimeError("WORK_INTERVAL_SECONDS must be greater than zero")


def generate_values(size: int) -> list[int]:
    unique_values = max(size // 2, 1)
    return [(index * 37) % unique_values for index in range(size)]


def find_duplicates_slow(values: list[int]) -> list[int]:
    duplicates: set[int] = set()
    for index, value in enumerate(values):
        for candidate_index in range(index + 1, len(values)):
            if value == values[candidate_index]:
                duplicates.add(value)
                break
    return sorted(duplicates)


def find_duplicates_fast(values: list[int]) -> list[int]:
    seen: set[int] = set()
    duplicates: set[int] = set()
    for value in values:
        if value in seen:
            duplicates.add(value)
        else:
            seen.add(value)
    return sorted(duplicates)


def run_workload() -> None:
    values = generate_values(INPUT_SIZE)
    implementation = (
        find_duplicates_slow
        if DEFAULT_IMPLEMENTATION == "slow"
        else find_duplicates_fast
    )
    expected_duplicates = INPUT_SIZE // 2
    iterations = 0
    report_started = time.perf_counter()

    print(
        f"implementation={DEFAULT_IMPLEMENTATION} input_size={INPUT_SIZE}",
        flush=True,
    )

    while True:
        iteration_started = time.perf_counter()
        duplicates = implementation(values)
        if len(duplicates) != expected_duplicates:
            raise RuntimeError("Workload produced an unexpected result")
        iterations += 1
        work_elapsed = time.perf_counter() - iteration_started
        time.sleep(max(0, WORK_INTERVAL_SECONDS - work_elapsed))

        now = time.perf_counter()
        elapsed = now - report_started
        if elapsed >= REPORT_INTERVAL_SECONDS:
            print(
                f"implementation={DEFAULT_IMPLEMENTATION} "
                f"iterations_per_second={iterations / elapsed:.2f} "
                f"checksum={sum(duplicates)}",
                flush=True,
            )
            iterations = 0
            report_started = now


if __name__ == "__main__":
    run_workload()
