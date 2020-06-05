import pytest


@pytest.fixture(scope="session", autouse=True)
def my_own_session_run_at_beginning(request):
    print("\nIn my_own_session_run_at_beginning()")

    def my_own_session_run_at_end():
        print("In my_own_session_run_at_end()")

    request.addfinalizer(my_own_session_run_at_end)
