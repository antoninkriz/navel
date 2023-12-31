"""
Module for the custom Glob Yaml Expression
"""

import os
import pathlib
import re
from typing import NoReturn

import yaml

from navel.caching.file_manager import File
from navel.errors import ExprError
from navel.yaml_expr.yaml_expr import YamlExpr, yaml_add


@yaml_add
class GlobExpr(YamlExpr):
    """
    Construct and parse glob expressions in YAML

    YAML:
    ~+/some/dir/*
    Output:
    pathlib.Path('some/dir/*')
    """

    PATTERN = re.compile(r"~\+[/\\].+")

    def __init__(self, loader: yaml.Loader, node: yaml.ScalarNode):
        super().__init__(loader, node)
        val = loader.construct_scalar(node)
        if not isinstance(val, str):
            raise ExprError("Invalid glob")

        self._glob = pathlib.Path(os.path.dirname(loader.name), val[len("~+/") :])

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {self._glob}>"

    def match_line_numbers(self, file: File) -> NoReturn:
        raise NotImplementedError

    def matches(self, file: File) -> NoReturn:
        raise NotImplementedError

    @property
    def glob(self) -> pathlib.Path:
        """
        Get the glob as a path
        @return: Glob as a path
        """
        return self._glob
