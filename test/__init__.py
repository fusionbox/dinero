import dotenv
dotenv.read_dotenv()


def runtests():
    import sys
    import pytest

    sys.exit(pytest.main([]))
