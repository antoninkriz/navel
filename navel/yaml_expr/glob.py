import os

import yaml
import pathlib

from navel.caching.file_manager import File
from navel.yaml_expr.yaml_expr import YamlExpr


class Glob(YamlExpr):
    """
    Construct and parse glob expressions in YAML

    YAML:
    ~+/some/dir/*
    Output:
    pathlib.Path('some/dir/*')
    """

    def __init__(self, loader: yaml.Loader, node: yaml.ScalarNode):
        super().__init__(loader, node)
        self._glob = pathlib.Path(
            os.path.dirname(loader.name),
            loader.construct_scalar(node)[len('~+/'):]
        )

    def match_line_numbers(self, file: File):
        raise NotImplementedError
