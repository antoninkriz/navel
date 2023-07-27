import abc
import re
from typing import List, Optional, Type, TypeVar

import yaml

from navel.caching.file_manager import File


class YamlExpr(abc.ABC):
    TAG: Optional[str] = None
    PATTERN: Optional[re.Pattern[str]] = None

    def __init__(self, loader: yaml.Loader, node: yaml.Node):
        self._loader = loader
        self._node = node

    @classmethod
    def add_to_yaml(cls) -> None:
        tag = cls.TAG if cls.TAG is not None else f"!{cls.__name__.lower()[:-4]}"
        yaml.add_constructor(tag, cls)
        if cls.PATTERN is not None:
            yaml.add_implicit_resolver(tag, cls.PATTERN)

    @abc.abstractmethod
    def match_line_numbers(self, file: File) -> List[int]:
        raise NotImplementedError

    @abc.abstractmethod
    def matches(self, file: File) -> bool:
        raise NotImplementedError


T = TypeVar("T", bound=Type[YamlExpr])


def yaml_add(cls: T) -> T:
    cls.add_to_yaml()
    return cls
