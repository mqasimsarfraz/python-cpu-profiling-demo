import os
import time

DUPLICATE_IMPLEMENTATION = os.getenv("DUPLICATE_IMPLEMENTATION", "baseline")
DUPLICATE_INPUT_SIZE = int(os.getenv("DUPLICATE_INPUT_SIZE", "5000"))
SORT_INPUT_SIZE = int(os.getenv("SORT_INPUT_SIZE", "200000"))
WORK_INTERVAL_SECONDS = float(os.getenv("WORK_INTERVAL_SECONDS", "1"))

if DUPLICATE_IMPLEMENTATION not in {"baseline", "optimized"}:
    raise RuntimeError(
        "DUPLICATE_IMPLEMENTATION must be 'baseline' or 'optimized'"
    )
if DUPLICATE_INPUT_SIZE < 100 or DUPLICATE_INPUT_SIZE > 20_000:
    raise RuntimeError("DUPLICATE_INPUT_SIZE must be between 100 and 20000")
if SORT_INPUT_SIZE < 1_000 or SORT_INPUT_SIZE > 1_000_000:
    raise RuntimeError("SORT_INPUT_SIZE must be between 1000 and 1000000")
if WORK_INTERVAL_SECONDS <= 0:
    raise RuntimeError("WORK_INTERVAL_SECONDS must be greater than zero")


def generate_values(size: int) -> list[int]:
    unique_values = max(size // 2, 1)
    return [(index * 37) % unique_values for index in range(size)]


def generate_sort_values(size: int) -> list[int]:
    return [(index * 48_271) % 2_147_483_647 for index in range(size)]


def sort_values(values: list[int]) -> list[int]:
    return sorted(values)


def find_duplicates(values: list[int]) -> list[int]:
    duplicates: set[int] = set()
    for index, value in enumerate(values):
        for candidate_index in range(index + 1, len(values)):
            if value == values[candidate_index]:
                duplicates.add(value)
                break
    return sorted(duplicates)


def find_duplicates_optimized(values: list[int]) -> list[int]:
    seen: set[int] = set()
    duplicates: set[int] = set()
    for value in values:
        if value in seen:
            duplicates.add(value)
        else:
            seen.add(value)
    return sorted(duplicates)


def build_histogram(values: list[int], bucket_count: int = 1_024) -> list[int]:
    buckets = [0] * bucket_count
    for value in values:
        buckets[value % bucket_count] += 1
    return buckets


def run_workload() -> None:
    duplicate_values = generate_values(DUPLICATE_INPUT_SIZE)
    sort_input = generate_sort_values(SORT_INPUT_SIZE)
    duplicate_function = (
        find_duplicates
        if DUPLICATE_IMPLEMENTATION == "baseline"
        else find_duplicates_optimized
    )
    expected_duplicates = DUPLICATE_INPUT_SIZE // 2

    print(
        f"duplicate_implementation={DUPLICATE_IMPLEMENTATION} "
        f"duplicate_input_size={DUPLICATE_INPUT_SIZE} "
        f"sort_input_size={SORT_INPUT_SIZE}",
        flush=True,
    )

    while True:
        iteration_started = time.perf_counter()

        started = time.perf_counter()
        sorted_values = sort_values(sort_input)
        sort_ms = (time.perf_counter() - started) * 1_000

        started = time.perf_counter()
        duplicates = duplicate_function(duplicate_values)
        duplicates_ms = (time.perf_counter() - started) * 1_000

        started = time.perf_counter()
        histogram = build_histogram(sort_input)
        histogram_ms = (time.perf_counter() - started) * 1_000

        if len(duplicates) != expected_duplicates:
            raise RuntimeError("Duplicate workload produced an unexpected result")
        if len(sorted_values) != SORT_INPUT_SIZE:
            raise RuntimeError("Sort workload produced an unexpected result")
        if sum(histogram) != SORT_INPUT_SIZE:
            raise RuntimeError("Histogram workload produced an unexpected result")

        work_elapsed = time.perf_counter() - iteration_started
        time.sleep(max(0, WORK_INTERVAL_SECONDS - work_elapsed))

        print(
            f"sort_ms={sort_ms:.2f} "
            f"duplicates_ms={duplicates_ms:.2f} "
            f"histogram_ms={histogram_ms:.2f}",
            flush=True,
        )


if __name__ == "__main__":
    run_workload()
