from typing import Optional, TypeVar, List

import abc
import re

import pyastgrep.search
import yaml

from navel.caching.file_manager import File

T = TypeVar('T')


class YamlExpr(abc.ABC):
    TAG: Optional[str] = None
    PATTERN: Optional[re.Pattern] = None

    def __init__(self, loader: yaml.Loader, node: yaml.Node):
        self._loader = loader
        self._node = node

    @classmethod
    def add_to_yaml(cls):
        tag = cls.TAG if cls.TAG is not None else cls.__name__.lower()
        yaml.add_constructor(tag, cls)
        if cls.PATTERN is not None:
            yaml.add_implicit_resolver(tag, cls.PATTERN)

    @abc.abstractmethod
    def match_line_numbers(self, file: File) -> List[int]:
        raise NotImplementedError
