"""
Module for the abstract class for the custom Yaml Expression
"""

import abc
from typing import List, Optional, Pattern, Type, TypeVar

import yaml

from navel.caching.file_manager import File


class YamlExpr(abc.ABC):
    """
    Abstract class for custom Yaml Expressions

    Attributes:
        - TAG: tag of the expression to be used in YAML files, by default it's `!<lowercase class name>`
        - PATTERN: RegEx pattern to match in YAML files to detect this expression, disabled by default
    """

    TAG: Optional[str] = None
    PATTERN: Optional[Pattern[str]] = None

    def __init__(self, loader: yaml.Loader, node: yaml.Node):
        self._loader = loader
        self._node = node

    @abc.abstractmethod
    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}>"

    @classmethod
    def add_to_yaml(cls) -> None:
        """
        Add this class to PyYAML loaders
        """
        tag = cls.TAG if cls.TAG is not None else f"!{cls.__name__.lower()[:-4]}"
        yaml.add_constructor(tag, cls)
        if cls.PATTERN is not None:
            yaml.add_implicit_resolver(tag, cls.PATTERN)

    @abc.abstractmethod
    def match_line_numbers(self, file: File) -> List[int]:
        """
        Matched line numbers by an expression
        @raise NotImplementedError
        @param file: File object to match the lines in
        @return: List of matched line numbers
        """
        raise NotImplementedError

    @abc.abstractmethod
    def matches(self, file: File) -> bool:
        """
        Check if a file object matches the expression
        @raise NotImplementedError
        @param file: File object to check the match for
        @return: True on match, False otherwise
        """
        raise NotImplementedError


T = TypeVar("T", bound=Type[YamlExpr])


def yaml_add(cls: T) -> T:
    """
    Class decorator to add the class to the YAML parsers
    @param cls: Class to be added
    @return: The same class
    """
    cls.add_to_yaml()
    return cls
