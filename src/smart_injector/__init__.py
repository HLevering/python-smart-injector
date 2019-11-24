__version__ = "__version__ = '0.0.4'"

from smart_injector.container import StaticContainer
from smart_injector.container_factory import create_container
from smart_injector.scope import Scope

__all__ = ["create_container", "StaticContainer", "Scope"]
