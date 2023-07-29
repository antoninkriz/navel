"""
Module for the custom Settings Yaml Expression
"""

import dataclasses
from typing import Any, Dict, NoReturn, cast

import yaml

from navel.caching.file_manager import File
from navel.errors import ExprError
from navel.models import Settings as SettingsModel
from navel.yaml_expr.yaml_expr import YamlExpr, yaml_add


@yaml_add
class SettingsExpr(YamlExpr):
    """
    Construct and parse glob expressions in YAML

    YAML:
    ~+/some/dir/*
    Output:
    pathlib.Path('some/dir/*')
    """

    def __init__(self, loader: yaml.Loader, node: yaml.MappingNode):
        super().__init__(loader, node)
        values = cast(Dict[str, Any], loader.construct_mapping(node))
        try:
            self._settings = SettingsModel(**values)
        except TypeError as exc:
            for field in dataclasses.fields(SettingsModel):
                if field.name not in values:
                    raise ExprError(f"!settings node is missing required field `{field.name}`") from exc
            raise

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {self._settings}>"

    def match_line_numbers(self, file: File) -> NoReturn:
        raise NotImplementedError

    def matches(self, file: File) -> NoReturn:
        raise NotImplementedError

    @property
    def settings(self) -> SettingsModel:
        """
        Get the SettingsModel stored in this expression
        @return: SettingsModel class of this expression
        """
        return self._settings
