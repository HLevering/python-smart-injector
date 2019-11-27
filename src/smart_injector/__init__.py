__version__ = "__version__ = '0.0.4'"

from smart_injector.config.user import Config
from smart_injector.container.container import StaticContainer
from smart_injector.container.factory import create_container
from smart_injector.lifetime import Lifetime

__all__ = ["create_container", "StaticContainer", "Lifetime", "Config"]
