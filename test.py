from traceback import print_exc
from dvk_manga.tests.test_mangadex import TestMangadex


def main():
    """
    Runs all tests for dvk_manga.
    """
    test_mangadex = TestMangadex()
    print("Running")
    try:
        test_mangadex.test_all()
        print("All dvk_manga tests passed.")
    except AssertionError:
        print("Test failed:")
        print_exc()


if __name__ == "__main__":
    main()
