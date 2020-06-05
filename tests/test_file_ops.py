import sys, os

sys.path.append(os.path.join(os.path.dirname(sys.path[0]), "src"))
from jide import jide


class TestFileProcs:
    def test_file_open(self, main_window):
        print("start of test")
        assert isinstance(main_window, jide)
