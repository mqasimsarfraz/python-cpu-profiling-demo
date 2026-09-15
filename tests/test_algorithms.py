import unittest

from app.main import (
    find_duplicates_fast,
    find_duplicates_slow,
    generate_values,
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


if __name__ == "__main__":
    unittest.main()
