import dataclasses

import yaml

from navel.caching.file_manager import File
from navel.errors import ExprError
from navel.yaml_expr.yaml_expr import YamlExpr
from navel.models import Settings as SettingsModel


class Settings(YamlExpr):
    """
    Construct and parse glob expressions in YAML

    YAML:
    ~+/some/dir/*
    Output:
    pathlib.Path('some/dir/*')
    """

    def __init__(self, loader: yaml.Loader, node: yaml.ScalarNode):
        super().__init__(loader, node)
        values = loader.construct_mapping(node)
        try:
            self.settings = SettingsModel(**values)
        except TypeError:
            for field in dataclasses.fields(SettingsModel):
                if field.name not in values:
                    raise ExprError(f'!settings node is missing required field `{field.name}`')
            raise

    def match_line_numbers(self, file: File):
        raise NotImplementedError
