import bisect
import re
from typing import List

import yaml

from navel.caching.file_manager import File
from navel.errors import ExprError
from navel.yaml_expr.yaml_expr import YamlExpr, yaml_add


@yaml_add
class RegExExpr(YamlExpr):
    """
    Construct and parse RegEx expressions in YAML

    YAML:
    !regex .*
    Output:
    re.Pattern(/.*/m)
    """

    def __init__(self, loader: yaml.Loader, node: yaml.ScalarNode):
        super().__init__(loader, node)
        val = loader.construct_scalar(node)
        if not isinstance(val, str):
            raise ExprError("Invalid RegEx")
        try:
            self._regex = re.compile(val, re.MULTILINE | re.DOTALL)
        except re.error as exc:
            raise ExprError("Invalid RegEx") from exc

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__} {self._regex}>'

    def match_line_numbers(self, file: File) -> List[int]:
        matched_line_numbers = [match.start() for match in re.finditer("\n", file.content_str)]
        return [
            bisect.bisect(matched_line_numbers, match.start() - 1) for match in self._regex.finditer(file.content_str)
        ]

    def matches(self, file: File) -> bool:
        return bool(re.finditer("\n", file.content_str))
