import os
import time
from typing import Literal

from fastapi import FastAPI, HTTPException, Query

Implementation = Literal["slow", "optimized"]
DEFAULT_IMPLEMENTATION = os.getenv("IMPLEMENTATION", "slow")

if DEFAULT_IMPLEMENTATION not in {"slow", "optimized"}:
    raise RuntimeError("IMPLEMENTATION must be 'slow' or 'optimized'")

app = FastAPI(
    title="Python CPU Profiling Demo",
    description="A deterministic CPU workload with slow and optimized implementations.",
)


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


def find_duplicates_optimized(values: list[int]) -> list[int]:
    seen: set[int] = set()
    duplicates: set[int] = set()
    for value in values:
        if value in seen:
            duplicates.add(value)
        else:
            seen.add(value)
    return sorted(duplicates)


@app.get("/healthz")
def healthz() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/analyze")
def analyze(
    size: int = Query(default=5_000, ge=100, le=20_000),
    implementation: Implementation | None = None,
) -> dict[str, int | float | str]:
    selected = implementation or DEFAULT_IMPLEMENTATION
    values = generate_values(size)

    started = time.perf_counter()
    if selected == "slow":
        duplicates = find_duplicates_slow(values)
    elif selected == "optimized":
        duplicates = find_duplicates_optimized(values)
    else:
        raise HTTPException(status_code=400, detail="Unknown implementation")
    elapsed_ms = (time.perf_counter() - started) * 1_000

    return {
        "implementation": selected,
        "input_size": size,
        "duplicate_count": len(duplicates),
        "checksum": sum(duplicates),
        "elapsed_ms": round(elapsed_ms, 3),
    }
