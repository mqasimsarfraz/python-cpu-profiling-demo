import unittest

from app.main import (
    build_histogram,
    find_duplicates_fast,
    find_duplicates_slow,
    generate_sort_values,
    generate_values,
    sort_values,
)


class DuplicateDetectionTests(unittest.TestCase):
    def test_implementations_return_identical_results(self) -> None:
        values = generate_values(200)

        self.assertEqual(
            find_duplicates_slow(values),
            find_duplicates_fast(values),
        )

    def test_unique_values_have_no_duplicates(self) -> None:
        values = [1, 2, 3, 4]

        self.assertEqual(find_duplicates_slow(values), [])
        self.assertEqual(find_duplicates_fast(values), [])

    def test_sort_values_orders_input(self) -> None:
        values = generate_sort_values(100)

        self.assertEqual(sort_values(values), sorted(values))

    def test_histogram_accounts_for_every_value(self) -> None:
        values = generate_sort_values(100)

        self.assertEqual(sum(build_histogram(values)), len(values))


if __name__ == "__main__":
    unittest.main()
