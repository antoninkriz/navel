from typing import List
import bisect
import re

import yaml

from navel.caching.file_manager import File
from navel.yaml_expr.yaml_expr import YamlExpr


class RegEx(YamlExpr):
    """
    Construct and parse RegEx expressions in YAML

    YAML:
    !regex .*
    Output:
    re.Pattern(/.*/m)
    """

    def __init__(self, loader: yaml.Loader, node: yaml.ScalarNode):
        super().__init__(loader, node)
        self._regex = re.compile(loader.construct_scalar(node), re.MULTILINE | re.DOTALL)

    def match_line_numbers(self, file: File) -> List[int]:
        nl = [match.start() for match in re.finditer('\n', file.content_str)]
        return [
            bisect.bisect(nl, match.start() - 1)
            for match in self._regex.finditer(file.content_str)
        ]
