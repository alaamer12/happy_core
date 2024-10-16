import pytest
# from happy.util import Du


pytest.fixture(scope="session")
def create_resources():
    ...

def test_compression():
    # from happy import compress
    # assert compress
    ...

def test_archives_compression():
    ...

def test_decompression():
    ...

class TestOptimizeImage:
    def test_pre_optimize(self):
        ...

    def test_optimize(self):
        ...

    def test_post_optimize(self):
        ...

class TestOptimizeVideo:
    ...

class TestOptimizeAudio:
    ...

