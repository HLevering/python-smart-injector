from smart_injector import StaticContainer
from smart_injector import create_container


def test_container_creates_simple_type():
    container = create_container(StaticContainer)
    my_int = container.get(int)
    assert isinstance(my_int, int)
